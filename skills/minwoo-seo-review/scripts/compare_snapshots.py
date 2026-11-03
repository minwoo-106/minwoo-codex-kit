"""Compare two supplied SEO snapshots. No network, writes, history store or ranking inference."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from check_pages import Page, check, read_local


def snapshot(manifest):
    manifest = Path(manifest).absolute()
    # Validate the manifest itself with the same bounded local-file reader.
    data = json.loads(read_local(manifest.parent, manifest.name))
    if not isinstance(data, dict):
        raise ValueError('Manifest must be an object')
    inspection = check(manifest)
    pages = {}
    for index, entry in enumerate(data['pages']):
        page = Page()
        page.feed(read_local(manifest.parent, entry['html']))
        page.close()
        schemas = []
        for block in page.jsonld:
            raw = ''.join(block)
            try:
                schemas.append(json.dumps(json.loads(raw), sort_keys=True, ensure_ascii=False))
            except (ValueError, RecursionError):
                schemas.append('invalid-json:' + hashlib.sha256(raw.encode()).hexdigest())
        def meta(name):
            return sorted(m.get('content', '').strip() for m in page.metas
                          if m.get('name', '').lower() == name)
        headers = entry.get('headers')
        # Header names are case-insensitive. Retain duplicate observations.
        robots_header = None if headers is None else sorted(
            v.strip() for k, v in headers.items() if k.lower() == 'x-robots-tag')
        pages[entry['url']] = {
            'index': index,
            'fields': {
                'title': [' '.join(''.join(t).split()) for t in page.titles],
                'description': meta('description'),
                'canonical': sorted(page.canonicals),
                'meta_robots': meta('robots'),
                'meta_googlebot': meta('googlebot'),
                'x_robots_tag': robots_header,
                'http_status': entry.get('status'),
                'headers_observed': headers is not None,
                'jsonld': sorted(schemas),
                'expect_indexable': entry.get('expectIndexable', True),
            },
        }
    site = {}
    for name in ('robots', 'sitemap'):
        value = data.get(name)
        site[name] = None if not value else hashlib.sha256(
            read_local(manifest.parent, value).encode()).hexdigest()
    return pages, site, inspection


def compare(before, after):
    old, old_site, old_check = snapshot(before)
    new, new_site, new_check = snapshot(after)
    changes = []
    for url in sorted(old.keys() | new.keys()):
        left, right = old.get(url), new.get(url)
        if left is None or right is None:
            changes.append({'kind': 'added' if left is None else 'removed',
                            'before_page': None if left is None else left['index'],
                            'after_page': None if right is None else right['index']})
            continue
        fields = [key for key in left['fields'] if left['fields'][key] != right['fields'][key]]
        if fields:
            changes.append({'kind': 'changed', 'before_page': left['index'],
                            'after_page': right['index'], 'fields': fields})
    site_changes = [key for key in old_site if old_site[key] != new_site[key]]
    return {
        'status': 'changed' if changes or site_changes else 'unchanged',
        'changes': changes, 'site_files_changed': site_changes,
        'before_check': old_check, 'after_check': new_check,
        'scope': 'Supplied snapshots only; page numbers are zero-based. Changes are not automatically defects. '
                 'JSON-LD compares parsed values, not semantic validity. No URL/body/header values emitted.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = compare(args.before, args.after)
    except (OSError, ValueError, KeyError, TypeError, RecursionError, ET.ParseError) as exc:
        # Do not print paths or input values from exception messages.
        print(json.dumps({'status': 'incomplete', 'reason': type(exc).__name__}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['status'] == 'changed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
