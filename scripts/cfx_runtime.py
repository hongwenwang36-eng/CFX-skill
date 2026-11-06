#!/usr/bin/env python3
"""Reusable CFX Skill operations. Run outside Workbench with Python 3.10+."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid


PROGRAMS = {
    "runwb2": ("ANSYS_RUNWB2", "Framework/bin/Win64/RunWB2.exe"),
    "spaceclaim": ("ANSYS_SPACECLAIM", "scdm/SpaceClaim.exe"),
    "cfx_pre": ("ANSYS_CFX_PRE", "CFX/bin/cfx5pre.exe"),
    "cfx_solve": ("ANSYS_CFX_SOLVE", "CFX/bin/cfx5solve.exe"),
    "cfx_post": ("ANSYS_CFX_POST", "CFX/bin/cfx5post.exe"),
    "icem_cfd": ("ANSYS_ICEM_CFD", "icemcfd/win64_amd/bin/icemcfd.bat"),
}
ERROR_PATTERN = re.compile(
    r"^\s*[| ]*\s*(?:FATAL\b|ERROR\b(?!\s*(?:[:=]\s*)?0\b)|Traceback\b)"
    r"|floating point exception|segmentation (?:fault|violation)", re.I)


def absolute(value):
    return Path(value).expanduser().resolve()


def write_json(path, data):
    path = absolute(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot(path):
    path = absolute(path)
    if not path.is_file():
        return {"exists": False, "size": 0, "mtime_ns": None}
    stat = path.stat()
    return {"exists": True, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def artifact(path, before=None, started_ns=None):
    path = absolute(path)
    state = snapshot(path)
    check = {"path": str(path), **state, "ok": state["exists"] and state["size"] > 0}
    if before is not None:
        fresh = (state != before and state["exists"]
                 and state["mtime_ns"] >= started_ns - 2_000_000_000)
        check.update(fresh=fresh, ok=check["ok"] and fresh)
    return check


def read_bytes(path):
    path = absolute(path)
    return path.read_bytes() if path.is_file() else b""


def decode(data):
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeError:
            pass
    return data.decode("utf-8", errors="replace")


def new_log_text(path, previous):
    current = read_bytes(path)
    # A marker retained in an old prefix must not certify an appended failed run.
    appended = previous and len(current) > len(previous) and current.startswith(previous)
    return decode(current[len(previous):] if appended else current)


def analyze_solver_log(text, success_pattern):
    """Use the actual case's termination rule, including transient end-time cases."""
    errors = [line.strip() for line in text.splitlines() if ERROR_PATTERN.search(line)]
    return {
        "ok": bool(text.strip()) and bool(re.search(success_pattern, text, re.I | re.M)) and not errors,
        "success_pattern": success_pattern,
        "termination_matched": bool(re.search(success_pattern, text, re.I | re.M)),
        "errors": errors[-20:],
    }


def project_files(project):
    return project.with_name(project.stem + "_files")


def inspect_project(project):
    project = absolute(project)
    if project.suffix.lower() != ".wbpj":
        raise ValueError("Project must be a .wbpj file")
    check = artifact(project)
    companion = project_files(project)
    has_files = companion.is_dir() and any(p.is_file() for p in companion.rglob("*"))
    check.update(companion=str(companion), companion_has_files=has_files,
                 ok=check["ok"] and has_files)
    return check


def installation(root=None):
    candidates = [absolute(root)] if root else []
    if not root:
        candidates.extend(absolute(value) for key, value in os.environ.items()
                          if re.fullmatch(r"AWP_ROOT\d+", key) and value)
        if os.environ.get("ANSYS_RUNWB2"):
            exe = absolute(os.environ["ANSYS_RUNWB2"])
            if len(exe.parents) >= 4:
                candidates.append(exe.parents[3])
        for base in (Path("C:/Program Files/ANSYS Inc"), Path("D:/Program Files/ANSYS Inc")):
            if base.is_dir():
                candidates.extend(sorted(base.glob("v[0-9]*"), reverse=True))
    selected = next((p for p in candidates if (p / PROGRAMS["runwb2"][1]).is_file()),
                    candidates[0] if candidates else None)
    programs = {}
    for name, (variable, relative) in PROGRAMS.items():
        value = (selected / relative if root else os.environ.get(variable)
                 or (selected / relative if selected else None))
        path = absolute(value) if value else None
        programs[name] = {"path": str(path) if path else None, "exists": bool(path and path.is_file())}
    return {"ok": all(programs[k]["exists"] for k in ("runwb2", "cfx_pre", "cfx_solve")),
            "ansys_root": str(selected) if selected else None, "programs": programs}


