# ICEM CFD 路线

在 Workbench 中建立或复用 Geometry → ICEM CFD Model → CFX Setup 的数据连接。优先使用与工程关联的 ICEM 模型、参数和 Replay。已有 Blocking 时先读取几何、Part 与边/面关联，验证适用于本次几何，再调整节点分布。全新几何按实际拓扑编写 Tcl / Replay。关键命令从本机版本帮助或录制取得；脚本按次序加载几何、建立或更新分块与投影、设置边分布、生成并检查网格、写出供下游读取的网格。

- 区分用户给出的节点数和单元数。简单未分段的 blocking 边上，20 个单元对应 21 个节点；多段、周期或合并边按实际连接逐段核对。保留偏置方向及首末间距的物理含义。
- 同时有流体域和固体域时分别识别体 Part、壁面及热交换接口两侧，核对流固各域统计。共享节点或非共形接口依算例约定，进入 CFX 后检查两侧映射。
- 从实际 pre-mesh / 输出网格检查单元类型和数量、指定方向层数、负体积及适用质量指标。保留可编辑的 Tcl 和必要几何、Blocking 与项目文件。日志记录质量定义和最差值，阈值取自该任务或已验证基线。
- 使用独立 ICEM 会话或 batch Replay 时，先建立写出和导入步骤，并让 WBJN 在每次几何变化后等待对应的新网格、更新 CFX 输入。独立 ICEM 与 Workbench 中的组件可指向不同数据库，须核对设计点、路径及网格统计。若约定从工程重新生成网格，在新打开的工程副本中实际验证一次更新。

[ICEM CFD 的 Workbench 组件、Replay 与参数](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/wb2_help/wb2h_IcemCFD.html) · [ICEM Tcl 脚本](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/icm_pguide/ipguide_basic.html)

Workbench 工程交付时，将独立 ICEM 的几何、Blocking 和网格保存为实际 .prj，再导入工程并建立 ICEM 模型到 CFX Setup 的数据连接。重新更新网格和求解，检查组件内的文件与结果一致；验证从 ICEM 模型单元可以打开网格。交付说明明确指出该单元的位置。
