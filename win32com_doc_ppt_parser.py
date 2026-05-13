# -*- coding: utf-8 -*-
"""
win32com 文档解析器

使用 Microsoft Office COM 接口解析旧版 .doc 和 .ppt 文件。
"""
import os
from win32com.client import Dispatch


def parse_doc_with_win32com(file_path):
    """使用 win32com 提取 .doc 文件文本"""
    try:
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
        if not lines:
            return None
        return '\n'.join(lines)
    except Exception as e:
        print(f"    警告: win32com 解析 .doc 失败: {e}")
        return None


def parse_ppt_with_win32com(file_path):
    """使用 win32com 提取 .ppt 幻灯片文本"""
    try:
        ppt = Dispatch("PowerPoint.Application")
        try:
            pres = ppt.Presentations.Open(os.path.abspath(file_path), WithWindow=False)
            all_text = []
            for slide_idx, slide in enumerate(pres.Slides, 1):
                slide_content = []
                for shape in slide.Shapes:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        slide_content.append(shape.TextFrame.TextRange.Text.strip())
                if slide_content:
                    all_text.append(f"[幻灯片 {slide_idx}] " + "\n".join(slide_content))
            pres.Close()
        finally:
            ppt.Quit()
        return "\n".join(all_text)
    except Exception as e:
        print(f"    警告: win32com 解析 .ppt 失败: {e}")
        return None
