import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('seo',ROOT/'skills/minwoo-seo-review/scripts/check_pages.py')
seo=importlib.util.module_from_spec(spec);spec.loader.exec_module(seo)
HTML='<!doctype html><html><head><title>Example</title><meta name="description" content="Description"><link rel="canonical" href="https://example.test/"></head><body><h1>Example</h1></body></html>'
SITEMAP='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.test/</loc></url></urlset>'

class SearchReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.data={'pages':[{'url':'https://example.test/','html':'page.html','status':200,'headers':{}}],'robots':'robots.txt','sitemap':'sitemap.xml'}
        self.write('page.html',HTML);self.write('robots.txt','User-agent: *\nAllow: /\n');self.write('sitemap.xml',SITEMAP)
    def write(self,name,value):(self.root/name).write_text(value,encoding='utf-8')
    def run_check(self):
        self.write('manifest.json',json.dumps(self.data))
        before={p.name:(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in self.root.iterdir()}
        result=seo.check(self.root/'manifest.json')
        self.assertEqual(before,{p.name:(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in self.root.iterdir()})
        return result
    def test_healthy_snapshot_and_optional_canonical(self):
        self.assertEqual(self.run_check()['status'],'no-issues-detected')
        self.write('page.html',HTML.replace('<link rel="canonical" href="https://example.test/">',''))
        self.assertEqual(self.run_check()['status'],'no-issues-detected')
    def test_meta_and_header_noindex(self):
        self.write('page.html',HTML.replace('</head>','<meta name="robots" content="noindex"></head>'))
        self.assertIn('unexpected-noindex',[x['code'] for x in self.run_check()['findings']])
        self.write('page.html',HTML);self.data['pages'][0]['headers']={'X-Robots-Tag':'googlebot: noindex'}
        self.assertIn('unexpected-noindex',[x['code'] for x in self.run_check()['findings']])
    def test_intentionally_private_page(self):
        self.data['pages'][0]['expectIndexable']=False;self.data['pages'][0]['headers']={'x-robots-tag':'noindex'}
        self.write('sitemap.xml','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        self.assertEqual(self.run_check()['status'],'no-issues-detected')
    def test_metadata_http_and_jsonld_errors(self):
        self.data['pages'][0]['status']=404
        self.write('page.html',HTML.replace('<title>Example</title>','').replace('</head>','<script type="application/ld+json">{bad}</script></head>'))
        codes={x['code'] for x in self.run_check()['findings']}
        self.assertTrue({'http-error','title-missing-or-multiple','invalid-jsonld'}<=codes)
    def test_complex_robots_is_review_not_false_pass(self):
        self.write('robots.txt','User-agent: *\nDisallow: /private*\nAllow: /private/public\n')
        self.assertEqual(self.run_check()['status'],'review')
        self.write('robots.txt','User-agent: *\nDisallow: /\n')
        self.assertIn('robots-disallow-all',[x['code'] for x in self.run_check()['findings']])
    def test_unknown_http_and_cross_origin_canonical_are_review(self):
        self.data['pages'][0].pop('status');self.data['pages'][0].pop('headers')
        self.write('page.html',HTML.replace('href="https://example.test/"','href="https://elsewhere.test/"'))
        result=self.run_check();self.assertEqual(result['status'],'review')
        self.assertEqual(result['counts']['error'],0)
    def test_bad_input_is_not_success(self):
        self.data['pages'][0]['html']='../outside.html'
        with self.assertRaises(ValueError):self.run_check()
        self.data['pages'][0]['html']='page.html';self.data['pages'][0]['expectIndexable']='true'
        with self.assertRaises(ValueError):self.run_check()
    def test_xml_entity_rejected(self):
        self.write('sitemap.xml','<!DOCTYPE a [<!ENTITY x "boom">]><a>&x;</a>')
        with self.assertRaises(ValueError):self.run_check()
if __name__=='__main__':unittest.main()
