# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

![Skill source](https://img.shields.io/badge/Skill-Markdown%20%2B%20YAML-2563EB)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/CFX-skill?style=social)](https://github.com/hongwenwang36-eng/CFX-skill/stargazers)

用自然語言描述模擬需求，讓 Codex 編寫腳本，透過 MCP 自動完成 **ANSYS Workbench + CFX 模擬**。

## 能做什麼

- **幾何與網格** — 建立或匯入幾何，依需求使用 ICEM CFD 或 Ansys Meshing。
- **CFX 求解** — 編寫設定與求解腳本，配置材料、邊界條件與物理模型，檢查求解結果。
- **自訂控制** — 編寫 WBJN 主控，支援參數掃描、條件判斷與數值迭代等計算邏輯。
- **參數化** — 依需求配置 Workbench Parameter Set 與設計點。
- **工程交付** — 儲存可重新開啟的 `.wbpj`、配套檔案、結果與腳本，方便自行在 CFD-Post 查看雲圖。

## 編寫語言

Skill 本體使用 **Markdown（中文指令）+ YAML 設定**編寫。Codex 讀取指令後，依算例產生 Workbench WBJN（Python）、ICEM Tcl/Replay 與 CFX CCL/CEL、工作階段腳本。

## 如何配合

Skill 指導 Codex 編寫腳本，MCP 負責呼叫軟體，WBJN 串聯整個模擬流程。

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## 安裝與使用

**1. 準備環境**

使用 Windows，安裝 Git、Python 3.10+ 與 Codex；安裝具有效授權的 ANSYS Workbench、CFX，以及所需的 ICEM CFD 或 Ansys Meshing。本專案已在 ANSYS 2025 R1 上完成算例驗證。

**2. 安裝 Skill**

在 PowerShell 執行，將儲存庫放入目前使用者的 Codex 技能目錄。

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/CFX-skill.git (Join-Path $skillParent 'cfx-skill')
```

確認 `%USERPROFILE%\.agents\skills\cfx-skill\SKILL.md` 存在。Codex 會自動發現技能；若列表未出現，重新啟動 Codex。已有安裝可在該目錄執行 `git pull`，避免在多個技能目錄重複安裝同名 Skill。[官方技能目錄說明](https://learn.chatgpt.com/docs/build-skills)

**3. 設定配套 MCP**

Skill 與 MCP 分別安裝。已設定 [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp) 的使用者可直接進入連線檢查。

<details>
<summary>首次安裝 MCP：展開查看命令與 Codex 設定</summary>

先安裝 MCP 與 Python 相依套件，再於 `%USERPROFILE%\.codex\config.toml` 加入以下設定；已有同名項目時修改原項。範例使用 D 槽與 ANSYS 2025 R1，請依本機位置修改路徑。

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

**4. 檢查連線**

儲存設定並重新啟動 Codex，傳送以下要求。確認所需程式路徑存在、Workbench bridge 可連線後再執行模擬。

```text
檢查 ansys-workbench MCP，呼叫 check_ansys_installation，
確認 Workbench、CFX 與所選網格工具可用，
再啟動 Workbench bridge 並檢查連線。
```

**5. 開始模擬**

在 Codex 輸入，並附上幾何檔案、材料、邊界條件、網格需求與儲存位置。

```text
使用 $cfx-skill，完成 CFX 模擬。
依我提供的幾何、材料、邊界條件與網格需求編寫腳本，
透過 MCP 執行，並交付可重新開啟的 Workbench 工程與求解結果。
```

可指定 ICEM CFD 或 Ansys Meshing，也可提出 Parameter Set、參數掃描或自訂迭代要求。完成後開啟 `.wbpj`，保留同名 `_files` 目錄，在 Results 進入 CFD-Post 查看雲圖。

[MIT License](LICENSE)

## 結果展示

以下為已完成的 CFX 模擬速度與壓力雲圖。

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="速度雲圖" /><br />
  <img src="assets/original_pressure.png" width="680" alt="壓力雲圖" />
</p>