async def _mcp_call(root, python, tool, arguments, timeout, environment):
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise RuntimeError("MCP mode needs the mcp package; run this script with the companion MCP's .venv Python") from exc
    root = absolute(root)
    server = root / "mcp_server.py"
    python = absolute(python) if python else root / ".venv/Scripts/python.exe"
    if not server.is_file() or not python.is_file():
        raise ValueError("MCP server/Python not found; set --mcp-root and, if needed, --mcp-python")
    params = StdioServerParameters(command=str(python), args=[str(server)], cwd=str(root), env=environment)
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=timeout + 60)) as client:
            await client.initialize()
            response = await client.call_tool(tool, arguments)
            if response.isError:
                raise RuntimeError(str(response.content))
            structured = response.structuredContent
            body = structured.get("result", structured) if structured else "\n".join(
                block.text for block in response.content if getattr(block, "type", "") == "text")
            return json.loads(body) if isinstance(body, str) else body


def execution_environment(root=None):
    environment = dict(os.environ, LC_ALL="C", LANG="C")
    found = installation(root)
    for name, (variable, _) in PROGRAMS.items():
        if found["programs"][name]["exists"]:
            environment[variable] = found["programs"][name]["path"]
    return environment


def launch(journal, workdir, console, timeout, via="mcp", mcp_root=None, mcp_python=None, ansys_root=None):
    environment = execution_environment(ansys_root)
    if via == "mcp":
        mcp_root = mcp_root or os.environ.get("ANSYS_WORKBENCH_MCP_HOME")
        if not mcp_root:
            raise ValueError("MCP mode requires --mcp-root or ANSYS_WORKBENCH_MCP_HOME")
        environment["ANSYS_WORKBENCH_MCP_HOME"] = str(absolute(mcp_root))
        response = asyncio.run(_mcp_call(mcp_root, mcp_python, "run_workbench_journal", {
            "journal_path": str(journal), "workdir": str(workdir), "batch": True,
            "timeout_seconds": timeout,
        }, timeout, environment))
        write_json(console, response)
        return {"ok": response.get("ok") is True, "via": "mcp", "response": response}
    found = installation(ansys_root)
    if not found["programs"]["runwb2"]["exists"]:
        raise ValueError("RunWB2 not found; set --ansys-root or ANSYS_RUNWB2")
    command = [found["programs"]["runwb2"]["path"], "-B", "-R", str(journal)]
    with console.open("wb") as output:
        process = subprocess.Popen(command, cwd=str(workdir), env=environment,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            code = process.wait(timeout=timeout)
            return {"ok": code == 0, "via": "native", "pid": process.pid, "returncode": code}
        except subprocess.TimeoutExpired:
            # ANSYS spawns child applications. Preserve their state for diagnosis,
            # rather than killing unrelated sessions or starting a duplicate solve.
            return {"ok": False, "via": "native", "pid": process.pid, "timed_out": True,
                    "process_may_be_running": True}


def run_case(journal, workdir, log, marker, expected, solver_log=None, solver_success=None,
             timeout=3600, executor=launch, **transport):
    journal, workdir, log = absolute(journal), absolute(workdir), absolute(log)
    if not journal.is_file() or journal.suffix.lower() != ".wbjn":
        raise ValueError("A readable .wbjn journal is required")
    if not marker.strip() or not expected or timeout <= 0:
        raise ValueError("A completion marker, expected outputs and positive timeout are required")
    if bool(solver_log) != bool(solver_success):
        raise ValueError("Use --solver-log and --solver-success together")
    if solver_success:
        re.compile(solver_success)
    paths = list(dict.fromkeys(absolute(p) for p in expected))
    if log in paths or journal in paths:
        raise ValueError("Expected artifacts must be separate from the journal and completion log")
    baseline = {p: snapshot(p) for p in paths + [log] + ([absolute(solver_log)] if solver_log else [])}
    old_log = read_bytes(log)
    old_solver = read_bytes(solver_log) if solver_log else b""
    workdir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = workdir / ".cfx-skill" / run_id
    run_dir.mkdir(parents=True)
    report_path = run_dir / "report.json"
    started_ns = time.time_ns()
    report = {"run_id": run_id, "ok": False, "status": "running", "journal": str(journal),
              "started_at": datetime.now(timezone.utc).isoformat(), "report": str(report_path),
              "scope": "solver_termination_and_artifacts" if solver_log else "workflow_artifacts"}
    write_json(report_path, report)
    try:
        execution = executor(journal, workdir, run_dir / "console.log", timeout, **transport)
    except Exception as exc:
        execution = {"ok": False, "error": str(exc)}
    checks = [artifact(p, baseline[p], started_ns) for p in paths]
    project_checks = [inspect_project(p) for p in paths if p.suffix.lower() == ".wbpj"]
    marker_check = artifact(log, baseline[log], started_ns)
    marker_check["marker_seen_in_new_content"] = marker in new_log_text(log, old_log)
    marker_check["ok"] &= marker_check["marker_seen_in_new_content"]
    solver_check = None
    if solver_log:
        path = absolute(solver_log)
        solver_check = {**artifact(path, baseline[path], started_ns),
                        "analysis": analyze_solver_log(new_log_text(path, old_solver), solver_success)}
        solver_check["ok"] &= solver_check["analysis"]["ok"]
    ok = (execution.get("ok") is True and marker_check["ok"]
          and all(check["ok"] for check in checks + project_checks)
          and (solver_check is None or solver_check["ok"]))
    report.update(ok=bool(ok), status="succeeded" if ok else "failed", execution=execution,
                  artifacts=checks, projects=project_checks, completion_log=marker_check,
                  solver_log=solver_check, elapsed_seconds=round((time.time_ns() - started_ns) / 1e9, 3))
    write_json(report_path, report)
    return report


def save_project(source, destination, workdir=None, overwrite=False, **transport):
    source, destination = absolute(source), absolute(destination)
    if not inspect_project(source)["ok"]:
        raise ValueError("Source project or its companion _files directory is missing/empty")
    if destination.suffix.lower() != ".wbpj":
        raise ValueError("Destination must end in .wbpj")
    if (destination.exists() or project_files(destination).exists()) and not overwrite:
        raise ValueError("Destination exists; select a new project path or explicitly use --overwrite")
    destination.parent.mkdir(parents=True, exist_ok=True)
    workdir = absolute(workdir) if workdir else destination.parent
    stage = workdir / ".cfx-skill" / ("save-" + uuid.uuid4().hex[:12])
    stage.mkdir(parents=True)
    log, journal = stage / "save.log", stage / "save.wbjn"
    marker = "PROJECT_SAVED_AND_REOPENED_" + uuid.uuid4().hex
    # repr of forward-slash paths is compatible with Workbench's IronPython.
    code = ("Open(FilePath=u%r)\nSave(FilePath=u%r, Overwrite=%r)\nReset()\nOpen(FilePath=u%r)\n"
            "with open(u%r, 'w') as report:\n    report.write(%r)\n") % (
                source.as_posix(), destination.as_posix(), overwrite, destination.as_posix(),
                log.as_posix(), marker + "\n")
    journal.write_text("# -*- coding: utf-8 -*-\n" + code, encoding="utf-8")
    return run_case(journal, workdir, log, marker, [destination], **transport)


def _regular_files(root):
    root = absolute(root)
    entries = [root] if root.is_file() else [root, *root.rglob("*")]
    for path in entries:
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Package linked files explicitly before delivery: " + str(path))
    return [p for p in entries if p.is_file()]


def package_project(project, destination, includes=(), require_result=False):
    project, destination = absolute(project), absolute(destination)
    if not inspect_project(project)["ok"]:
        raise ValueError("Project or companion _files directory is missing/empty")
    companion = project_files(project)
    if require_result and not any(p.stat().st_size > 0 for p in companion.rglob("*.res") if p.is_file()):
        raise ValueError("No nonempty .res found inside the project's _files directory")
    sources = [(project, Path(project.name)), (companion, Path(companion.name))]
    sources.extend((absolute(p), Path("extras") / absolute(p).name) for p in includes)
    targets = [target for _, target in sources]
    if len(set(targets)) != len(targets):
        raise ValueError("Included files have colliding names")
    files = []
    for source, target in sources:
        if not source.exists():
            raise ValueError("Missing package input: " + str(source))
        if destination == source or source in destination.parents:
            raise ValueError("Delivery directory cannot be inside a package input")
        for path in _regular_files(source):
            relative = target if source.is_file() else target / path.relative_to(source)
            files.append((path, relative, sha256(path)))
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"project": project.name, "scope": "file_integrity", "files": []}
    for source, relative, before in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha256(target) != before or sha256(source) != before:
            raise RuntimeError("File changed during packaging: " + str(source))
        manifest["files"].append({"path": relative.as_posix(), "size": target.stat().st_size, "sha256": before})
    write_json(destination / "delivery.json", manifest)
    return verify_package(destination)


