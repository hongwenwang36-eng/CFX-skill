# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Skill source](https://img.shields.io/badge/Skill-Markdown%20%2B%20YAML-2563EB)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/CFX-skill?style=social)](https://github.com/hongwenwang36-eng/CFX-skill/stargazers)

用自然语言描述仿真需求，让 Codex 编写脚本，通过 MCP 自动完成 **ANSYS Workbench + CFX 仿真**。

## 能做什么

- **几何与网格** — 创建或导入几何，按要求使用 ICEM CFD 或 Ansys Meshing。
- **CFX 求解** — 编写设置与求解脚本，配置材料、边界条件和物理模型，检查求解结果。
- **自定义控制** — 编写 WBJN 主控，支持参数扫描、条件判断、数值迭代等计算逻辑。
- **参数化** — 按需求配置 Workbench Parameter Set 和设计点。
- **工程交付** — 保存可重新打开的 `.wbpj`、配套文件、结果与脚本，便于自行打开 CFD-Post 查看云图。

## 编写语言

本项目使用 **Python 3.10+ 执行工具 + Markdown（中文 Skill 指令）+ YAML 配置**。Python 封装通用执行与验收操作，Codex 按算例生成 WBJN、ICEM Tcl/Replay 和 CFX CCL/CEL、会话脚本。

## 如何配合

Skill 指导 Codex 编写脚本，MCP 负责调用软件，WBJN 串联整个仿真流程。

## Python 工具

`scripts/cfx_runtime.py` 提供程序检测、MCP 批处理、新日志与产物检查、工程另存重开、交付整理和 SHA-256 校验。在本仓库目录运行以下命令，完整参数见 [Python 工具说明](references/runtime.md)。

```powershell
python scripts/cfx_runtime.py doctor
python scripts/cfx_runtime.py --help
```

执行仿真时默认通过 MCP 调用 Workbench；使用配套 MCP 虚拟环境的 Python 即可复用其依赖。几何、网格、物理模型与自定义算法仍按需求生成。

## 安装与使用

**1. 准备环境**

使用 Windows，安装 Git、Python 3.10+ 和 Codex；安装具备有效许可的 ANSYS Workbench、CFX，以及所需的 ICEM CFD 或 Ansys Meshing。本项目已在 ANSYS 2025 R1 上完成算例验证。

**2. 安装 Skill**

在 PowerShell 中执行，将仓库放入当前用户的 Codex 技能目录。

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/CFX-skill.git (Join-Path $skillParent 'cfx-skill')
```

安装完成后，确认 `%USERPROFILE%\.agents\skills\cfx-skill\SKILL.md` 存在。Codex 会自动发现技能；若列表未出现，重启 Codex。已有安装可在该目录运行 `git pull`；避免在多个技能目录重复安装同名 Skill。[官方技能目录说明](https://learn.chatgpt.com/docs/build-skills)

**3. 配置配套 MCP**

Skill 与 MCP 分别安装。已配置 [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp) 的用户可直接进入连接检查。

<details>
<summary>首次安装 MCP：展开查看命令与 Codex 配置</summary>

先安装 MCP 及其 Python 依赖，再向 `%USERPROFILE%\.codex\config.toml` 添加以下配置；已有同名配置项时修改原项。示例使用 D 盘与 ANSYS 2025 R1，请按本机位置修改路径。

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

**4. 检查连接**

保存配置并重启 Codex，发送以下请求。确认所需程序路径存在、Workbench bridge 可以连接后再运行仿真。

```text
检查 ansys-workbench MCP，调用 check_ansys_installation，
确认 Workbench、CFX 和所选网格工具可用，
然后启动 Workbench bridge 并检查连接。
```

**5. 发起仿真**

在 Codex 中输入，并附上几何文件、材料、边界条件、网格要求和保存位置。

```text
使用 $cfx-skill，完成 CFX 仿真。
根据我提供的几何、材料、边界条件和网格要求编写脚本，
通过 MCP 执行，并交付可重新打开的 Workbench 工程与求解结果。
```

可指定 ICEM CFD 或 Ansys Meshing，也可提出 Parameter Set、参数扫描或自定义迭代要求。完成后打开交付的 `.wbpj`，保留同名 `_files` 目录，在 Results 中进入 CFD-Post 查看云图。

[MIT License](LICENSE)

## 结果展示

以下为已完成的 CFX 仿真速度与压力云图。

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="速度云图" /><br />
  <img src="assets/original_pressure.png" width="680" alt="压力云图" />
</p>
