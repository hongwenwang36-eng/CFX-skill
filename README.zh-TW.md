# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/cfx-skill?style=social)](https://github.com/hongwenwang36-eng/cfx-skill/stargazers)

用自然語言描述模擬需求，讓 Codex 編寫腳本，透過 MCP 自動完成 **ANSYS Workbench + CFX 模擬**。

## 能做什麼

- **幾何與網格** — 建立或匯入幾何，依需求使用 ICEM CFD 或 Ansys Meshing。
- **CFX 求解** — 編寫設定與求解腳本，配置材料、邊界條件與物理模型，檢查求解結果。
- **自訂控制** — 編寫 WBJN 主控，支援參數掃描、條件判斷與數值迭代等計算邏輯。
- **參數化** — 依需求配置 Workbench Parameter Set 與設計點。
- **工程交付** — 儲存可重新開啟的 `.wbpj`、配套檔案、結果與腳本，方便自行在 CFD-Post 查看雲圖。

## 如何配合

Skill 指導 Codex 編寫腳本，MCP 負責呼叫軟體，WBJN 串聯整個模擬流程。

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## 安裝與使用

需要 Windows、有效的 ANSYS 授權，以及已設定 [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp) 的 Codex。

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/cfx-skill.git (Join-Path $skillParent 'cfx-skill')
```

安裝後在 Codex 中輸入

```text
使用 $cfx-skill，完成一個簡單的管道水流模擬。
使用 ICEM CFD 劃分網格，透過 MCP 執行整個流程，
交付可以在 Workbench 中開啟的工程與求解結果。
```

也可以指定 Ansys Meshing，或提出參數化、自訂控制邏輯等需求；具體流程依算例驗證。

[MIT License](LICENSE)

## 結果展示

方管水流測試已完成 ICEM 網格、Workbench 整合與 CFX 求解，以下為速度與壓力雲圖。

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="速度雲圖" /><br />
  <img src="assets/original_pressure.png" width="680" alt="壓力雲圖" />
</p>
