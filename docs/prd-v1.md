# PRD: 通用文档格式转换器 V1（已实现）

## 状态：已完成

## Problem Statement

用户需要在本地将 PDF 文件转换为可编辑的 Word 文件，现有方案（在线转换服务、LibreOffice）要么需要上传敏感文件到云端，要么安装体积过大（500MB+），要么转换效果不可控。用户希望有一个轻量、本地运行、核心算法自主可控的转换工具，并能以此为起点逐步扩展到更多文件格式。

## Solution

一个本地运行的桌面应用，单窗口极简界面，支持批量 PDF→Word、PDF→图片、图片→PDF 转换。核心采用自研的双层模型（视觉层+语义层）架构，Reader→Document→Inference→Writer 管道设计，O(N+M) 扩展模式。

Windows 单文件 EXE（55MB），macOS DMG。开源（AGPL）。

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
15. 作为一名普通用户，我想要转换后的 Word 文档保留原标题层级，以便文档结构完整
16. 作为一名普通用户，我想要无边框表格也能被识别并转换，以便表格内容不丢失

## Implementation Decisions

### 架构：双层模型（V1 简化版）

文档在内存中以统一 IR（中间表示）表达。V1 以视觉层为主——每个页面是元素列表（TextElement、ImageElement、TableRegion），附带可空的 SemanticHint 标签（role/level/confidence）。V2 将分离出独立的语义层结构。

IR 数据模型（dataclass）：

```
Document  →  list[Page]  →  list[PageElement]
                              ├── TextElement (text, font_name, font_size, font_color, bold, italic, hint)
                              ├── ImageElement (image_bytes, image_format, width, height)
                              └── TableRegion (rows: list[list[str]])

SemanticHint (role: heading|paragraph|list_item|table_cell, level: int, confidence: float)
```

### 转换管道

流程：`源文件 → Reader → Document → Inference → Document（带 SemanticHint）→ Writer → 目标文件`

- Reader 接口：`read(filepath) -> Document`
- Writer 接口：`write(doc, output_path)`
- 格式注册：dict 映射扩展名 → Reader/Writer 实例
- 管道：串行处理，QThread 异步，signal/slot 更新进度
- 错误处理：失败跳过，转换结束后汇总 X 成功 / Y 失败

### V1 转换对（已实现）

1. PDF → Word（核心）
2. PDF → PNG/JPEG
3. PNG/JPEG → PDF

### 语义推断算法

三个推断器，按顺序执行（table → heading → paragraph）：

**表格检测（table.py）**：两层检测。PyMuPDF `find_tables()` 捕获有边框表格；自研基于文本坐标 X/Y 聚类的网格检测捕获无边框表格（参考 Tabula 思路）。`_cluster_1d` 聚类坐标，`_is_grid` 检查网格填充率，`_build_table_region` 构建 TableRegion。X 和 Y 方向使用各自的容差参数。

**标题检测（heading.py）**：加权评分模型，综合考虑 5 个信号：

- 字号比例（vs `statistics.median_low()` 正文基准）：ratio≥1.8 → +0.40, ≥1.5 → +0.30, ≥1.25 → +0.15
- 加粗：+0.15
- 文本长度（短文本是标题特征）：<30 字 → +0.15
- 编号模式（正则匹配 "1.1"、"第一章"、"III." 等）：+0.20
- 页面顶部位置：+0.05

总分 ≥0.50 判定为标题。使用 `median_low()` 而非 `sorted[n//2]` 以避免偶数元素时取到最大字号。

**段落合并（paragraph.py）**：基于 Y 中心对齐和 X 连续性的合并策略，跳过已标记为 heading 的元素。支持分栏检测——通过分析 X 坐标直方图的垂直间隙检测页面分栏，每栏独立做阅读顺序排列。

### 技术栈

- 语言：Python 3.11+
- UI：PySide6（LGPL），Qt Fusion 样式
- PDF 解析：PyMuPDF (fitz)（AGPL，项目开源）
- DOCX 生成：python-docx
- 图片处理：Pillow
- 测试：pytest（28 个测试）
- 打包：PyInstaller（one-file EXE），实际体积 55MB

### 打包与分发

- **Windows**：`build.bat` → PyInstaller → `dist/pdf2word.exe`（55MB 便携版）。可选 `makensis scripts/installer.nsi` → 安装包（开始菜单/桌面快捷方式/注册表卸载）
- **macOS**：`./build.sh` → PyInstaller → `dist/pdf2word`。可选 DMG 创建（带 /Applications 拖放快捷方式）→ `scripts/sign_mac.sh`（codesign + notarytool）
- 关键教训：从 Anaconda 构建会打包 200+ 个无关包（775MB），必须用干净 venv

## Testing Decisions

### 测试原则

只测试模块的外部行为（输入→输出），不测试内部实现。使用程序化生成或固定样本文件作为输入。

### 测试覆盖（28 个测试，全部通过）

| 模块 | 测试数 | 测试类型 |
|---|---|---|
| IR Model | 5 | 数据结构构造和 SemanticHint 绑定 |
| PDF Reader | 3 | 用自动生成的 PDF 验证元素提取、元数据 |
| Image Reader | 2 | 用自动生成的 PNG 验证尺寸和字节 |
| DOCX Writer | 3 | 文本/标题/表格三种元素类型的输出验证 |
| Inference | 10 | 段落合并（同行/换行/远距）、标题检测（大字号/加粗/编号模式）、表格检测（网格/非网格）、完整推断管道 |
| Pipeline | 5 | PDF→DOCX 端到端、不支持的格式、格式检测、目标列表、注册表 |

### 不做

- PySide6 UI 层（手工验证）
- 第三方库（PyMuPDF、python-docx）内部行为

## Out of Scope

- Word→PDF / Word→图片 / PPT 相关所有转换（V2）
- Excel 和 CAD 所有转换（V3）
- 表格合并单元格的还原（V2）
- 分栏识别（已部分实现基础版，多栏精确阅读顺序 V2）
- 复杂排版：水印、批注、表单域、目录结构
- 持久化的中间文件格式（明确不做）
- 云服务 / API 形式

## Further Notes

- PyMuPDF 的 AGPL 协议要求项目开源
- macOS 分发需 Apple Developer Program（$99/年）+ 签名公证
- 语义推断质量取决于测试 PDF 的多样性；建议收集不同排版风格的样本持续改进
- 项目完整文档：CONTEXT.md（领域术语），docs/adr/（5 份架构决策）
