# CONTEXT — 通用文档格式转换器

## 项目定位

一个轻量、本地的文档格式转换工具。V1 聚焦文档域（PDF/Word/PPT + 图片），V2/V3 扩展 Excel 和 CAD。

## 领域术语

### 架构

- **双层模型 (Dual-Layer Model)**：将文档表达为语义层（逻辑结构）和视觉层（精确排版）的分离模型。两层通过 SemanticRef 弱关联。
- **语义层 (Semantic Layer)**：表达"文档讲了什么"——段落、标题、表格、列表等结构化信息。不包含坐标。
- **视觉层 (View Layer)**：表达"文档看起来什么样"——页面元素（文本框、图片、矢量路径）及其精确坐标、尺寸、层级。
- **SemanticRef**：语义层 Block 与视觉层 PageElement 之间的弱引用指针，携带置信度。
- **Canvas**：视觉层的画布抽象。页面型文档（PDF/Word）有固定尺寸，数据型/几何型文档（Excel/CAD）的 Canvas 可为无限。
- **中心辐条架构 (Hub-and-Spoke)**：源格式→中间模型→目标格式的转换管道。Reader 负责提取，Writer 负责生成。O(N+M) 而非 O(N×M)。
- **中间表示 (IR, Intermediate Representation)**：内存中的双层模型实例。不做持久化文件格式，仅用 JSON/MessagePack 做调试快照。

### 转换

- **有损转换 (Lossy Conversion)**：目标格式无法承载源格式的全部信息时，丢弃不可表达的部分。例如 PDF→Word 丢失精确坐标，Excel→PDF 丢失公式。
- **语义推断 (Semantic Inference)**：从纯排版信息（PDF 的坐标/字号）推算出结构化信息（标题层级、段落边界、表格结构）。是 PDF→Word 的核心挑战，结果带置信度。
- **渲染 (Rendering)**：将文档模型转换为像素或固定页面（如 →PNG/PDF）。只消费视觉层。

### 格式域

- **文档域 (Document Domain)**：PDF、DOCX、PPTX。共同特征是页面/幻灯片 + 排版 + 语义结构。
- **像素域 (Pixel Domain)**：PNG、JPEG、TIFF、BMP。纯像素矩阵，无结构。
- **数据域 (Data Domain)**：XLSX、CSV。数据网格 + 公式 DAG，不关心页面。
- **几何域 (Geometry Domain)**：DWG、DXF、SVG。精确几何体 + 约束，不关心排版。

## 技术栈

- **语言**：Python（PyMuPDF、python-docx 生态最成熟）
- **UI**：PySide6（LGPL，原生控件，不引入 Web 运行时）
- **打包**：PyInstaller，目标体积 ~60-80MB
- **平台**：Windows 10+ / macOS 12+

## V1 范围

三对转换：

1. **PDF → Word**：核心，验证语义推断（坐标→段落/标题/表格）
2. **PDF → 图片**：视觉层逐页渲染
3. **图片 → PDF**：像素封装，零算法复杂度

## UI 设计

单窗口，三部分：文件上传区（拖放+批量）、格式选择区（自动识别源格式，仅显示可用目标格式）、转换按钮（有文件时亮起，转换中显示进度）。

## 项目结构

- `src/ui/` — PySide6 界面层
- `src/core/` — IR 模型 + Reader/Writer 抽象接口 + 具体实现
- `src/inference/` — 语义推断（段落合并、标题检测、表格检测）
- `tests/` — 测试
- `resources/` — 测试用样本文件

## 决策记录

- [0001-双模型架构选型](docs/adr/0001-dual-layer-architecture.md)
- [0002-不创建中间文件格式](docs/adr/0002-no-intermediate-file-format.md)
- [0003-v1-转换范围](docs/adr/0003-v1-scope.md)
- [0004-pyside6-技术栈](docs/adr/0004-pyside6-tech-stack.md)
- [0005-管道与错误处理](docs/adr/0005-pipeline-and-error-handling.md)
