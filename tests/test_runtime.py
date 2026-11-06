"""Failure-path and file-integrity tests; these do not simulate CFD physics."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("cfx_runtime", Path(__file__).parents[1] / "scripts/cfx_runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.journal = self.root / "控制.wbjn"
        self.journal.write_text("# test executor replaces Workbench", encoding="utf-8")
        self.log = self.root / "workflow.log"
        self.result = self.root / "result.res"
        self.solver = self.root / "solver.out"

    def tearDown(self):
        self.temp.cleanup()

    def run_case(self, executor, **kwargs):
        return runtime.run_case(self.journal, self.root, self.log, "DONE", [self.result],
                                executor=executor, **kwargs)

    def successful_executor(self, *args, **kwargs):
        self.log.write_text("DONE\n", encoding="utf-8")
        self.result.write_bytes(b"test-only output, not a CFX result")
        return {"ok": True}

    def test_success_requires_new_artifacts_and_marker(self):
        report = self.run_case(self.successful_executor)
        self.assertTrue(report["ok"])
        self.assertTrue(Path(report["report"]).is_file())

    def test_stale_output_rejected_despite_zero_exit_code(self):
        self.result.write_bytes(b"old")
        def executor(*args, **kwargs):
            self.log.write_text("DONE\n")
            return {"ok": True}
        self.assertFalse(self.run_case(executor)["ok"])

    def test_old_marker_cannot_certify_appended_failure(self):
        self.log.write_text("DONE\n")
        def executor(*args, **kwargs):
            with self.log.open("a") as stream:
                stream.write("new run failed\n")
            self.result.write_bytes(b"new output")
            return {"ok": True}
        self.assertFalse(self.run_case(executor)["ok"])

    def test_identical_rewritten_completion_log_is_accepted(self):
        self.log.write_text("DONE\n")
        os.utime(self.log, ns=(1_000_000_000, 1_000_000_000))
        self.assertTrue(self.run_case(self.successful_executor)["ok"])

    def test_failed_process_cannot_be_overridden_by_outputs(self):
        def executor(*args, **kwargs):
            self.successful_executor()
            return {"ok": False, "returncode": 2}
        self.assertFalse(self.run_case(executor)["ok"])

    def test_timeout_is_preserved_in_report(self):
        report = self.run_case(lambda *a, **k: {"ok": False, "timed_out": True, "pid": 123})
        self.assertFalse(report["ok"])
        self.assertTrue(report["execution"]["timed_out"])

    def test_solver_errors_override_termination_match(self):
        def executor(*args, **kwargs):
            self.successful_executor()
            self.solver.write_text("targets reached\n| ERROR #123: failure\n")
            return {"ok": True}
        report = self.run_case(executor, solver_log=self.solver, solver_success="targets reached")
        self.assertFalse(report["ok"])
        self.assertTrue(report["solver_log"]["analysis"]["errors"])

    def test_solver_must_match_case_specific_termination(self):
        def executor(*args, **kwargs):
            self.successful_executor()
            self.solver.write_text("maximum iterations reached\n")
            return {"ok": True}
        report = self.run_case(executor, solver_log=self.solver, solver_success="targets reached")
        self.assertFalse(report["ok"])

    def test_invalid_solver_rule_rejected_before_execution(self):
        with self.assertRaises(re.error):
            self.run_case(self.successful_executor, solver_log=self.solver, solver_success="[")

    def test_zero_error_count_is_not_a_solver_failure(self):
        self.assertTrue(runtime.analyze_solver_log("Error: 0\ntargets reached\n", "targets reached")["ok"])
        self.assertFalse(runtime.analyze_solver_log("ERROR IN SOLVER\ntargets reached\n", "targets reached")["ok"])

    def make_project(self):
        project = self.root / "工程.wbpj"
        project.write_text("test-only project placeholder")
        files = runtime.project_files(project)
        files.mkdir()
        (files / "solution.res").write_bytes(b"test-only result placeholder")
        return project

    def test_delivery_preserves_companion_and_detects_tampering(self):
        project = self.make_project()
        self.log.write_text("diagnostic log")
        output = self.root / "delivery"
        report = runtime.package_project(project, output, [self.journal, self.log], require_result=True)
        self.assertTrue(report["ok"])
        (output / project.name).write_bytes(b"damaged")
        self.assertFalse(runtime.verify_package(output)["ok"])

    def test_delivery_requires_result_when_requested(self):
        project = self.make_project()
        (runtime.project_files(project) / "solution.res").unlink()
        (runtime.project_files(project) / "mesh.dat").write_text("mesh")
        with self.assertRaises(ValueError):
            runtime.package_project(project, self.root / "delivery", require_result=True)

    def test_cli_json_is_utf8_with_chinese_paths(self):
        project = self.make_project()
        result = subprocess.run([sys.executable, str(Path(runtime.__file__)), "inspect", "--project", str(project)],
                                capture_output=True, check=True)
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertTrue(report["ok"])
        self.assertIn("工程.wbpj", report["checks"][0]["path"])

    def test_delivery_refuses_recursive_destination_and_overwrite(self):
        project = self.make_project()
        with self.assertRaises(ValueError):
            runtime.package_project(project, runtime.project_files(project) / "nested")
        with self.assertRaises(FileExistsError):
            runtime.package_project(project, self.root)

    def test_manifest_path_cannot_escape_delivery(self):
        project = self.make_project()
        output = self.root / "delivery"
        runtime.package_project(project, output)
        manifest = json.loads((output / "delivery.json").read_text())
        manifest["files"][0]["path"] = "../outside"
        runtime.write_json(output / "delivery.json", manifest)
        with self.assertRaises(ValueError):
            runtime.verify_package(output)

    def test_save_generates_actual_open_save_reopen_journal(self):
        project = self.make_project()
        destination = self.root / "另存.wbpj"
        def executor(journal, workdir, console, timeout, **kwargs):
            text = journal.read_text(encoding="utf-8")
            self.assertEqual(text.count("Open(FilePath="), 2)
            self.assertIn("Save(FilePath=", text)
            # Execute only the final ordinary-Python log-writing block.
            tail = text[text.index("with open("):]
            exec(tail, {})
            destination.write_text("new test project")
            files = runtime.project_files(destination)
            files.mkdir()
            (files / "data").write_text("data")
            return {"ok": True}
        self.assertTrue(runtime.save_project(project, destination, executor=executor)["ok"])


if __name__ == "__main__":
    unittest.main()
