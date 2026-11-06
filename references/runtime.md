# Python 执行与交付工具

入口是 `scripts/cfx_runtime.py`，运行于 **Workbench 外的 Python 3.10+**。不替代用户算例的几何、网格、边界条件或自定义算法脚本。

| 命令 | 用途 |
| --- | --- |
| `doctor` | 检测 Workbench、CFX、SpaceClaim、ICEM 路径，不启动求解 |
| `run` | 运行 WBJN，核对本次完成标记、产物更新和可选的 CFX 日志终止规则 |
| `inspect` | 只读检查现有工程配套目录、结果文件和指定日志 |
| `save` | 用 Workbench 打开源工程、另存副本，并重新打开副本 |
| `package` | 复制工程、同名 `_files` 及指定脚本、日志到新目录，生成 SHA-256 清单 |
| `verify-package` | 依据 `delivery.json` 检查传输后的文件完整性 |

## 环境与调用

`doctor`、`inspect`、`package` 和 `verify-package` 只依赖 Python 标准库。`run` 和 `save` 默认 `--via mcp`，需要当前 Python 安装 `mcp`，并以 `--mcp-root` 指定配套 MCP 仓库。推荐复用配套 MCP 的虚拟环境。

以下 `$runtime` 指向实际安装的 Skill 入口，`$case` 是本次算例的绝对路径。示例只展示工具参数，运行前由 Codex 编写对应算例的 WBJN 与模块脚本。

```powershell
$runtime = Join-Path $env:USERPROFILE '.agents/skills/cfx-skill/scripts/cfx_runtime.py'
$python = 'D:\ansys-workbench-mcp\.venv\Scripts\python.exe'
$case = 'D:\cases\cfx_case'
& $python $runtime doctor
```

已安装在其他目录时使用实际路径。`doctor --ansys-root 'D:\Program Files\ANSYS Inc\v251'` 可指定版本；否则先读 `ANSYS_*` / `AWP_ROOTxxx` 环境变量，再查找 C、D 盘的常见安装目录。`ok` 针对 Workbench 和 CFX 所需程序，几何及网格工具分别核对 `programs` 内的 `exists`。

## 执行主控

```powershell
& $python $runtime run `
  --journal "$case\run.wbjn" --workdir $case `
  --log "$case\workflow.log" --marker 'CASE_ACCEPTED' `
  --expect "$case\model.wbpj" `
  --expect "$case\model_files\dp0\CFX\CFX\model_001.res" `
  --mcp-root 'D:\ansys-workbench-mcp' --timeout 7200
```

结果路径必须来自本次实际系统与求解输出，不要照抄示例中的编号。主控仅在本次验收通过、保存工程后写入完成标记。`run` 拒绝旧产物、空文件、未更新日志、只存在于旧日志前缀的完成标记，以及进程报告的失败；每次在算例的 `.cfx-skill/<run-id>/` 保存 `report.json` 和执行日志。stdout 输出 JSON，退出码 `0` 表示本命令检查通过，`1` 表示检查失败，`2` 表示参数或调用错误。

需要验收 CFX 日志时，同时提供 `--solver-log` 和 `--solver-success`。后者为从当前版本日志与本次验收要求确定的正则表达式，例如确认过的稳态收敛终止语句。瞬态需匹配规定终止时刻的成功信息，不能套用稳态“收敛”措辞。工具检查本次新增或重写的日志段，并拒绝其中的错误；残差阈值、质量守恒、目标时刻和外层判定仍由算例脚本核对后再写主控完成标记。

已有工程的只读检查用 `inspect --project <路径> --result <路径>`，也支持同一组 CFX 日志参数。此命令不证明文件来自本轮，不实际重开 Workbench，也不证明 `.res` 已关联至工程的 Results。

仅在确有需要时使用 `--via native --ansys-root <安装目录>` 直接启动 RunWB2。运行期间避免另一个会话同时写入同一工程。超时会保留失败报告；原生模式报告进程 PID，不自动重复求解，恢复前检查 ANSYS 子进程、日志和锁。MCP 模式沿用配套服务器的进程超时行为。

## 工程另存与重开

```powershell
& $python $runtime save `
  --source "$case\model.wbpj" --project "$case\delivery_model.wbpj" `
  --mcp-root 'D:\ansys-workbench-mcp' --timeout 600
```

该操作生成并实际运行 `Open → Save → Reset → Open` 的 WBJN，完成后才写成功标记。默认拒绝覆盖现有工程；需要覆盖时显式指定 `--overwrite`。源工程需已保存且未被其他会话占用；操作当前已打开且尚未保存的模型时，用现有 MCP 实时会话保存，不另起批处理读取旧磁盘版本。工程重开通过后，仍按执行与验收指南核对模块联系和 Results 数据加载。

## 整理与校验交付

关闭或停止工程写入后，复制到新的交付目录。

```powershell
& $python $runtime package `
  --project "$case\model.wbpj" --destination 'D:\deliveries\cfx_case' `
  --include "$case\run.wbjn" --include "$case\workflow.log" --require-result
& $python $runtime verify-package --directory 'D:\deliveries\cfx_case'
```

默认不覆盖现有目录。`--include` 可重复传入文件或目录，保存在交付目录的 `extras/`；必需的外部依赖先由 Workbench 归档或迁入工程，复制到 `extras/` 本身不会修改工程引用。`--require-result` 要求工程 `_files` 内有非空 `.res`，适用于完整求解交付。复制时检查源文件和副本哈希，发现过程中被改写则报错，未写出 `delivery.json` 的目录视为未完成。哈希校验只证明文件完整，物理验收和 Results 关联检查仍须单独完成。

## 验证

仓库根目录运行 `python -m unittest discover -s tests -v`，检查旧结果误判、日志标记、求解失败与超时、工程保存控制及交付文件损坏等路径。单元测试中的文件为测试替身，不是 CFD 计算结果。

本工具已在 ANSYS 2025 R1 上实测通过 MCP 启动 Workbench、执行 WBJN、创建与保存 CFX 系统、另存并重开工程，以及交付文件哈希校验。
