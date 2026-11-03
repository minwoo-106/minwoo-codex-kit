import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/minwoo-seo-review/scripts/compare_snapshots.py'
BASE = '<html><head><title>Example</title><meta name="description" content="Description"><link rel="canonical" href="https://example.test/"></head><body>Example</body></html>'


class SnapshotCompareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for side in ('before', 'after'):
            folder = self.root / side
            folder.mkdir()
            (folder / 'page.html').write_text(BASE, encoding='utf-8')
            (folder / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
            (folder / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.test/</loc></url></urlset>', encoding='utf-8')
            self.write_manifest(side, {'pages': [{'url': 'https://example.test/', 'html': 'page.html', 'status': 200, 'headers': {}}], 'robots': 'robots.txt', 'sitemap': 'sitemap.xml'})

    def write_manifest(self, side, value):
        (self.root / side / 'manifest.json').write_text(json.dumps(value), encoding='utf-8')

    def change_manifest(self, side, change):
        p = self.root / side / 'manifest.json'
        value = json.loads(p.read_text(encoding='utf-8'))
        change(value)
        self.write_manifest(side, value)

    def run_compare(self):
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), '--before', str(self.root/'before/manifest.json'),
                               '--after', str(self.root/'after/manifest.json')], capture_output=True,
                              text=True, encoding='utf-8', timeout=15)
        return proc.returncode, json.loads(proc.stdout)

    def test_identical_and_inputs_preserved(self):
        def digest():
            return {str(p.relative_to(self.root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                    for p in self.root.rglob('*') if p.is_file()}
        before = digest()
        code, report = self.run_compare()
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'unchanged')
        self.assertEqual(report['before_check']['status'], 'no-issues-detected')
        self.assertEqual(before, digest())

    def test_json_key_order_is_not_a_change(self):
        for side, value in [('before', {'@type':'Thing','name':'Example'}), ('after', {'name':'Example','@type':'Thing'})]:
            (self.root/side/'page.html').write_text(BASE.replace('</head>', '<script type="application/ld+json">'+json.dumps(value)+'</script></head>'), encoding='utf-8')
        self.assertEqual(self.run_compare()[0], 0)

    def test_page_order_is_not_a_change(self):
        for side in ('before','after'):
            (self.root/side/'two.html').write_text(BASE.replace('Example','Second'), encoding='utf-8')
            self.change_manifest(side, lambda d: d['pages'].append({'url':'https://example.test/second','html':'two.html','status':200,'headers':{}}))
        self.change_manifest('after', lambda d: d['pages'].reverse())
        self.assertEqual(self.run_compare()[0], 0)

    def test_title_canonical_and_noindex_drift(self):
        html = BASE.replace('<title>Example', '<title>Changed').replace('href="https://example.test/"','href="https://example.test/moved"').replace('</head>','<meta name="robots" content="noindex"></head>')
        (self.root/'after/page.html').write_text(html, encoding='utf-8')
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual(set(report['changes'][0]['fields']), {'title','canonical','meta_robots'})
        self.assertIn('unexpected-noindex', {f['code'] for f in report['after_check']['findings']})

    def test_added_and_removed_pages(self):
        self.change_manifest('after', lambda d: d['pages'][0].update(url='https://example.test/new'))
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual({c['kind'] for c in report['changes']}, {'added','removed'})

    def test_unknown_headers_and_status_remain_unknown(self):
        for side in ('before','after'):
            self.change_manifest(side, lambda d: (d['pages'][0].pop('status'), d['pages'][0].pop('headers')))
        code, report = self.run_compare()
        self.assertEqual(code, 0)  # no difference, not a clean SEO report
        self.assertEqual(report['before_check']['status'], 'review')
        self.assertIn('http-status-not-observed', {f['code'] for f in report['before_check']['findings']})

    def test_header_case_and_intent_change(self):
        self.change_manifest('before', lambda d: d['pages'][0].update(headers={'X-Robots-Tag':'noindex'}, expectIndexable=False))
        self.change_manifest('after', lambda d: d['pages'][0].update(headers={'x-robots-tag':'noindex'}, expectIndexable=False))
        self.assertEqual(self.run_compare()[0], 0)
        self.change_manifest('after', lambda d: d['pages'][0].update(expectIndexable=True))
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual(report['changes'][0]['fields'], ['expect_indexable'])

    def test_existing_invalid_json_is_not_a_clean_baseline(self):
        for side in ('before','after'):
            (self.root/side/'page.html').write_text(BASE.replace('</head>', '<script type="application/ld+json">{bad}</script></head>'), encoding='utf-8')
        code, report = self.run_compare()
        self.assertEqual(code, 0)
        self.assertEqual(report['before_check']['status'], 'issues')

    def test_snapshot_text_and_urls_not_emitted(self):
        secret = 'synthetic-marker-never-publish'
        self.change_manifest('after', lambda d: d['pages'][0].update(url='https://example.test/'+secret))
        (self.root/'after/page.html').write_text(BASE.replace('Example', secret), encoding='utf-8')
        report = self.run_compare()[1]
        self.assertNotIn(secret, json.dumps(report))
        self.assertNotIn('https://example.test/', json.dumps(report))

    def test_path_escape_is_rejected(self):
        self.change_manifest('after', lambda d: d['pages'][0].update(html='../before/page.html'))
        code, report = self.run_compare()
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'incomplete')
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_bad_manifest_is_incomplete(self):
        (self.root/'after/manifest.json').write_text('{bad}', encoding='utf-8')
        self.assertEqual(self.run_compare()[0], 2)

    def test_non_object_manifest_is_incomplete(self):
        for value in ([], None, 'invalid', 123):
            with self.subTest(value=value):
                self.write_manifest('after', value)
                code, report = self.run_compare()
                self.assertEqual(code, 2)
                self.assertEqual(report['status'], 'incomplete')

    def test_googlebot_directive_change(self):
        (self.root/'after/page.html').write_text(BASE.replace('</head>', '<meta name="googlebot" content="noindex"></head>'), encoding='utf-8')
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual(report['changes'][0]['fields'], ['meta_googlebot'])
        self.assertIn('unexpected-noindex', {f['code'] for f in report['after_check']['findings']})

    def test_oversized_manifest_is_rejected(self):
        (self.root/'after/manifest.json').write_text(' '*(2*1024*1024+1), encoding='utf-8')
        self.assertEqual(self.run_compare()[0], 2)

    def test_site_file_change_is_separate(self):
        (self.root/'after/robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual(report['site_files_changed'], ['robots'])
        self.assertEqual(report['changes'], [])

    def test_http_status_and_json_value_change(self):
        self.change_manifest('after', lambda d: d['pages'][0].update(status=404))
        (self.root/'after/page.html').write_text(BASE.replace('</head>', '<script type="application/ld+json">{"@type":"Thing","name":"new"}</script></head>'), encoding='utf-8')
        code, report = self.run_compare()
        self.assertEqual(code, 1)
        self.assertEqual(set(report['changes'][0]['fields']), {'http_status','jsonld'})


if __name__ == '__main__':
    unittest.main()
