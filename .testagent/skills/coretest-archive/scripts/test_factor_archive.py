"""Regression checks for factor IDs, TP relations and repeat Archive."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import factor_archive as archive


class FactorArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.state_file = root / "archive" / "archive_state.json"
        self.state_file.parent.mkdir()
        self.state_file.write_text(json.dumps({
            "schema_version": 2, "context": {"pbi": 266926538, "tr_id": 4029},
            "request": {"execution_plan": {"ts": ["TS_17"],
                                            "tp": ["TS_17/TP.17.01"]}},
            "ts": {"TS_17": {"status": "succeeded", "platform_id": 38490}},
            "tp": {}, "factor": {},
        }), encoding="utf-8")
        self.tr_info = root / "tr_info.json"
        self.tr_info.write_text(json.dumps({"requirements": [{
            "requirement_number": "SR001", "requirement_id": "2096516380"}]}), encoding="utf-8")
        self.factor = {"testFactorId": "9f609356af2247605f7b2d6f7acfaf1e",
                       "name": "IP 类型", "number": "CLI_TF_DATA_002", "type": 1,
                       "assoActType": "SceneAnalysis", "sourceType": "TestFactorLibrary",
                       "factorType": "BusinessInterImplAnalysis", "pbi": "266926538"}
        self.plan = {"ts_key": "TS_17", "ts_type": "scene", "test_factors": [self.factor],
                     "scene_factors": [], "tp_factors": {"TP.17.01": {
                         "test_factor_ids": [self.factor["testFactorId"]],
                         "scene_factor_codes": []}}}
        self.tp_json = {"tps": [{"tp_id_temp": "TP.17.01", "tpName": "关联测试点",
                                 "tpType": "BusinessSceneAnalysis",
                                 "tpSourceType": "基于业务场景设计—场景因子",
                                 "requirement_ids": "SR001"}]}
        self.args = SimpleNamespace(action="create-tp", cli=Path("coretool-cli"), state_file=self.state_file,
                                    ts_key="TS_17", ts_type="scene", ts_id=38490,
                                    pbi=266926538, tr_id="4029", creator="c00959281",
                                    idp_doc_id="doc-id", tr_info_file=self.tr_info,
                                    tp_id_temp="TP.17.01")

    def test_relation_id_is_rejected(self):
        self.factor["testFactorId"] = "28894"
        with self.assertRaisesRegex(ValueError, "UUID"):
            archive.validate(self.plan, self.tp_json, "TS_17", "scene")

    def test_feature_contract_allows_only_test_factors(self):
        self.plan["ts_type"] = "feature"
        archive.validate(self.plan, self.tp_json, "TS_17", "feature")
        self.plan["scene_factors"] = [{"factorCode": "SC01", "factorName": "场景因子"}]
        with self.assertRaisesRegex(ValueError, "非 scene"):
            archive.validate(self.plan, self.tp_json, "TS_17", "feature")

    def test_scene_list_with_blank_number_uses_name_for_rerun(self):
        scene = {"factorCode": "TFACTOR001", "factorName": "产品环境IP类型"}
        self.assertTrue(archive.contains([{"number": "", "name": "产品环境IP类型"}],
                                         "scene", scene))
        self.assertFalse(archive.contains([{"number": "TFACTOR002", "name": "产品环境IP类型"}],
                                          "scene", scene))

    def test_tp_create_passes_uuid_and_requirement_without_rewriting_source(self):
        calls = []

        def fake_cli(_cli, *args):
            calls.append(args)
            if args[2:4] == ("tp", "list"):
                return {"items": [], "pagination": {"total": 0, "page_size": 10}}
            return {"id": 50001}

        with patch.object(archive, "run_cli", side_effect=fake_cli):
            result = archive.create_tp(self.args, self.plan, self.tp_json)
        self.assertEqual(result["id"], 50001)
        created = calls[-1]
        self.assertEqual(created[created.index("--tp-source-type") + 1],
                         "business_scenario_factor")
        relations = json.loads(created[created.index("--relations") + 1])
        self.assertEqual(relations["testFactorIdList"][0]["testFactorId"],
                         self.factor["testFactorId"])
        self.assertEqual(relations["tpAssociationRequirementAlmIdList"], ["2096516380"])
        self.assertEqual(self.tp_json["tps"][0]["tpSourceType"],
                         "基于业务场景设计—场景因子")

    def test_ts_factor_rerun_queries_and_does_not_create_duplicate(self):
        self.args.action = "sync-ts"
        calls = []

        def fake_cli(_cli, *args):
            calls.append(args)
            return {"items": [{"test_factor_id": self.factor["testFactorId"]}],
                    "pagination": {"total": 1}}

        with patch.object(archive, "run_cli", side_effect=fake_cli):
            result = archive.sync_ts(self.args, self.plan)
            rerun = archive.sync_ts(self.args, self.plan)
        self.assertEqual([item["status"] for item in result["results"]], ["succeeded"])
        self.assertEqual(rerun["results"], result["results"])
        self.assertTrue(all(args[4] == "list" for args in calls))
        state = archive.load_state(self.state_file)
        self.assertEqual(state["factor"][f"TS_17/test/{self.factor['testFactorId']}"]["status"],
                         "succeeded")

    def test_ts_factor_create_is_confirmed_by_followup_query(self):
        self.args.action = "sync-ts"
        calls = []

        def fake_cli(_cli, *args):
            calls.append(args)
            if args[4] == "create":
                payload = Path(args[args.index("--factor-file") + 1])
                self.assertEqual(json.loads(payload.read_text(encoding="utf-8"))[0]
                                 ["testFactorId"], self.factor["testFactorId"])
                return {"created": 1}
            if len(calls) == 1:
                return {"items": [], "pagination": {"total": 0, "page_size": 10}}
            return {"items": [{"test_factor_id": self.factor["testFactorId"]}],
                    "pagination": {"total": 1, "page_size": 10}}

        with patch.object(archive, "run_cli", side_effect=fake_cli):
            result = archive.sync_ts(self.args, self.plan)
        self.assertEqual(result["results"][0]["status"], "succeeded")
        self.assertEqual([args[4] for args in calls], ["list", "create", "list"])

    def test_scene_tp_can_send_both_factor_types(self):
        scene = {"factorCode": "TFACTOR001", "sceneFactorCode": "TFACTOR001",
                 "factorName": "产品环境IP类型", "assoActType": "SceneAnalysis",
                 "sourceType": "scene", "pbi": "266926538"}
        self.plan["scene_factors"] = [scene]
        self.plan["tp_factors"]["TP.17.01"]["scene_factor_codes"] = ["TFACTOR001"]
        commands = []

        def fake_cli(_cli, *args):
            commands.append(args)
            if args[2:4] == ("tp", "list"):
                return {"items": [], "pagination": {"total": 0, "page_size": 10}}
            return {"id": 50002}

        with patch.object(archive, "run_cli", side_effect=fake_cli):
            result = archive.create_tp(self.args, self.plan, self.tp_json)
        self.assertTrue(result["success"])
        command = commands[-1]
        relations = json.loads(command[command.index("--relations") + 1])
        self.assertEqual(relations["sceneFactorIdList"][0]["factorCode"], "TFACTOR001")
        self.assertEqual(relations["testFactorIdList"][0]["testFactorId"],
                         self.factor["testFactorId"])

    def test_no_match_plan_continues_without_cli_factor_writes(self):
        self.args.action = "sync-ts"
        self.plan["test_factors"] = []
        self.plan["tp_factors"]["TP.17.01"]["test_factor_ids"] = []
        archive.validate(self.plan, self.tp_json, "TS_17", "scene")
        with patch.object(archive, "run_cli") as cli:
            result = archive.sync_ts(self.args, self.plan)
        self.assertEqual(result["results"], [])
        cli.assert_not_called()

    def test_cli_receives_json_with_spaces_as_one_argument(self):
        completed = SimpleNamespace(returncode=0, stdout='{"id":50003}', stderr="")
        relation = '{"name":"DSP CBINFO 因子"}'
        with patch.object(archive.subprocess, "run", return_value=completed) as run:
            self.assertEqual(archive.run_cli("coretool-cli", "--relations", relation),
                             {"id": 50003})
        self.assertEqual(run.call_args.args[0], ["coretool-cli", "--relations", relation])


if __name__ == "__main__":
    unittest.main()
