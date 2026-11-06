# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/cfx-skill?style=social)](https://github.com/hongwenwang36-eng/cfx-skill/stargazers)

Describe your simulation in plain language. Codex writes scripts and uses MCP to automate **ANSYS Workbench + CFX simulations**.

## What it can do

- **Geometry and meshing** — Create or import geometry and use ICEM CFD or Ansys Meshing as requested.
- **CFX solving** — Script materials, boundary conditions, physics and solving, then check the results.
- **Custom control** — Write a master WBJN for parameter sweeps, conditional logic and numerical iterations.
- **Parameterization** — Configure Workbench Parameter Set and design points for the task.
- **Project delivery** — Save a reopenable `.wbpj`, companion files, results and scripts for inspection in CFD-Post.

## How it works

The Skill guides Codex in writing scripts. MCP calls the software, and WBJN orchestrates the simulation.

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## Install and use

Requires Windows, a valid ANSYS license and Codex configured with [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp).

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/cfx-skill.git (Join-Path $skillParent 'cfx-skill')
```

Then ask Codex

```text
Use $cfx-skill to simulate water flow in a simple duct.
Mesh it with ICEM CFD and execute the workflow through MCP.
Deliver a Workbench project that I can reopen, with solved results.
```

You can also request Ansys Meshing, parameterization or custom control logic. Each workflow is validated for its case.

[MIT License](LICENSE)

## Example results

The duct flow test completed ICEM meshing, Workbench integration and CFX solving; velocity and pressure contours are shown below.

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="Velocity contour" /><br />
  <img src="assets/original_pressure.png" width="680" alt="Pressure contour" />
</p>