def verify_package(directory):
    directory = absolute(directory)
    manifest = json.loads((directory / "delivery.json").read_text(encoding="utf-8"))
    names = [entry["path"] for entry in manifest["files"]]
    project_name = manifest["project"]
    if (not names or len(set(names)) != len(names) or Path(project_name).name != project_name
            or project_name not in names):
        raise ValueError("Manifest must list a unique local project and its files")
    errors = []
    for entry in manifest["files"]:
        path = (directory / entry["path"]).resolve()
        if directory not in path.parents:
            raise ValueError("Invalid manifest path: " + entry["path"])
        if not path.is_file() or path.stat().st_size != entry["size"] or sha256(path) != entry["sha256"]:
            errors.append(entry["path"])
    project_check = inspect_project(directory / project_name)
    return {"ok": not errors and project_check["ok"], "scope": "file_integrity", "directory": str(directory),
            "project": project_check, "files_checked": len(manifest["files"]), "mismatches": errors}


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="operation", required=True)
    doctor = sub.add_parser("doctor", help="Locate required ANSYS programs without launching them")
    doctor.add_argument("--ansys-root")
    run = sub.add_parser("run", help="Run WBJN and verify this run's completion log and expected artifacts")
    run.add_argument("--journal", required=True)
    run.add_argument("--workdir", required=True)
    run.add_argument("--log", required=True)
    run.add_argument("--marker", required=True)
    run.add_argument("--expect", action="append", required=True, dest="expected")
    run.add_argument("--solver-log")
    run.add_argument("--solver-success", help="Case-specific regex for successful solver termination")
    inspect = sub.add_parser("inspect", help="Check existing project/results/log; does not claim freshness or reopen")
    inspect.add_argument("--project")
    inspect.add_argument("--result", action="append", default=[])
    inspect.add_argument("--solver-log")
    inspect.add_argument("--solver-success")
    save = sub.add_parser("save", help="Use Workbench to open, save and reopen a project copy")
    save.add_argument("--source", required=True)
    save.add_argument("--project", required=True, dest="destination")
    save.add_argument("--workdir")
    save.add_argument("--overwrite", action="store_true")
    for command in (run, save):
        command.add_argument("--via", choices=("mcp", "native"), default="mcp")
        command.add_argument("--mcp-root")
        command.add_argument("--mcp-python")
        command.add_argument("--ansys-root")
        command.add_argument("--timeout", type=int, default=3600)
    package = sub.add_parser("package", help="Copy project and dependencies into a new directory and hash-verify")
    package.add_argument("--project", required=True)
    package.add_argument("--destination", required=True)
    package.add_argument("--include", action="append", default=[], dest="includes")
    package.add_argument("--require-result", action="store_true")
    verify = sub.add_parser("verify-package", help="Verify a delivery.json manifest after copying/transferring")
    verify.add_argument("--directory", required=True)
    return cli


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = vars(parser().parse_args(argv))
    operation = args.pop("operation")
    try:
        if operation == "doctor":
            result = installation(args["ansys_root"])
        elif operation == "run":
            result = run_case(**args)
        elif operation == "save":
            result = save_project(**args)
        elif operation == "package":
            result = package_project(**args)
        elif operation == "verify-package":
            result = verify_package(**args)
        else:
            if not any(args[k] for k in ("project", "result", "solver_log")):
                raise ValueError("Provide --project, --result or --solver-log")
            if bool(args["solver_log"]) != bool(args["solver_success"]):
                raise ValueError("Use --solver-log and --solver-success together")
            checks = ([inspect_project(args["project"])] if args["project"] else [])
            checks.extend(artifact(p) for p in args["result"])
            if args["solver_log"]:
                checks.append(analyze_solver_log(decode(read_bytes(args["solver_log"])), args["solver_success"]))
            result = {"ok": all(c["ok"] for c in checks), "scope": "existing_artifacts", "checks": checks}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, RuntimeError, re.error) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
