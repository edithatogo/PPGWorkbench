import hashlib
import unittest
try:
    from scripts.ppg_external_reconciliation import pdf_uri_inspection, reference_scope, representation_scope
except ModuleNotFoundError as error:
    if error.name != 'bs4':
        raise
    raise unittest.SkipTest('Optional catalogue HTML profile missing; use the qualified hash-locked Python 3.15.1 profile') from error


class ReferenceScopeTests(unittest.TestCase):
    def setup_case(self):
        text='NSQHS Standards second edition unknown. '+('Fictional retained text. '*8)
        original=b'fictional original'; raw=text.encode()
        s=dict(documentUID='fictional',originalSHA256=hashlib.sha256(original).hexdigest(),textSHA256=hashlib.sha256(raw).hexdigest(),text=text,originalPath='original',textPath='text',extractionError=None,identityState='exact_register_identifier',sourceVersion='retained',versionConflict=True)
        p=dict(kind='Publication',key='acsqhc:nsqhs',assertions=[])
        return s,p,{'original':original,'text':raw}

    def test_literal_match_preserves_conflict_and_does_not_choose_latest_edition(self):
        s,p,files=self.setup_case();r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],1);o=r['occurrences'][0]
        self.assertEqual(o['literal'],'NSQHS Standards');self.assertEqual(o['resolution'],'publication-only')
        self.assertIsNone(o['editionKey']);self.assertTrue(o['versionConflict'])
        self.assertFalse(r['completeExternalReferenceCoverage']);self.assertEqual(r['nativeWrites'],0)
        self.assertEqual(r,reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__))

    def test_hash_mismatch_is_held_and_unsearched_identity_accounted(self):
        s,p,files=self.setup_case();files['text']+=b'edited'
        r=reference_scope([{'DocumentUID':'fictional'},{'DocumentUID':'missing'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],0);self.assertEqual(len(r['heldSources']),1)
        self.assertEqual(r['sourceStates'],{'some-retained-text-held':1,'no-retained-source':1})

    def test_duplicate_identity_or_source_refuses(self):
        s,p,files=self.setup_case()
        for cat,sources in [([{'DocumentUID':'fictional'}]*2,[s]),([{'DocumentUID':'fictional'}],[s,s])]:
            with self.assertRaises(ValueError):reference_scope(cat,sources,[p],read_bytes=files.__getitem__)

    def test_same_url_ambiguous_publications_stay_ambiguous(self):
        s,p,files=self.setup_case();url='https://www.safetyandquality.gov.au/resources/fictional'
        s['text']=url+' '+('fictional '*20);files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key=k,assertions=[{'sourceURL':url}]) for k in ['first','second']]
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,read_bytes=files.__getitem__)
        self.assertEqual(r['resolutionCounts'],{'ambiguous':1});self.assertEqual(r['occurrences'][0]['candidatePublicationKeys'],['first','second'])

    def test_selected_publisher_urls_exclude_names_and_other_origins(self):
        s,p,files=self.setup_case()
        url='https://publisher.example.org/fictional/guideline.pdf'
        s['text']='NSQHS Standards '+url+' '+url+' https://intranet.example.org/local.pdf https://publisher.example.org.evil.test/x https://publisher.example.org:invalid/x https://user@publisher.example.org/x '+('fictional '*20)
        files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key='qh:fictional',assertions=[{'sourceURL':url}])]
        options=dict(read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,**options)
        self.assertEqual(r['occurrenceCount'],2)
        self.assertEqual(len({x['key'] for x in r['occurrences']}),2)
        self.assertEqual(r['resolutionCounts'],{'publication-only':2})
        self.assertTrue(all(x['editionKey'] is None and x['versionConflict'] for x in r['occurrences']))
        self.assertFalse(r['completeExternalReferenceCoverage'])
        files['text']+=b'changed'
        self.assertEqual(reference_scope([{'DocumentUID':'fictional'}],[s],pubs,**options)['occurrenceCount'],0)

    def test_balanced_url_parentheses_and_citation_punctuation(self):
        s,p,files=self.setup_case();url='https://publisher.example.org/guideline(2026)'
        s['text']=url+' '+url+'). '+('fictional '*20)
        files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key='pub',assertions=[{'sourceURL':url}])]
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        self.assertEqual(r['resolutionCounts'],{'publication-only':2})
        self.assertTrue(all(x['candidatePublicationKeys']==['pub'] for x in r['occurrences']))

    def test_unqualified_reference_host_and_flag_refused(self):
        s,p,files=self.setup_case()
        for hosts,flag in [([],False),(['evil.test/path'],False),(['publisher.example.org'],1)]:
            with self.assertRaises(ValueError):
                reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__,publisher_hosts=hosts,include_nsqhs_names=flag)

    def test_representation_page_absence_never_becomes_complete(self):
        r=representation_scope({'records':[dict(kind='Publication',key='fictional',requiredCapture=True)]},'.')
        self.assertEqual(len(r['pageGaps']),1);self.assertFalse(r['requiredRepresentationDenominatorDeclared'])


    def test_representation_links_preserve_occurrences_and_missing_captures(self):
        import tempfile
        from pathlib import Path
        raw=b'<main><h1>Fictional</h1><a href="/one.pdf">One</a><a href="/one.pdf">Again</a></main>'
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'page.html').write_bytes(raw)
            pub=dict(kind='Publication',key='pub',requiredCapture=True)
            page=dict(kind='Capture',key='page',publicationKey='pub',editionKey=None,data=dict(mimeType='text/html',file='page.html',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceURL='https://www.safetyandquality.gov.au/resources/fictional'))
            r=representation_scope({'records':[pub,page]},temp)
            self.assertEqual(r['candidateOccurrences'],2);self.assertEqual(r['uniquePublicationURLs'],1)
            self.assertEqual(r['notRetainedOccurrences'],2)
            Path(temp,'page.html').write_bytes(raw+b'edit')
            with self.assertRaises(ValueError):representation_scope({'records':[pub,page]},temp)

    def test_malformed_representation_link_does_not_discard_valid_candidates(self):
        import tempfile
        from pathlib import Path
        raw=b'<main><a href="https://www.safetyandquality.gov.au:invalid/bad.pdf">Bad port</a><a href="https://[broken/file.pdf">Bad bracket</a><a href="/valid.pdf">Valid</a></main>'
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'page.html').write_bytes(raw)
            pub=dict(kind='Publication',key='pub',requiredCapture=True)
            page=dict(kind='Capture',key='page',publicationKey='pub',editionKey=None,data=dict(mimeType='text/html',file='page.html',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceURL='https://www.safetyandquality.gov.au/resources/fictional'))
            r=representation_scope({'records':[pub,page]},temp)
            self.assertEqual(r['candidateOccurrences'],1)
            self.assertEqual(len(r['malformedLinks']),2)
            self.assertTrue(all(x['reason']=='malformed_link_authority' for x in r['malformedLinks']))
            self.assertFalse(r['requiredRepresentationDenominatorDeclared'])

    def test_pdf_uri_inspection_preserves_pages_duplicates_and_encoded_targets(self):
        dump='Page  Type          URL\n   2  Annotation    https://publisher.example.org/one.pdf\n   2  Annotation    https://publisher.example.org/one.pdf\n   4  Annotation    https://www.google.com/url?url=https%3A%2F%2Fpublisher.example.org%2Ftwo.pdf\n'
        q=pdf_uri_inspection(dump,'1'*64,decode_url_wrappers=True)
        self.assertEqual(len(q['entries']),3)
        self.assertEqual(q['entries'][2]['decodedTarget'],'https://publisher.example.org/two.pdf')
        self.assertEqual(q['text'].split('\f')[1].count('https://publisher.example.org/one.pdf'),2)
        self.assertIn('Encoded URL target',q['text'].split('\f')[3])
        self.assertEqual(q['retrievals'],0);self.assertFalse(q['fullTextReview'])
        self.assertFalse(pdf_uri_inspection(dump,'1'*64)['entries'][2]['decodedTarget'])
        self.assertEqual(q['annotationOutputSHA256'],hashlib.sha256(dump.encode()).hexdigest())

    def test_pdf_uri_inspection_refuses_bad_dump_and_records_bad_uris(self):
        for dump in ['wrong header','Page Type URL\n0 Annotation https://publisher.example.org/x','Page Type URL\n1 Unknown https://publisher.example.org/x']:
            with self.assertRaises(ValueError):pdf_uri_inspection(dump,'1'*64)
        q=pdf_uri_inspection('Page Type URL\n1 Annotation mailto:fictional@example.org\n1 Annotation https://publisher.example.org:invalid/x\n1 Annotation https://publisher.example.org/space here','1'*64)
        self.assertEqual(len(q['ignoredURIs']),3);self.assertEqual(q['entries'],[])
        with self.assertRaises(ValueError):pdf_uri_inspection('Page Type URL','bad')

    def test_pdf_annotation_reference_scope_retains_representation_provenance(self):
        s,p,files=self.setup_case();dump='Page Type URL\n3 Annotation https://publisher.example.org/guideline.pdf'
        q=pdf_uri_inspection(dump,s['originalSHA256'])
        s.update(text=q['text'],textSHA256=q['textSHA256'],inspectionKind=q['inspectionKind'],annotationOutputSHA256=q['annotationOutputSHA256'])
        files['text']=q['text'].encode()
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[],read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        self.assertEqual(r['occurrenceCount'],1);o=r['occurrences'][0]
        self.assertEqual(o['page'],3);self.assertEqual(o['inspectionKind'],'pdf-uri-annotations')
        self.assertEqual(o['annotationOutputSHA256'],q['annotationOutputSHA256'])
        self.assertEqual(o['method'],'literal-PDF-URI-annotation');self.assertEqual(o['resolution'],'unresolved')

    def test_cli_manifest_is_create_only_and_binds_inputs(self):
        import tempfile,json,contextlib,io
        from pathlib import Path
        from scripts.ppg_external_reconciliation import main
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);s,p,files=self.setup_case()
            for name,raw in files.items():Path(root,name).write_bytes(raw)
            s['originalPath']=str(root/'original');s['textPath']=str(root/'text')
            (root/'bundle.json').write_text(json.dumps({'records':[dict(p,requiredCapture=False)]}))
            (root/'local.json').write_text(json.dumps({'catalogue':[{'DocumentUID':'fictional'}],'sources':[s]}))
            args=['--bundle',str(root/'bundle.json'),'--local-inputs',str(root/'local.json'),'--capture-root',temp,'--source-root',temp,'--output-dir',str(root/'out'),'--publisher-host','publisher.example.org','--no-nsqhs-names']
            with contextlib.redirect_stdout(io.StringIO()):main(args)
            manifest=json.loads((root/'out/manifest.json').read_text())
            self.assertEqual(manifest['nativeWrites'],0)
            selected=json.loads((root/'out/references.json').read_text())
            self.assertEqual(selected['publisherHosts'],['publisher.example.org'])
            self.assertFalse(selected['includeNSQHSNames'])
            self.assertEqual(selected['occurrenceCount'],0)
            self.assertEqual(manifest['outputs']['references.json'],hashlib.sha256((root/'out/references.json').read_bytes()).hexdigest())
            self.assertEqual((root/'out/references.json').stat().st_mode&0o777,0o600)
            with self.assertRaises(ValueError):main(args)


if __name__=='__main__':unittest.main()
