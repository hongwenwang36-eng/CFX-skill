# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/cfx-skill?style=social)](https://github.com/hongwenwang36-eng/cfx-skill/stargazers)

解析の要件を自然言語で伝えると、Codex がスクリプトを作成し、MCP を通じて **ANSYS Workbench + CFX の解析を自動化**します。

## できること

- **形状とメッシュ** — 形状を作成・読み込み、要件に応じて ICEM CFD または Ansys Meshing を使用。
- **CFX 解析** — 材料・境界条件・物理モデル・求解をスクリプトで設定し、結果を確認。
- **制御ロジック** — WBJN でパラメータ走査、条件分岐、数値反復などを実装。
- **パラメータ化** — Workbench Parameter Set と設計点を要件に応じて設定。
- **成果物** — 再度開ける `.wbpj`、関連ファイル、結果とスクリプトを保存し、CFD-Post で確認可能。

## 連携の仕組み

Skill が Codex のスクリプト作成を導き、MCP がソフトウェアを呼び出し、WBJN が解析全体を制御します。

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## インストールと使い方

Windows、有効な ANSYS ライセンス、および [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp) を設定した Codex が必要です。

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/cfx-skill.git (Join-Path $skillParent 'cfx-skill')
```

インストール後、Codex に入力

```text
$cfx-skill を使って、単純な管内の水流を解析してください。
ICEM CFD でメッシュを作成し、MCP で全工程を実行してください。
Workbench で開けるプロジェクトと解析結果を保存してください。
```

Ansys Meshing、パラメータ化、独自の制御ロジックも指定できます。各ワークフローは解析ケースごとに検証します。

[MIT License](LICENSE)

## 解析結果

角管の水流テストで ICEM メッシュ作成、Workbench 連携、CFX 求解を完了しました。以下は速度と圧力のコンターです。

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="速度コンター" /><br />
  <img src="assets/original_pressure.png" width="680" alt="圧力コンター" />
</p>
