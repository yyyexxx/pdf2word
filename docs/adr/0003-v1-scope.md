# ADR 0003: V1 转换范围

## 状态

已采纳

## 背景

需确定 V1 支持的转换对。文档域（PDF/Word/PPT）+ 图片理论可行 12 对，但需按"用户价值 × 技术验证价值"排序。

## 决策

V1 仅支持三对：

1. **PDF → Word** — 核心，验证语义推断算法
2. **PDF → 图片** — 视觉层渲染的自然副产品
3. **图片 → PDF** — 像素封装，验证 Reader/Writer 管道

## 理由

- PDF→Word 是项目起点，也是最大技术挑战（坐标→结构推断）
- PDF→图片 复用同一套 PyMuPDF 渲染，边际成本极低
- 图片→PDF 让用户至少能完成一个"闭环"（图片→PDF→Word），即使没意义也证明管道可用
- Word→* 和 PPT↔* 的 Reader 实现需要 python-docx/python-pptx 的深入集成，复杂度高，V2 再做
- PPT 相关的跨域转换（PPT→Word）需要语义层较完整后才有效果

## 后果

- V1 Reader: PDF Reader + Image Reader
- V1 Writer: DOCX Writer + PDF Writer + Image(png/jpg) Writer
- Word Reader 和 PPT Reader/Writer 延后
- 双层模型在 V1 中以视觉层为主，语义层仅实现段落合并和标题检测（PDF→Word 的最小必要子集）
