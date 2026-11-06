# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Skill source](https://img.shields.io/badge/Skill-Markdown%20%2B%20YAML-2563EB)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/CFX-skill?style=social)](https://github.com/hongwenwang36-eng/CFX-skill/stargazers)

Describe your simulation in plain language. Codex writes scripts and uses MCP to automate **ANSYS Workbench + CFX simulations**.

## What it can do

- **Geometry and meshing** — Create or import geometry and use ICEM CFD or Ansys Meshing as requested.
- **CFX solving** — Script materials, boundary conditions, physics and solving, then check the results.
- **Custom control** — Write a master WBJN for parameter sweeps, conditional logic and numerical iterations.
- **Parameterization** — Configure Workbench Parameter Set and design points for the task.
- **Project delivery** — Save a reopenable `.wbpj`, companion files, results and scripts for inspection in CFD-Post.

## Authoring languages

The project combines **Python 3.10+ runtime tools, Markdown Skill instructions (Chinese) and YAML configuration**. Python handles reusable execution and verification; Codex generates case-specific WBJN, ICEM Tcl/Replay, CFX CCL/CEL and session scripts.

## How it works

The Skill guides Codex in writing scripts. MCP calls the software, and WBJN orchestrates the simulation.

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## Python tools

`scripts/cfx_runtime.py` provides installation checks, MCP batch execution, fresh-log and artifact checks, project save/reopen, delivery packaging and SHA-256 verification. Run these commands from the repository; see the [runtime guide](references/runtime.md) for full options.

```powershell
python scripts/cfx_runtime.py doctor
python scripts/cfx_runtime.py --help
```

Simulation execution uses MCP to call Workbench by default. Run with the companion MCP virtual environment’s Python to reuse its dependencies. Geometry, mesh, physics and custom algorithms are generated for each task.

## Install and use

**1. Prepare the environment**

Use Windows with Git, Python 3.10+ and Codex. Install licensed ANSYS Workbench, CFX and either ICEM CFD or Ansys Meshing as needed. A case has been validated on ANSYS 2025 R1.

**2. Install the Skill**

Run these commands in PowerShell to install it in the current user’s Codex skills directory.

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/CFX-skill.git (Join-Path $skillParent 'cfx-skill')
```

Confirm that `%USERPROFILE%\.agents\skills\cfx-skill\SKILL.md` exists. Codex discovers skills automatically; restart it if the Skill does not appear. Run `git pull` in this folder to update an existing installation. Avoid installing the same Skill in multiple skill directories. [Official skill locations](https://learn.chatgpt.com/docs/build-skills)

**3. Configure the companion MCP**

Install the Skill and MCP separately. If [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp) is already configured, skip to the connection check.

<details>
<summary>First-time MCP setup: commands and Codex configuration</summary>

Install the MCP and its Python dependencies, then add the following to `%USERPROFILE%\.codex\config.toml`. Edit an existing entry with the same name instead of duplicating it. These paths use drive D and ANSYS 2025 R1; adjust them for your installation.

```powershell
git clone https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp.git D:\ansys-workbench-mcp
py -3 -m venv D:\ansys-workbench-mcp\.venv
& D:\ansys-workbench-mcp\.venv\Scripts\python.exe -m pip install -r D:\ansys-workbench-mcp\requirements.txt
```

```toml
[mcp_servers.ansys-workbench]
command = 'D:\ansys-workbench-mcp\.venv\Scripts\python.exe'
args = ['D:\ansys-workbench-mcp\mcp_server.py']
cwd = 'D:\ansys-workbench-mcp'
startup_timeout_sec = 30
tool_timeout_sec = 600
enabled = true

[mcp_servers.ansys-workbench.env]
ANSYS_WORKBENCH_MCP_HOME = 'D:\ansys-workbench-mcp'
ANSYS_RUNWB2 = 'D:\Program Files\ANSYS Inc\v251\Framework\bin\Win64\RunWB2.exe'
ANSYS_SPACECLAIM = 'D:\Program Files\ANSYS Inc\v251\scdm\SpaceClaim.exe'
ANSYS_CFX_PRE = 'D:\Program Files\ANSYS Inc\v251\CFX\bin\cfx5pre.exe'
ANSYS_CFX_SOLVE = 'D:\Program Files\ANSYS Inc\v251\CFX\bin\cfx5solve.exe'
ANSYS_CFX_POST = 'D:\Program Files\ANSYS Inc\v251\CFX\bin\cfx5post.exe'
ANSYS_ICEM_CFD = 'D:\Program Files\ANSYS Inc\v251\icemcfd\win64_amd\bin\icemcfd.bat'
```

</details>

**4. Check the connection**

Save the configuration, restart Codex and send this request. Check that the required program paths exist and the Workbench bridge connects before running a simulation.

```text
Check the ansys-workbench MCP using check_ansys_installation.
Confirm Workbench, CFX and the selected mesher are available.
Then start the Workbench bridge and check its connection.
```

**5. Start a simulation**

Send the following to Codex with your geometry, materials, boundary conditions, mesh requirements and output folder.

```text
Use $cfx-skill to complete a CFX simulation.
Write scripts based on my geometry, materials, boundary conditions and mesh requirements.
Execute through MCP and deliver a reopenable Workbench project with solved results.
```

Specify ICEM CFD or Ansys Meshing, and request Parameter Set, parameter sweeps or custom iterations as needed. Open the delivered `.wbpj`, keep its matching `_files` folder, and open CFD-Post from Results to view contours.

[MIT License](LICENSE)

## Example results

Velocity and pressure contours from a completed CFX simulation are shown below.

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="Velocity contour" /><br />
  <img src="assets/original_pressure.png" width="680" alt="Pressure contour" />
</p>
