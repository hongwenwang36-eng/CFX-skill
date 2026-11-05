# MCP 执行、CFX 与工程验收

**先定位执行环境。** 查询当前连接的 ansys_workbench MCP 工具和参数签名，用 `check_ansys_installation` 确认版本、所需程序和路径。每次运行使用独立算例目录，修改已有工程时先保存工作副本，并保持项目文件与配套目录的名称匹配。记录算例 ID、设计点、输入和运行开始时间。

| 需要的操作 | 已有 MCP 入口及用法 |
|---|---|
| 写入本次生成的脚本 | `write_ansys_script` 接收完整脚本正文及输出路径。先完成具体脚本编写，再调用工具写入。 |
| 独立运行主控 | `run_workbench_journal` 指向本次的主控 WBJN、工作目录和合理超时。需要校验时由主控实际写日志，并在成功分支写唯一完成标记；将日志路径、标记和预期输出传给工具。 |
| 操作指定的已打开工程 | `check_workbench_connection` 和 `get_project_info` 核对会话与工程，按需 `start_workbench_bridge`。通过 `execute_workbench_script` 在该会话执行主控。批处理与实时会话任选一个持有工程；避免同一 Workbench 在执行主控时经 MCP 同步回调自身。 |
| 几何或 ICEM 单独调试 | 需要时使用 `run_spaceclaim_script`、`run_icem_replay`，或连接 ICEM 后使用 `execute_icem_script`。正式迭代须将这些阶段接回主控，并刷新本设计点的下游数据。 |
| CFX 批处理 | `run_cfx_pre_session` 执行 .pre 并可检查预期 .def；`run_cfx_solver` 读取 .def。独立批跑时主控可调相应原生批处理程序、等待并验收；完成后通过本版本支持的工程关联方式接回 CFX Solution/Results。优先使用 Workbench 内的 CFX 系统执行正式求解，便于保存结果关联。 |

**CFX 设置。** 针对实际网格生成 CFX-Pre 命令或 .pre 会话及所需的 CCL/CEL。核对材料、域类型、参考系和壁面运动、边界条件及单位、接口和传热模型。按任务配置监测量，例如指定轴向的力矩、入口出口压差。批处理路径需核查新生成的 .def；求解器写 .out 日志和 .res 结果。闭环读取标量时优先使用求解监测或日志，必要时用只读批处理提取数值。默认保留结果给用户手动查看。

**完成判定。** 按算例的稳态或瞬态设置核对终止原因、目标时刻、残差、守恒或监测量等适用条件，同时核对外层算法的停止条件。确认最终 .res 对应被接受的设计点、网格和输入；旧结果、零长度文件、超时、仅求解器退出码均不足以判定成功。超时先查仍在运行的进程、日志及锁，确认退出后从最近一致状态恢复。对同一错误只有找到新证据并作针对性改动才重试。超出用户给的运行预算、达到算法上限或无法满足物理约束时，保留最近可用工况，标记中断阶段和诊断证据。

**交付。** 保存并重新打开同一 .wbpj，确认配套的同名 _files 目录完整，核对工程内 Geometry、所选网格、CFX Setup/Solution 的联系和状态，验证从相应 Results 单元可以加载本次 .res 以及预期域和结果变量。只检查能否加载数据即可，云图由用户自己创建。若独立求解结果只能通过磁盘手动打开，则继续修复工程关联；无法修复时明确交付缺口。归档引用到的外部几何、网格和结果，避免临时路径依赖。报告打开入口、必须保留的配套文件、可编辑脚本、日志，以及成功/未收敛/未运行的工况。

[CFX 的 Workbench 脚本调用](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/cfx_intr/sect_js_cfx.html) · [Workbench CFX 流程和 Results 入口](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/wb2_help/wb2h_basicffgeomstart.html)
