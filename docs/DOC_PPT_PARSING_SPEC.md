# 旧版 .doc 和 .ppt 文件解析方案规范

## 1. 背景

当前项目中 `.doc`（旧版 Word 二进制 OLE2 格式）依赖 `antiword` 命令行工具提取文本，`.ppt`（旧版 PowerPoint 二进制格式）直接跳过不处理。两者均存在以下问题：

- **antiword**：2005 年后停止维护，Windows 上安装困难，仅支持纯文本提取，不支持 `.ppt`
- **`.ppt` 跳过**：5 个旧版 `.ppt` 文件完全未处理，知识库内容缺失

本方案采用 `win32com`（Windows COM 自动化）替代 antiword，同时支持 `.doc` 和 `.ppt` 解析。

---

## 2. 方案概述

### 2.1 原理

通过 `pywin32` 库的 `win32com.client` 接口，调用系统中已安装的 Microsoft Word / PowerPoint 的 COM 对象，在后台打开文件并提取文本。

### 2.2 安装

```bash
pip install pywin32
```

**前提条件**：系统已安装 Microsoft Office（Word + PowerPoint）。

### 2.3 优缺点

| 优点 | 缺点 |
|------|------|
| 安装简单（仅 `pip install pywin32`） | 必须已安装 Microsoft Office |
| 使用 Office 原生解析器，保真度最高 | COM 自动化在无人值守场景可能有弹窗风险 |
| 同时支持 .doc 和 .ppt | 仅限 Windows 平台 |
| 无需额外系统安装 | 多个 Office 实例并发打开时可能冲突 |

---

## 3. 实现

### 3.1 .doc 解析

```python
def parse_doc_with_win32com(file_path):
    """使用 win32com 提取 .doc 文件文本"""
    from win32com.client import Dispatch
    word = Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(os.path.abspath(file_path))
        text = doc.Content.Text
        doc.Close(SaveChanges=False)
    finally:
        word.Quit()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)
```

### 3.2 .ppt 解析

```python
def parse_ppt_with_win32com(file_path):
    """使用 win32com 提取 .ppt 幻灯片文本"""
    from win32com.client import Dispatch
    ppt = Dispatch("PowerPoint.Application")
    ppt.Visible = False
    try:
        pres = ppt.Presentations.Open(os.path.abspath(file_path), False, False, False)
        all_text = []
        for slide in pres.Slides:
            slide_content = []
            for shape in slide.Shapes:
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    slide_content.append(shape.TextFrame.TextRange.Text.strip())
            if slide_content:
                all_text.append(f"[幻灯片 {slide.Number}] " + "\n".join(slide_content))
        pres.Close()
    finally:
        ppt.Quit()
    return "\n".join(all_text)
```

### 3.3 集成到 build_and_save()

在 `4-disney_build_index.py` 的 `build_and_save()` 中更新 `.doc` 和 `.ppt` 的处理分支：

- `.doc` 处理：优先使用 `parse_doc_with_win32com()`，失败时降级到 antiword（如已安装）
- `.ppt` 处理：使用 `parse_ppt_with_win32com()`，失败时跳过并打印警告

---

## 4. 新增依赖

```
pywin32==306
```

添加到 `requirements.txt`。

---

## 5. 测试用例

| 编号 | 输入 | 预期行为 |
|------|------|---------|
| DP-01 | 标准 .doc 文件（OLE2 格式） | 成功提取文本，内容非空 |
| DP-02 | 含表格的 .doc 文件 | 提取包含表格数据的文本 |
| DP-03 | 含中文内容的 .doc 文件 | 正确提取中文，无乱码 |
| DP-04 | 空 .doc 文件 | 返回空字符串或 None，不报错 |
| DP-05 | 标准 .ppt 文件 | 成功提取幻灯片文本，包含幻灯片编号 |
| DP-06 | 含备注的 .ppt 文件 | 提取幻灯片文本及备注内容 |
| DP-07 | 含中文的 .ppt 文件 | 正确提取中文，无乱码 |
| DP-08 | .doc 解析失败 | 降级到 antiword 或跳过并打印警告 |
| DP-09 | .ppt 解析失败 | 跳过并打印警告，不中断整体流程 |
| DP-10 | 无 MS Office | 打印清晰错误提示，跳过解析 |
