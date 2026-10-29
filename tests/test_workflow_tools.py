import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
api=module('contract','skills/minwoo-api-compat/scripts/check_contract.py')
video=module('delivery','skills/minwoo-video-review/scripts/check_delivery.py')
inventory=module('inventory','skills/minwoo-kit-maintenance/scripts/skill_inventory.py')


def contract(schema):
    body={'content':{'application/json':{'schema':copy.deepcopy(schema)}}}
    operation={'requestBody':copy.deepcopy(body),'responses':{'200':copy.deepcopy(body)}}
    return {'openapi':'3.1.1','paths':{'/items':{'post':operation}}}


class ContractTests(unittest.TestCase):
    def test_enum_variance_and_required_guarantees(self):
        before=contract({'type':'object','properties':{'name':{'type':'string','enum':['a','b']}},'required':['name']})
        after=copy.deepcopy(before)
        op=after['paths']['/items']['post']
        op['requestBody']['content']['application/json']['schema']['properties']['name']['enum']=['a']
        op['responses']['200']['content']['application/json']['schema']['required']=[]
        result=api.compare(before,after)
        self.assertEqual(result['counts']['breaking'],2)
        self.assertEqual(api.compare(before,before)['status'],'no-breaking-detected')

    def test_response_enum_expansion_breaks_request_expansion_does_not(self):
        before=contract({'type':'string','enum':['a']});after=copy.deepcopy(before)
        op=after['paths']['/items']['post']
        op['requestBody']['content']['application/json']['schema']['enum']=['a','b']
        self.assertEqual(api.compare(before,after)['status'],'no-breaking-detected')
        op['responses']['200']['content']['application/json']['schema']['enum']=['a','b']
        self.assertEqual(api.compare(before,after)['status'],'breaking')

    def test_unknown_constraints_and_refs_require_review(self):
        before=contract({'$ref':'#/components/schemas/Item'});after=copy.deepcopy(before)
        after['components']={'schemas':{'Item':{'type':'string'}}}
        self.assertEqual(api.compare(before,after)['status'],'review')
        before=contract({'type':'string','maxLength':30});after=contract({'type':'string','maxLength':10})
        self.assertEqual(api.compare(before,after)['status'],'review')

    def test_removed_path_auth_change_and_invalid_input(self):
        before=contract({'type':'string'});after=copy.deepcopy(before);after['paths']={}
        self.assertEqual(api.compare(before,after)['status'],'breaking')
        after=copy.deepcopy(before);after['security']=[{'key':[]}]
        self.assertEqual(api.compare(before,after)['status'],'review')
        with self.assertRaises(ValueError): api.compare({}, {})


class DeliveryTests(unittest.TestCase):
    meta={'streams':[{'codec_type':'video','width':64,'height':36,'avg_frame_rate':'30000/1001'}],
          'format':{'duration':'1.0'}}
    def test_audio_and_fps_fail_and_input_is_unchanged(self):
        original=copy.deepcopy(self.meta)
        result=video.assess(self.meta,{'width':64,'fps':25,'audio':True})
        self.assertEqual(result['failures'],['audio','fps'])
        self.assertEqual(original,self.meta)
        self.assertTrue(video.assess(self.meta,{'fps':29.97,'audio':False})['passed'])

    def test_subtitle_range_overlap_and_invalid_criteria(self):
        good='1\n00:00:00,100 --> 00:00:00,800\nhello'
        self.assertTrue(video.assess(self.meta,{'width':64},good)['passed'])
        self.assertFalse(video.assess(self.meta,{'width':64},good.replace('00,800','01,800'))['passed'])
        overlapping=good+'\n\n2\n00:00:00,500 --> 00:00:00,900\nworld'
        self.assertTrue(video.assess(self.meta,{'width':64},overlapping)['warnings'])
        self.assertFalse(video.assess(self.meta,{'width':64,'no_overlap':True},overlapping)['passed'])
        for spec in ({},{'audio':'yes'},{'fps':float('nan')},{'unknown':1}):
            with self.assertRaises(ValueError): video.assess(self.meta,spec)


class InventoryTests(unittest.TestCase):
    def test_counts_multiline_duplicates_explicit_and_no_writes(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('KIT_TEST_ROOT')) as temp:
            root=Path(temp)
            for name in ('a','b'):
                folder=root/name;folder.mkdir()
                (folder/'SKILL.md').write_text('---\nname: same\ndescription: >-\n  first line\n  second line\n---\nBODY',encoding='utf-8')
            policy=root/'b/agents';policy.mkdir()
            (policy/'openai.yaml').write_text('policy:\n  allow_implicit_invocation: false\n',encoding='utf-8')
            before={str(p):(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
            result=inventory.inventory([root,root],1)
            self.assertEqual(result['scanned'],2)
            self.assertEqual(result['implicit_candidates'],1)
            self.assertEqual(result['duplicates'],['same'])
            self.assertTrue(result['over_comparison_budget'])
            self.assertEqual(result['entries'][0]['description_chars'],len('first line second line'))
            self.assertEqual(before,{str(p):(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()})


if __name__=='__main__': unittest.main()
