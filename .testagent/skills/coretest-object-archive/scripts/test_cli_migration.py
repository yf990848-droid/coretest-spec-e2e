"""Offline regressions for the CLI boundary, using captured-interface fixtures."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import object_cli as obj

SKILLS = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('init_cli', SKILLS / 'test-init-context/scripts/fetch_design_task_info.py')
init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cli = self.root / 'CLI with spaces.exe'
        self.cli.touch()
        self.response = self.root / 'cli/tc_TS_11_TC.01.json'
        self.source = {'name': '中文用例', 'case_id': 'PCF_N23SUB_01_01',
                       'case_id_prefix': 'PCF_N23SUB', 'case_id_number': '1',
                       'case_id_start_value': 0, 'rank': '2', 'auto_type': 0,
                       'AutoType': '1', 'TestType': '78', 'owner': '',
                       'preparation': '准备\n多行', 'test_step': '执行 "步骤"; $() `x`',
                       'expect_output': '结果\n保持原文'}
        self.flags = obj.tc_flags(self.source, 28241, '266926538', 'c00959281')
        self.item = {'id': '155667', 'case_id': self.source['case_id'], 'name': '中文用例',
                     'rank': '2', 'owner': 'c00959281', 'status': 'notArchived',
                     'pbi': '266926538', 'auto_type': 0}

    def reply(self, data, code=0):
        return subprocess.CompletedProcess([], code, json.dumps(data, ensure_ascii=False), '')

    def listing(self, items):
        return self.reply({'items': items, 'pagination': {'total': len(items)}})

    def test_init_schema_and_context_compatibility(self):
        raw = {'pbi': '266926538', 'project_id': 'project', 'tasks': [{
            'design_task_id': '2470', 'idp_doc_id': 'doc',
            'ir_list': [{'requirement_alm_id': '2094163417', 'asso_act_type': '',
                         'sr_list': [{'requirement_parent_id': '2094163417', 'asso_act_type': 'RequirementAnalysis'}]}],
            'feature_list': [{'asso_act_type': 'RequirementAnalysis'}],
            'tr_list': [{'tr_id': '5192', 'tr_name': 'TR', 'relation_requirement': 'IR01',
                         'ir_list': [{'requirement_alm_id': '2094163417', 'requirement_type': 'IR'}]}]}]}
        normalized = init.adapt(raw)
        task = normalized['data'][0]
        self.assertEqual(task['ir_list'][0]['requirementAlmId'], '2094163417')
        self.assertEqual(task['ir_list'][0]['sr_list'][0]['requirementParentId'], '2094163417')
        self.assertIn('requirement_alm_id', task['tr_list'][0]['ir_list'][0])
        self.assertIn('requirement_alm_id', raw['tasks'][0]['ir_list'][0])
        init.save(self.root / 'design_task_info.json', normalized)
        result = subprocess.run([sys.executable, str(SKILLS / 'test-init-context/scripts/generate_tr_context.py'),
                                 '--design-task-info', str(self.root / 'design_task_info.json'),
                                 '--output-root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        cida = obj.read(self.root / '2470/TR_5192/cida_info.json')
        self.assertEqual(cida['requirement_number'], 'IR01')
        self.assertEqual(cida['requirement_id'], '2094163417')

    def test_init_invalid_and_empty(self):
        with self.assertRaises(ValueError):
            init.adapt({'tasks': []})
        self.assertEqual(init.adapt({'pbi': '1', 'project_id': 'p', 'tasks': []})['data'], [])

    def test_init_queries_once_and_preserves_failed_snapshot(self):
        target = self.root / 'design_task_info.json'
        target.write_text('{"old":true}')
        args = ['fetch', '--cli', str(self.cli), '--product-name', 'UPCF 27.0.0',
                '--owner-id', 'c00959281', '--output-root', str(self.root)]
        with patch('sys.argv', args), patch.object(init.subprocess, 'run', return_value=self.reply({}, 1)) as run:
            self.assertEqual(init.main(), 1)
            self.assertEqual(run.call_count, 1)
        self.assertEqual(obj.read(target), {'old': True})
        self.assertTrue((self.root / 'design_task_info.cli_response.json').exists())

    def test_ts_relation_mapping_and_id(self):
        flags = obj.ts_flags({'ts_name': '特性 TS', 'ts_type': 'feature',
                              'featureSelecteds': ['特性一', '特性二'],
                              'requirement_ids': 'IR01,SR02'}, 2470, 5192, 'c00959281')
        self.assertEqual(flags[flags.index('--feature-names') + 1], '特性一,特性二')
        self.assertIn('IR01,SR02', flags)
        with patch.object(obj.subprocess, 'run', return_value=self.reply({'ts_id': 42026})):
            self.assertEqual(obj.Runner(self.cli, self.response).create('ts', flags), '42026')

    def test_exact_tc_mapping_and_card_columns(self):
        self.assertEqual(self.flags[self.flags.index('--case-id') + 1], 'PCF_N23SUB_01_01')
        self.assertEqual(self.flags[self.flags.index('--auto-type') + 1], '0')
        self.assertNotIn('--test-type', self.flags)
        self.assertNotIn('--case-id-number', self.flags)
        self.assertIn('准备\n多行', self.flags)
        self.assertEqual(self.flags[self.flags.index('--owner') + 1], 'c00959281')

    def test_optional_snake_fields(self):
        source = dict(self.source, test_case_type='78', test_environment_type='lab', case_id_type='end_begin')
        flags = obj.tc_flags(source, 28241, '266926538', 'c00959281')
        self.assertEqual(flags[flags.index('--test-type')+1], '78')
        self.assertEqual(flags[flags.index('--test-env-type')+1], 'lab')
        self.assertEqual(flags[flags.index('--case-id-type')+1], 'end_begin')

    def test_nonempty_tc_factors_rejected(self):
        for key in ('action_factor_names', 'data_factor_names', 'actionFactorInfo', 'dataFactorInfo'):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'factor association'):
                obj.tc_flags(dict(self.source, **{key: ['factor']}), 28241, '266926538', 'c00959281')

    def test_empty_message_readback_and_arguments(self):
        responses = [self.listing([]), self.reply({'message': ''}), self.listing([self.item])]
        with patch.object(obj.subprocess, 'run', side_effect=responses) as run:
            self.assertEqual(obj.Runner(self.cli, self.response).create('tc', self.flags), '155667')
        commands = [call.args[0] for call in run.call_args_list]
        self.assertNotIn('--version-pbi', commands[0])
        self.assertIn('执行 "步骤"; $() `x`', commands[1])
        self.assertNotIn('shell', run.call_args.kwargs)
        self.assertEqual(len(obj.read(self.response)['calls']), 3)

    def test_ambiguous_create_retry_only_reads(self):
        with patch.object(obj.subprocess, 'run', side_effect=[self.listing([]), subprocess.TimeoutExpired('cli', 120)]):
            with self.assertRaises(subprocess.TimeoutExpired):
                obj.Runner(self.cli, self.response).create('tc', self.flags)
        with patch.object(obj.subprocess, 'run', return_value=self.listing([self.item])) as run:
            self.assertEqual(obj.Runner(self.cli, self.response).create('tc', self.flags), '155667')
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0][3:5], ['tc', 'list'])

    def test_unconfirmed_write_never_recreated(self):
        with patch.object(obj.subprocess, 'run', side_effect=[self.listing([]), self.reply({'message': ''}), self.listing([])]):
            with self.assertRaisesRegex(ValueError, 'not confirmed'):
                obj.Runner(self.cli, self.response).create('tc', self.flags)
        with patch.object(obj.subprocess, 'run', return_value=self.listing([])) as run:
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                obj.Runner(self.cli, self.response).create('tc', self.flags)
            self.assertEqual(run.call_count, 1)

    def test_changed_request_refused(self):
        with patch.object(obj.subprocess, 'run', side_effect=[self.listing([]), self.reply({}, 1)]):
            with self.assertRaises(ValueError):
                obj.Runner(self.cli, self.response).create('tc', self.flags)
        with patch.object(obj.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'request changed'):
                obj.Runner(self.cli, self.response).create('tc', self.flags + ['--description', 'changed'])
            run.assert_not_called()

    def test_existing_duplicate_mismatch_and_incomplete_list(self):
        for data in ([self.item], [self.item, self.item], [dict(self.item, auto_type=1)]):
            with patch.object(obj.subprocess, 'run', return_value=self.listing(data)) as run:
                with self.assertRaises(ValueError):
                    obj.Runner(self.cli, self.response).create('tc', self.flags)
                self.assertEqual(run.call_count, 1)
        with patch.object(obj.subprocess, 'run', return_value=self.reply({'items': [], 'pagination': {'total': 1}})):
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                obj.Runner(self.cli, self.response).create('tc', self.flags)

    def test_invalid_json_and_zero_ts_id(self):
        with patch.object(obj.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'not json', '')):
            with self.assertRaises(ValueError):
                obj.Runner(self.cli, self.response).call(['tc', 'list', '--tp-id', '28241'])
        for value in (0, '0', None, True, '<TODO:tp>'):
            with self.assertRaises(ValueError):
                obj.positive(value)


if __name__ == '__main__':
    unittest.main()
