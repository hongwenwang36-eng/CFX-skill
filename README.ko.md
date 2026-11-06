# CFX-skill

[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

![Skill source](https://img.shields.io/badge/Skill-Markdown%20%2B%20YAML-2563EB)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hongwenwang36-eng/CFX-skill?style=social)](https://github.com/hongwenwang36-eng/CFX-skill/stargazers)

해석 요구사항을 자연어로 전달하면 Codex가 스크립트를 작성하고 MCP를 통해 **ANSYS Workbench + CFX 해석을 자동화**합니다.

## 주요 기능

- **형상과 격자** — 형상을 생성하거나 가져오고, 요구에 따라 ICEM CFD 또는 Ansys Meshing을 사용합니다.
- **CFX 해석** — 재료, 경계 조건, 물리 모델과 해석 실행을 스크립트로 구성하고 결과를 확인합니다.
- **사용자 정의 제어** — WBJN으로 매개변수 스윕, 조건 분기와 수치 반복 등을 구현합니다.
- **매개변수화** — 요구에 맞게 Workbench Parameter Set과 설계점을 구성합니다.
- **프로젝트 제공** — 다시 열 수 있는 `.wbpj`, 관련 파일, 결과와 스크립트를 저장하여 CFD-Post에서 확인할 수 있습니다.

## 작성 언어

Skill 본체는 **Markdown(중국어 지침) + YAML 설정**으로 작성되었습니다. Codex는 지침을 읽고 사례에 맞게 Workbench WBJN(Python), ICEM Tcl/Replay, CFX CCL/CEL 및 세션 스크립트를 생성합니다.

## 연동 방식

Skill은 Codex의 스크립트 작성을 안내하고, MCP는 소프트웨어를 호출하며, WBJN은 전체 해석 흐름을 제어합니다.

<p align="center">
  <img src="assets/workflow.svg" width="620" alt="仿真需求 → Codex + cfx-skill 编写脚本 → MCP 执行 → 几何、网格、CFX 与工程结果" />
</p>

## 설치 및 사용

**1. 환경 준비**

Windows에 Git, Python 3.10+, Codex를 준비하고, 유효한 라이선스의 ANSYS Workbench, CFX와 필요한 ICEM CFD 또는 Ansys Meshing을 설치합니다. ANSYS 2025 R1에서 사례를 검증했습니다.

**2. Skill 설치**

PowerShell에서 다음 명령을 실행하여 현재 사용자의 Codex 스킬 폴더에 설치합니다.

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/hongwenwang36-eng/CFX-skill.git (Join-Path $skillParent 'cfx-skill')
```

`%USERPROFILE%\.agents\skills\cfx-skill\SKILL.md`가 있는지 확인합니다. Codex가 자동으로 검색하며, 목록에 없으면 다시 시작합니다. 기존 설치를 업데이트하려면 해당 폴더에서 `git pull`을 실행합니다. 여러 스킬 폴더에 같은 Skill을 중복 설치하지 마세요. [공식 스킬 경로 안내](https://learn.chatgpt.com/docs/build-skills)

**3. 연동 MCP 설정**

Skill과 MCP는 별도로 설치합니다. [ANSYS-Workbench-mcp](https://github.com/hongwenwang36-eng/ANSYS-Workbench-mcp)가 이미 설정되어 있으면 연결 확인으로 이동합니다.

<details>
<summary>MCP 최초 설치: 명령과 Codex 설정 보기</summary>

MCP와 Python 의존성을 설치한 후 `%USERPROFILE%\.codex\config.toml`에 다음 설정을 추가합니다. 같은 이름의 항목이 있으면 기존 항목을 수정합니다. 예시는 D 드라이브와 ANSYS 2025 R1을 사용하므로 실제 설치 경로에 맞게 바꾸세요.

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

**4. 연결 확인**

설정을 저장하고 Codex를 다시 시작한 후 다음 요청을 보냅니다. 필수 프로그램 경로와 Workbench bridge 연결을 확인한 후 해석을 실행합니다.

```text
check_ansys_installation으로 ansys-workbench MCP를 확인해 주세요.
Workbench, CFX와 선택한 격자 도구가 사용 가능한지 확인하고,
Workbench bridge를 시작하여 연결을 확인해 주세요.
```

**5. 해석 시작**

다음 요청과 함께 형상 파일, 재료, 경계 조건, 격자 요구사항 및 저장 위치를 Codex에 전달합니다.

```text
$cfx-skill을 사용해 CFX 해석을 완료해 주세요.
제공한 형상, 재료, 경계 조건과 격자 요구사항에 맞게 스크립트를 작성하고,
MCP로 실행한 후 다시 열 수 있는 Workbench 프로젝트와 해석 결과를 저장해 주세요.
```

ICEM CFD 또는 Ansys Meshing을 지정하고 Parameter Set, 매개변수 스윕 또는 사용자 정의 반복을 요청할 수 있습니다. `.wbpj`와 같은 이름의 `_files` 폴더를 함께 보관하고, Results에서 CFD-Post를 열어 등고선을 확인합니다.

[MIT License](LICENSE)

## 해석 결과

완료된 CFX 해석의 속도 및 압력 등고선은 아래와 같습니다.

<p align="center">
  <img src="assets/original_velocity.png" width="680" alt="속도 등고선" /><br />
  <img src="assets/original_pressure.png" width="680" alt="압력 등고선" />
</p>
