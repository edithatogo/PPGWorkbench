"""Read-only external catalogue reconciliation; no applicability or native writes."""
from __future__ import annotations
import hashlib
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


DEFAULT_REFERENCE_HOSTS = frozenset({'www.safetyandquality.gov.au', 'safetyandquality.gov.au'})


def reference_scope(catalogue, sources, publications, *, read_bytes,
                    publisher_hosts=None, include_nsqhs_names=True):
    """Inspect retained, hash-bound text for literal NSQHS references and URLs.

    This is an explicit retrieval scope, not extraction of every bibliographic
    reference, current-policy verification or substantive dependency assessment.
    """
    if publisher_hosts is not None and not isinstance(publisher_hosts, (list, tuple, set, frozenset)):
        raise ValueError('Explicit publisher host collection required')
    hosts = DEFAULT_REFERENCE_HOSTS if publisher_hosts is None else frozenset(publisher_hosts)
    if (not hosts or type(include_nsqhs_names) is not bool or any(
            not isinstance(host, str) or len(host) > 253 or not re.fullmatch(
                r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', host) for host in hosts)):
        raise ValueError('Exact publisher hostnames and name-selection flag required')
    ids = [r['DocumentUID'] for r in catalogue]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate local catalogue identity')
    by_uid = {uid: [] for uid in ids}
    occurrences, held, seen = [], [], set()
    urls = {}
    nsqhs = []
    for p in publications:
        if p['kind'] != 'Publication':
            continue
        if p['key'] == 'acsqhc:nsqhs':
            nsqhs.append(p['key'])
        for a in p['assertions']:
            urls.setdefault(a['sourceURL'], set()).add(p['key'])
    pattern = re.compile(r'https?://[^\s<>"\x00-\x1f]+|\b(?:NSQHS(?:\s+Standards)?|National\s+Safety\s+and\s+Quality\s+Health\s+Service\s+Standards)\b', re.I)
    for s in sources:
        uid = s['documentUID']
        if uid not in by_uid:
            raise ValueError('Retained source outside catalogue scope')
        identity = (uid, s['originalSHA256'], s['textSHA256'])
        if identity in seen:
            raise ValueError('Duplicate retained source association')
        seen.add(identity)
        reason = None
        try:
            original = read_bytes(s['originalPath'])
            text_raw = read_bytes(s['textPath'])
            text = text_raw.decode('utf-8')
            if sha(original) != s['originalSHA256'] or sha(text_raw) != s['textSHA256'] or text != s['text']:
                reason = 'original_or_text_hash_binding_differs'
            elif s['extractionError'] or len(text.strip()) < 100:
                reason = 'extraction_error_or_insufficient_text'
            elif s['identityState'] not in {'exact_register_identifier', 'qualified_edition_variant'}:
                reason = 'identity_association_unqualified'
        except (OSError, UnicodeError):
            reason = 'retained_original_or_text_unavailable'
        if reason:
            held.append({'documentUID': uid, 'originalSHA256': s['originalSHA256'], 'reason': reason})
            by_uid[uid].append('held')
            continue
        by_uid[uid].append('inspected')
        for m in pattern.finditer(text):
            literal = m.group()
            is_url = literal.lower().startswith(('https://', 'http://'))
            locator = literal if is_url else None
            if is_url and locator not in urls:
                while True:
                    prior = locator
                    locator = locator.rstrip('.,;:')
                    if locator.endswith(')') and locator.count(')') > locator.count('('):
                        locator = locator[:-1]
                    if locator == prior:
                        break
            # Literal occurrences are retrieval candidates, never fetched or edition-adopted.
            if not is_url and not include_nsqhs_names:
                continue
            if is_url:
                try:
                    target = urlsplit(locator)
                    selected = (target.scheme in {'http', 'https'} and target.hostname in hosts
                        and not target.username and not target.password and target.port in (None, 80, 443))
                except ValueError:
                    selected = False
                if not selected:
                    continue
            candidates = sorted(urls.get(locator, set()) if is_url else nsqhs)
            start, end = m.span()
            key = sha((uid+'\0'+s['originalSHA256']+'\0'+s['textSHA256']+'\0'+str(start)+'\0'+str(end)).encode())
            occurrences.append({'key': 'reference:'+key, 'documentUID': uid,
                'sourceVersion': s['sourceVersion'], 'originalSHA256': s['originalSHA256'],
                'textSHA256': s['textSHA256'], 'start': start, 'end': end,
                'page': text.count('\f', 0, start)+1, 'line': text.count('\n', 0, start)+1,
                'literal': literal, 'context': text[max(0,start-120):min(len(text),end+200)],
                'method': 'literal-official-URL' if is_url else 'literal-NSQHS-name',
                'candidatePublicationKeys': candidates,
                'resolution': 'publication-only' if len(candidates)==1 else 'ambiguous' if candidates else 'unresolved',
                'editionKey': None, 'editionResolution': 'not-established-by-literal-match',
                'versionConflict': s['versionConflict'], 'clinicalApplicabilityAccepted': False})
    states = []
    for uid, values in by_uid.items():
        state = 'no-retained-source' if not values else 'all-retained-texts-inspected' if set(values)=={'inspected'} else 'some-retained-text-held'
        states.append({'documentUID': uid, 'state': state, 'inspectedSources': values.count('inspected'), 'heldSources': values.count('held')})
    return {'kind': 'ppg-local-external-reference-scope-v1', 'scope': ('Retained NSQHS names and Commission URLs; not every external citation'
            if hosts == DEFAULT_REFERENCE_HOSTS and include_nsqhs_names else
            'Retained literal URLs for selected publishers; not every external citation'),
        'publisherHosts': sorted(hosts), 'includeNSQHSNames': include_nsqhs_names,
        'catalogueIdentities':len(ids), 'retainedAssociations':len(sources),
        'sourceStates':dict(Counter(x['state'] for x in states)), 'identityLedger':states,
        'heldSources':held, 'occurrenceCount':len(occurrences), 'occurrences':occurrences,
        'resolutionCounts':dict(Counter(x['resolution'] for x in occurrences)),
        'nativeWrites':0, 'completeExternalReferenceCoverage':False, 'clinicalApplicabilityAccepted':False}


def representation_scope(bundle, root):
    """Enumerate literal PDF links in every selected publication HTML capture.

    Links remain candidates until identity/edition relevance is checked. Their
    absence among captures is a gap, not an exclusion or withdrawal decision.
    """
    records = bundle['records']; captures = [r for r in records if r['kind']=='Capture']
    inventory, gaps, malformed = [], [], []
    for p in records:
        if p['kind']!='Publication' or not p['requiredCapture']:
            continue
        pages = [c for c in captures if c['publicationKey']==p['key'] and c['data']['mimeType']=='text/html']
        if not pages:
            gaps.append({'publicationKey':p['key'], 'reason':'selected_publication_has_no_retained_HTML'})
        for page in pages:
            d=page['data']; path=Path(root)/d['file']
            if Path(d['file']).name != d['file'] or path.is_symlink():
                raise ValueError('Unsafe retained source path')
            raw=path.read_bytes()
            if sha(raw)!=d['sha256'] or len(raw)!=d['bytes']:
                raise ValueError('Retained representation bytes differ')
            main=BeautifulSoup(raw,'html.parser').find('main')
            if main is None:
                raise ValueError('Publication main content absent')
            for ordinal,link in enumerate(main.find_all('a',href=True)):
                try:
                    target=urljoin(d['sourceURL'],link['href']); u=urlsplit(target)
                    port=u.port
                except ValueError:
                    malformed.append({'publicationKey':p['key'],'sourceCaptureKey':page['key'],
                        'ordinal':ordinal,'rawHref':link['href'],'reason':'malformed_link_authority'})
                    continue
                if not u.path.lower().endswith('.pdf'):
                    continue
                same_origin=u.scheme=='https' and u.hostname=='www.safetyandquality.gov.au' and not u.username and not u.password and port in (None,443)
                matches=[c for c in captures if c['publicationKey']==p['key'] and c['data']['sourceURL']==target]
                inventory.append({'publicationKey':p['key'],'sourceCaptureKey':page['key'],
                    'sourceSHA256':d['sha256'],'ordinal':ordinal,'rawHref':link['href'],
                    'sourceURL':d['sourceURL'],'url':target,'label':link.get_text(' ',strip=True),
                    'samePublisherOrigin':same_origin,'captureKeys':[c['key'] for c in matches],
                    'exactEditionKeys':sorted({c['editionKey'] for c in matches if c['editionKey']}),
                    'disposition':'retained-candidate' if matches else 'not-retained-candidate',
                    'requiredRepresentationAccepted':False})
    return {'kind':'ppg-required-representation-candidates-v1','candidates':inventory,
        'candidateOccurrences':len(inventory),'uniquePublicationURLs':len({(x['publicationKey'],x['url']) for x in inventory}),
        'notRetainedOccurrences':sum(not x['captureKeys'] for x in inventory),'pageGaps':gaps,
        'malformedLinks':malformed,
        'requiredRepresentationDenominatorDeclared':False,'nativeWrites':0,'milestoneAccepted':False}


def main(argv=None):
    """Create new private audit outputs; never write catalogue/native state."""
    import argparse
    import json
    import os
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--local-inputs',type=Path,required=True)
    parser.add_argument('--capture-root',type=Path,required=True)
    parser.add_argument('--source-root',type=Path,default=Path.cwd())
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--publisher-host', action='append', metavar='HOST',
                        help='Explicit qualified URL host; repeat for a bounded source family')
    parser.add_argument('--no-nsqhs-names', action='store_true')
    args=parser.parse_args(argv)
    if args.output_dir.exists():
        raise ValueError('New private output directory required')
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:raise ValueError('Duplicate JSON member')
            result[k]=v
        return result
    def load(path):
        raw=path.read_bytes()
        if len(raw)>128*1024*1024:raise ValueError('Input exceeds bound')
        return raw,json.loads(raw,object_pairs_hook=unique)
    bundle_raw,bundle=load(args.bundle);local_raw,local=load(args.local_inputs)
    root=args.source_root.resolve()
    def read(path):
        p=Path(path).resolve()
        if root not in p.parents or not p.is_file() or p.stat().st_size>128*1024*1024:
            raise OSError('Retained source outside approved root or bound')
        return p.read_bytes()
    refs=reference_scope(local['catalogue'],local['sources'],bundle['records'],read_bytes=read,
        publisher_hosts=args.publisher_host,include_nsqhs_names=not args.no_nsqhs_names)
    reps=representation_scope(bundle,args.capture_root)
    outputs={'references.json':refs,'representations.json':reps}
    args.output_dir.mkdir(mode=0o700)
    hashes={}
    for name,value in outputs.items():
        raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        fd=os.open(args.output_dir/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw)
        hashes[name]=sha(raw)
    manifest={'bundleSHA256':sha(bundle_raw),'localInputsSHA256':sha(local_raw),
        'outputs':hashes,'nativeWrites':0,'completeExternalReferenceCoverage':False}
    fd=os.open(args.output_dir/'manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(manifest,f,indent=2)
    print(json.dumps({'referenceOccurrences':refs['occurrenceCount'],'catalogueIdentities':refs['catalogueIdentities'],
        'representationCandidates':reps['candidateOccurrences'],'nativeWrites':0}))


if __name__=='__main__':main()
