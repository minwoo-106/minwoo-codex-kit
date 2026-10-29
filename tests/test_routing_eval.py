import importlib.util
from pathlib import Path
import sys
import unittest

EVALS=Path(__file__).resolve().parents[1]/'evals'
sys.path.insert(0,str(EVALS))
spec=importlib.util.spec_from_file_location('routing_eval',EVALS/'run_routing.py')
routing=importlib.util.module_from_spec(spec);spec.loader.exec_module(routing)

class RoutingEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.docs={'routing.md':'Index unique\nPick one domain.',
            'routing/web-ui.md':'Web unique\nPreserve the design.',
            'routing/media.md':'Media unique\nCompare matching cuts.',
            'design-skill':'---\nname: design-skill\n---\nActual design workflow.'}
        self.case={'routes':['routing.md','routing/web-ui.md'],'expected':['design-skill'],'allowed':['design-skill']}

    def events(self,names,code=0):
        return [{'type':'item.completed','item':{'type':'command_execution','exit_code':code,
            'aggregated_output':'\n'.join(self.docs[n] for n in names)}},{'type':'turn.completed'}]

    def test_required_documents_with_successful_read(self):
        self.assertTrue(routing.grade(self.events(['routing.md','routing/web-ui.md','design-skill']),self.docs,self.case)['passed'])

    def test_claim_or_failed_command_cannot_replace_read(self):
        final=[{'type':'item.completed','item':{'type':'agent_message','text':'\n'.join(self.docs.values())}},{'type':'turn.completed'}]
        self.assertFalse(routing.grade(final,self.docs,self.case)['passed'])
        self.assertFalse(routing.grade(self.events(self.docs,code=1),self.docs,self.case)['passed'])

    def test_unrelated_domain_is_not_progressive_loading(self):
        result=routing.grade(self.events(self.docs),self.docs,self.case)
        self.assertFalse(result['passed']);self.assertEqual(result['unexpected'],['routing/media.md'])

    def test_simple_answer_needs_no_skill_and_mutation_fails(self):
        case={'routes':[],'expected':[],'allowed':[]}
        self.assertTrue(routing.grade([{'type':'turn.completed'}],self.docs,case)['passed'])
        events=self.events(['routing.md','routing/web-ui.md','design-skill'])
        events.append({'type':'item.completed','item':{'type':'file_change'}})
        self.assertFalse(routing.grade(events,self.docs,self.case)['passed'])

if __name__=='__main__':unittest.main()
