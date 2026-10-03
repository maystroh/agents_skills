import json,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
import history

class HistoryTests(unittest.TestCase):
    def test_fingerprint_uses_platform_independent_order_and_newlines(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            names=['a.py','SKILL.md','README.md']
            for name in names:(p/name).write_bytes(b'text\r\n')
            entries=[(name,hashlib.sha256(b'text\n').hexdigest()) for name in sorted(names)]
            expected=hashlib.sha256(json.dumps(entries,separators=(',',':')).encode()).hexdigest()
            self.assertEqual(history.fingerprint(p),expected)

    def test_changed_instructions_require_new_entry(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'skill').mkdir();(root/'evals').mkdir()
            f=root/'skill/SKILL.md';f.write_text('original')
            (root/'README.md').write_text(history.BEGIN+'\n'+history.END)
            with patch.object(history,'ROOT',root),patch.object(history,'HISTORY',root/'evals/history.json'):
                records=[{'id':'v1','change':'first','status':'pending evaluation',**history.current()}]
                history.HISTORY.write_text(json.dumps(records));history.update();history.update(check=True)
                f.write_text('changed')
                with self.assertRaises(AssertionError):history.update(check=True)

    def test_results_do_not_change_evaluator_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'score.py').write_text('x=1');before=history.fingerprint(p)
            (p/'results').mkdir();(p/'results/new.json').write_text('{}')
            self.assertEqual(before,history.fingerprint(p))
            (p/'score.py').write_text('x=2');self.assertNotEqual(before,history.fingerprint(p))

    def test_pending_has_no_invented_scores(self):
        text=history.render([{'id':'v2','change':'unmeasured','status':'pending evaluation'}])
        self.assertNotIn('pending evaluation',text);self.assertNotIn('v2',text);self.assertNotIn('0.0000',text)

    def test_model_column_reads_immutable_legacy_result(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);result=root/'evals/results/legacy';result.mkdir(parents=True)
            (result/'metrics.json').write_text(json.dumps({'model':'gpt-6-astra','token_usage':{'delta':{'total_tokens':7362686}}}))
            record={'id':'legacy','change':'baseline','status':'evaluated historical','result':'evals/results/legacy/README.md','summary':{'case_count':10,'breast_dice':.82,'union_dice':.83,'nipple_dice':.4,'nipple_distance_mm':12}}
            original=json.loads(json.dumps(record))
            with patch.object(history,'ROOT',root):text=history.render([record])
            self.assertIn('| Model |',text);self.assertIn('| gpt-6-astra |',text)
            self.assertNotIn('Nb tokens',text);self.assertNotIn('~7.4M',text)
            self.assertEqual(record,original)

    def test_model_label(self):
        record={'id':'new','change':'local evaluation','status':'evaluated local','model':'gpt-6.1-sol','model_label':'sol6.1','summary':{'case_count':10,'breast_dice':.82,'union_dice':.83,'nipple_dice':.34,'nipple_distance_mm':12.59}}
        text=history.render([record])
        self.assertIn('| gpt-6.1-sol (sol6.1) |',text)
        self.assertTrue(text.splitlines()[-1].endswith('| 12.59 |'))

if __name__=='__main__':unittest.main()
