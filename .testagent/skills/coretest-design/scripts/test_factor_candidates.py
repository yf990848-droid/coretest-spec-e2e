import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import factor_candidates
import factor_plan


class FactorCandidateTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {"items": [{"ts_key": "TS_18", "ts_type": "scene",
                                   "ts_name": "Nsmf/Nupf链路容灾端到端流程"}]}
        self.tp = {"tps": [{"tp_id_temp": "TP.18.01", "tpName": "正常重选"},
                           {"tp_id_temp": "TP.18.02", "tpName": "无可用NWDAF"}]}
        self.test_id = "9f609356-af22-4760-5f7b-2d6f7acfaf1e-1a06a9ae32e"
        self.test_factor = {"test_factor_id": self.test_id, "name": "链路故障",
                            "number": "TF_01"}
        self.scene_factor = {"factor_code": "TFACTOR_01", "factor_name": "链路容灾"}
        self.evidence = {"success": False, "ts_key": "TS_18", "ts_type": "scene",
                         "product": "UPCF", "queries": [], "test_factors": [], "scene_factors": []}

    def test_scene_searches_both_labels_for_ts_and_each_tp(self):
        def fake_search(_script, label, _product, _query):
            item = self.test_factor if label == "TestFactor" else self.scene_factor
            return {"ok": True, "action": "search", "count": 1, "data": [item]}

        with patch.object(factor_candidates, "search", side_effect=fake_search) as search:
            factor_candidates.collect(self.catalog, self.tp, "graph.py", "TS_18", "scene",
                                      "UPCF", self.evidence)
        self.assertEqual(search.call_count, 6)
        self.assertTrue(self.evidence["success"])
        self.assertEqual(len(self.evidence["test_factors"]), 1)
        self.assertEqual(len(self.evidence["scene_factors"]), 1)
        plan = {"test_factors": [{"testFactorId": self.test_id}],
                "scene_factors": [{"factorCode": "TFACTOR_01"}]}
        factor_plan.verify_candidates(self.evidence, plan, self.tp, "TS_18", "scene")
        plan["test_factors"][0]["testFactorId"] = "unseen-uuid"
        with self.assertRaisesRegex(ValueError, "未在图谱查询中查到"):
            factor_plan.verify_candidates(self.evidence, plan, self.tp, "TS_18", "scene")

    def test_failure_does_not_become_empty_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")
            (root / "tp.json").write_text(json.dumps(self.tp), encoding="utf-8")
            (root / "graph.py").write_text("", encoding="utf-8")
            output = root / "candidates.json"
            args = ["factor_candidates.py", "--catalog-file", str(root / "catalog.json"),
                    "--tp-file", str(root / "tp.json"), "--graph-script", str(root / "graph.py"),
                    "--ts-key", "TS_18", "--ts-type", "scene", "--product", "UPCF",
                    "--output", str(output)]
            with patch("sys.argv", args), patch.object(factor_candidates, "search",
                                                      side_effect=ValueError("网关失败")):
                with self.assertRaises(SystemExit) as exit_result:
                    factor_candidates.main()
            self.assertEqual(exit_result.exception.code, 1)
            failed = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(failed["success"])
            with self.assertRaisesRegex(ValueError, "图谱检索未成功"):
                factor_plan.verify_candidates(failed, {"test_factors": [], "scene_factors": []},
                                              self.tp, "TS_18", "scene")

    def test_non_scene_only_queries_test_factors(self):
        self.catalog["items"][0]["ts_type"] = "function"
        self.evidence["ts_type"] = "function"
        with patch.object(factor_candidates, "search", return_value={"ok": True,
                         "count": 0, "data": []}) as search:
            factor_candidates.collect(self.catalog, self.tp, "graph.py", "TS_18", "function",
                                      "UPCF", self.evidence)
        self.assertEqual(search.call_count, 3)
        self.assertEqual(self.evidence["scene_factors"], [])
        factor_plan.verify_candidates(self.evidence,
                                      {"test_factors": [], "scene_factors": []},
                                      self.tp, "TS_18", "function")

    def test_graph_failure_is_not_treated_as_no_results(self):
        response = CompletedProcess([], 0, stdout='{"ok":false,"count":null,"data":null,"error":"网关不可用"}', stderr="")
        with patch.object(factor_candidates.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(ValueError, "网关不可用"):
                factor_candidates.search("graph.py", "TestFactor", "UPCF", "链路容灾")


if __name__ == "__main__":
    unittest.main()
