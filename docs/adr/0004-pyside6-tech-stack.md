# ADR 0004: Python + PySide6 技术栈

## 状态

已采纳

## 背景

需要选择编程语言和 UI 框架。约束：Win+Mac 本地运行、安装包小（<100MB）、界面简洁原生、不依赖 Web 运行时。

评估了四种方案：

1. Python + Web UI (FastAPI + 浏览器)
2. Python + PySide6 (Qt 原生)
3. Rust + Tauri
4. Go + Wails

## 决策

**Python + PySide6**。

- 转换引擎：PyMuPDF（PDF 解析）+ python-docx（DOCX 生成）+ Pillow（图片处理）
- UI：PySide6（LGPL 协议，Qt 原生控件）
- 打包：PyInstaller，目标体积 ~60-80MB

## 理由

1. PyMuPDF 是 Python 生态最强的 PDF 解析库，无可替代——Rust/Go 没有同等成熟的替代品
2. V1 核心是算法验证（语义推断），Python 迭代速度最快
3. 用户拒绝了 Web UI，要原生界面
4. PySide6 的 LGPL 协议对闭源商用友好；Dear PyGui 组件太少，tkinter Mac 体验差
5. ~70MB 的打包体积在用户可接受范围内

## 后果

- 需要处理 PyMuPDF 的 AGPL 协议问题——如果在 AGPL 约束下使用，或考虑替代 pdfplumber（MIT）
- PyInstaller 在 Mac 上需处理签名公证（如果分发）
- UI 和转换引擎在同一进程，大文件转换时需用 QThread 避免界面卡死
