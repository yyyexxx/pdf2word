# PRD: 通用文档格式转换器 V1

## Problem Statement

用户需要在本地将 PDF 文件转换为可编辑的 Word 文件，现有方案（在线转换服务、LibreOffice）要么需要上传敏感文件到云端，要么安装体积过大（500MB+），要么转换效果不可控。用户希望有一个轻量、本地运行、核心算法自主可控的转换工具，并能以此为起点逐步扩展到更多文件格式。

## Solution

一个本地运行的桌面应用，单窗口极简界面，支持批量 PDF→Word、PDF→图片、图片→PDF 转换。核心采用自研的双层模型（视觉层+语义层）架构，Reader→Document→Writer 管道设计，O(N+M) 扩展模式。

## User Stories

1. 作为一名普通用户，我想要将 PDF 文件转换为可编辑的 Word 文档，以便修改内容
2. 作为一名普通用户，我想要一次性拖放多个 PDF 文件批量转换，以便节省时间
3. 作为一名普通用户，我想要在文件上传后自动识别文件格式，以便无需手动选择源格式
4. 作为一名普通用户，我想要只看到当前文件格式支持的目标转换选项，以便不会选错格式
5. 作为一名普通用户，我想要将 PDF 的某一页或全部页面导出为图片，以便在需要时使用
6. 作为一名普通用户，我想要将图片封装为 PDF 文件，以便统一管理或打印
7. 作为一名普通用户，我想要看到当前转换进度，以便知道还需等待多久
8. 作为一名普通用户，我想要在批量转换中某个文件失败时其余文件继续处理，以便不会因为一个文件的问题重新开始
9. 作为一名普通用户，我想要在转换完成后看到成功/失败/跳过的汇总结果，以便确认每个文件的处理状态
10. 作为一名普通用户，我想要在 Windows 和 macOS 上都能使用该软件，以便在不同电脑上工作
11. 作为一名普通用户，我想要安装包尽可能小（<100MB），以便快速下载和安装
12. 作为一名普通用户，我想要界面简洁直观、无多余步骤，以便快速完成转换任务
13. 作为一名开发者，我想要转换算法代码结构清晰，以便后续扩展更多格式（PPT、Excel、CAD）
14. 作为一名开发者，我想要 Reader/Writer 有统一的抽象接口，以便新增格式时只需新增一个 Reader 或 Writer

## Implementation Decisions

### 架构：双层模型（V1 简化版）

文档在内存中以统一 IR（中间表示）表达。V1 以视觉层为主——每个页面是元素列表（TextBox、ImageElement、TableRegion），附带可空的 SemanticHint 标签（role + confidence）。V2 将分离出独立的语义层结构。

IR 数据结构：

- **Document**: 页面列表 + 元数据字典
- **Page**: 页码 + 宽高 + 元素列表（z-order）
- **PageElement**: 基类，包含 bbox（坐标矩形）和 element_type
- **TextElement**: 文本 + 字体名/字号/颜色/粗体/斜体
- **ImageElement**: 图片字节数据 + 格式 + 原始尺寸
- **TableRegion**: 二维文本矩阵（V1 不处理合并单元格）
- **SemanticHint**: 附加在 TextElement 上的语义标签（heading/paragraph/list_item/table_cell + 置信度）

### 架构：中心辐照管道

转换流程：`源文件 → Reader → Document → Inference → Document（带语义标签）→ Writer → 目标文件`

- Reader 接口：`read(filepath) -> Document`
- Writer 接口：`write(doc, output_path)`
- 格式注册：简单 dict 映射扩展名到 Reader/Writer 类，不引入插件系统

### V1 转换对

仅三对：

1. PDF → Word（核心，验证语义推断）
2. PDF → 图片（视觉层逐页渲染）
3. 图片 → PDF（像素封装）

### 语义推断

从 PDF 的纯坐标/字体信息推算出文档结构。V1 实现三个推断器：

- **段落合并**：相邻 TextBox 按 Y 坐标间距和 X 对齐合并为段落
- **标题检测**：基于字号阈值和文字位置识别标题层级
- **表格检测**：基于线条位置或文字网格对齐检测表格区域

推断结果以 SemanticHint 形式附加到元素上，DOCX Writer 根据 SemanticHint 选择对应的 Word 样式。

### 技术栈

- 语言：Python 3.11+
- UI：PySide6（LGPL）
- PDF 解析：PyMuPDF（AGPL，项目开源）
- DOCX 生成：python-docx
- 图片处理：Pillow
- 打包：PyInstaller，目标体积 ~60-80MB

### 管道与错误处理

- 串行处理，一个文件完成后再处理下一个
- 失败文件跳过，继续处理后续文件
- 转换结束后汇总：X 成功 / Y 失败
- 转换在 QThread 中运行，通过 signal/slot 更新 UI 进度

### 模块划分

详见 PRD 中的模块接口描述。每个模块都是 deep module——接口简单、内部封装复杂逻辑、可独立测试。

## Testing Decisions

### 测试原则

- 只测试模块的外部行为（输入→输出），不测试内部实现细节
- 每个模块的测试使用固定的样本文件作为输入，验证输出的 Document 结构或生成的文件内容

### 待测试模块

| 模块 | 测试类型 | 测试内容 |
|---|---|---|
| IR Model | 单元测试 | 数据结构构造、序列化/反序列化（JSON 快照） |
| PDF Reader | 单元测试 | 用固定 sample PDF 验证提取的页面数、元素数、文本内容 |
| Image Reader | 单元测试 | 验证单页 Document 生成、图片尺寸正确 |
| DOCX Writer | 单元测试 | 输入已知 Document，验证生成的 DOCX 文件可被 python-docx 重新打开且内容一致 |
| PDF Writer | 单元测试 | 输入已知 Document，验证生成的 PDF 页数正确 |
| Image Writer | 单元测试 | 输入已知 Document，验证输出的图片尺寸和格式 |
| Inference | 单元测试 | 输入精心构造的 Document（含已知坐标的 TextElement），验证 SemanticHint 结果 |
| Pipeline | 集成测试 | 用真实 PDF 样本端到端转换，验证输出文件存在且非空 |

### 不做

- 不测试 PySide6 UI 层（手工验证）
- 不测试第三方库（PyMuPDF、python-docx）的内部行为

## Out of Scope

- Word→PDF / Word→图片 / PPT 相关所有转换（V2）
- Excel 和 CAD 所有转换（V3）
- 表格合并单元格的还原（V2）
- 分栏识别（V2）
- 复杂排版：水印、批注、表单域、目录结构（不做承诺）
- 持久化的中间文件格式（明确不做）
- 云服务 / API 形式提供

## Further Notes

- PyMuPDF 的 AGPL 协议要求项目开源
- macOS 打包需额外处理签名公证
- 语义推断的质量是 V1 成败的关键，需要收集多样化的 PDF 样本进行测试
- 项目结构、技术选型、架构决策的完整记录见 CONTEXT.md 和 docs/adr/
