"""Prepare missing relationship progress rows; never replace existing reviews.

Inputs and output contain installation data and must remain private. This command
does not authenticate, write to SharePoint or make substantive review decisions.
"""
import argparse
import hashlib
import json
from pathlib import Path


def unique(rows, field):
    result = {}
    for row in rows:
        key = row.get(field)
        if not isinstance(key, str) or not key.strip() or key in result:
            raise ValueError('Missing or duplicate ' + field)
        result[key] = row
    return result


def prepare(catalogue, assessments, relationships):
    sources = unique(catalogue, 'DocumentUID')
    existing = unique(assessments, 'DocumentUID')
    unique(assessments, 'AssessmentKey')
    unique(relationships, 'RelationshipKey')
    creates = []
    conflicts = []
    for uid, row in sources.items():
        identifier = row.get('sourceDocumentId')
        title = row.get('Title') or row.get('sourceTitle')
        if not isinstance(identifier, str) or not identifier.strip() or not isinstance(title, str) or not title.strip():
            conflicts.append({'documentUID': uid, 'reason': 'Missing source identifier or title'})
            continue
        if uid in existing:
            if existing[uid].get('SourceDocumentId') != identifier:
                conflicts.append({'documentUID': uid, 'reason': 'Source identity changed; preserve existing assessment'})
            continue
        key = hashlib.sha256(json.dumps([uid, identifier], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        evidence = {'schemaVersion': 1, 'currentAuthorityVerified': False,
                    'sources': [], 'catalogueItemId': row.get('Id'),
                    'limitations': ['New catalogue identity; substantive relationship review pending.',
                                    'A body binding does not establish current approval or full source qualification.']}
        creates.append({'Title': title[:255], 'AssessmentKey': 'cr-assessment:' + key,
                        'DocumentUID': uid, 'SourceDocumentId': identifier,
                        'AssessmentState': 'Needs relationship review',
                        'SourceMembership': 'Active source snapshot', 'SourceCount': 0,
                        'ExistingOutgoingCount': sum(r.get('FromDocumentUID') == uid for r in relationships),
                        'ExistingIncomingCount': sum(r.get('ToDocumentUID') == uid for r in relationships),
                        'EvidenceManifest': json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                        'AssessmentComplete': False, 'CurrentAuthorityVerified': False})
    return {'schemaVersion': 1, 'creates': creates, 'conflicts': conflicts,
            'preservedAssessmentCount': len(existing),
            'retainedOutsideCatalogue': sorted(set(existing) - set(sources))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('catalogue', 'assessments', 'relationships', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = prepare(*(json.loads(getattr(args, name).read_text()) for name in ('catalogue', 'assessments', 'relationships')))
    with args.output.open('x', encoding='utf-8') as handle:
        args.output.chmod(0o600)
        json.dump(result, handle, ensure_ascii=False, indent=2)
    return 2 if result['conflicts'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
