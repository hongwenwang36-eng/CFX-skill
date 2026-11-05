# Ansys Meshing 路线

使用 Fluid Flow (CFX) 的 Mesh 单元，或把独立 Mesh 系统的输出连接到 CFX Setup。需要保留可编辑的几何和网格控制时，使用几何驱动的 Mesh 单元；Workbench 的 Mesh.Import 会把它转成文件容器。

**脚本分工。** 从实际系统取得 Mesh 容器，在 WBJN 中读取本次编写的 Meshing Python 脚本并发送给编辑器。以下是 2025 R1 的调用形式；`cfx_system` 和 `meshing_python` 分别由主控从项目和本次脚本取得。

```python
mesh = cfx_system.GetContainer(ComponentName="Mesh")
mesh.Edit()
mesh.SendCommand(Language="Python", Command=meshing_python)
mesh.Exit()
cfx_system.GetComponent(Name="Mesh").Update()
```

在编辑器脚本里按 Named Selection 找体、面、边，核对匹配数量，再设置 Method、Sizing、Sweep、Inflation 等实际需要的控制，生成网格并导出统计。使用安装版本支持的对象和属性；可从已有模型的录制或该版本脚本帮助取得。Workbench 默认的 SendCommand 语言为 JavaScript，发送 Python 时须显式指定语言。

**层数要求。** 以“油膜厚度方向 20 层六面体”为例，先识别可配对的源面、目标面及扫掠方向，验证源面全四边形及所有目标体可扫掠，再设置扫掠分段。验收实际单元类型，并在指定薄膜区域核对贯穿厚度的单元层数。壁面 Inflation 层数与跨整个间隙的单元数分别统计。若几何不满足，定位需要分割或调整的体，保留用户指定的单元类型。

**交给 CFX 前。** 检查实际体数、各域单元数、质量指标及最差位置、命名边界和接口两侧，确认下游识别到正确的域与区域。几何变动后重新检查命名作用域和层数。

[Workbench Mesh 容器与 SendCommand](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/wb2_js/ContainerName35.html) · [Sweep 方法和分段](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/wb_msh/ds_sweep_method_option.html)
