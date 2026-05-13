# -*- coding: utf-8 -*-
"""
win32com 文档解析器测试

基于 SPEC 中的测试用例 DP-01 到 DP-10。
使用 mock 模拟 win32com COM 对象，不调用真实 Office。
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from win32com_doc_ppt_parser import parse_doc_with_win32com, parse_ppt_with_win32com


class TestParseDocWithWin32Com(unittest.TestCase):
    """测试用例 DP-01 到 DP-04：.doc 解析"""

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp01_standard_doc_returns_text(self, mock_dispatch):
        """DP-01: 标准 .doc 文件成功提取文本，内容非空"""
        mock_word = MagicMock()
        mock_doc = MagicMock()
        mock_doc.Content.Text = "这是迪士尼乐园的介绍文档。\n包含多个段落。\n"
        mock_word.Documents.Open.return_value = mock_doc
        mock_dispatch.return_value = mock_word

        result = parse_doc_with_win32com("test.doc")

        self.assertEqual(result, "这是迪士尼乐园的介绍文档。\n包含多个段落。")
        mock_word.Documents.Open.assert_called_once()
        mock_doc.Close.assert_called_once_with(SaveChanges=False)
        mock_word.Quit.assert_called_once()

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp02_doc_with_table_data(self, mock_dispatch):
        """DP-02: 含表格的 .doc 文件提取包含表格数据的文本"""
        mock_word = MagicMock()
        mock_doc = MagicMock()
        mock_doc.Content.Text = "门票价格表\n| 类型 | 价格 |\n| 成人 | 500 |\n| 儿童 | 300 |\n"
        mock_word.Documents.Open.return_value = mock_doc
        mock_dispatch.return_value = mock_word

        result = parse_doc_with_win32com("table_test.doc")

        self.assertIn("门票价格表", result)
        self.assertIn("| 成人 | 500 |", result)

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp03_chinese_content_no_garbled(self, mock_dispatch):
        """DP-03: 含中文内容的 .doc 文件正确提取中文，无乱码"""
        mock_word = MagicMock()
        mock_doc = MagicMock()
        mock_doc.Content.Text = "上海迪士尼度假区位于中国上海浦东新区。\n开园时间为2016年6月16日。\n"
        mock_word.Documents.Open.return_value = mock_doc
        mock_dispatch.return_value = mock_word

        result = parse_doc_with_win32com("chinese_test.doc")

        self.assertEqual(result, "上海迪士尼度假区位于中国上海浦东新区。\n开园时间为2016年6月16日。")

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp04_empty_doc_returns_none(self, mock_dispatch):
        """DP-04: 空 .doc 文件返回 None，不报错"""
        mock_word = MagicMock()
        mock_doc = MagicMock()
        mock_doc.Content.Text = ""
        mock_word.Documents.Open.return_value = mock_doc
        mock_dispatch.return_value = mock_word

        result = parse_doc_with_win32com("empty.doc")

        self.assertIsNone(result)

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp04_whitespace_only_returns_none(self, mock_dispatch):
        """DP-04: 只有空白内容的 .doc 文件返回 None，不报错"""
        mock_word = MagicMock()
        mock_doc = MagicMock()
        mock_doc.Content.Text = "   \n\n   \t  "
        mock_word.Documents.Open.return_value = mock_doc
        mock_dispatch.return_value = mock_word

        result = parse_doc_with_win32com("whitespace.doc")

        self.assertIsNone(result)


class TestParsePptWithWin32Com(unittest.TestCase):
    """测试用例 DP-05 到 DP-07：.ppt 解析"""

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp05_standard_ppt_with_slide_numbers(self, mock_dispatch):
        """DP-05: 标准 .ppt 文件成功提取幻灯片文本，包含幻灯片编号"""
        mock_ppt = MagicMock()
        mock_pres = MagicMock()

        mock_shape1 = MagicMock()
        mock_shape1.HasTextFrame = True
        mock_shape1.TextFrame.HasText = True
        mock_shape1.TextFrame.TextRange.Text = "迪士尼乐园概述"

        mock_shape2 = MagicMock()
        mock_shape2.HasTextFrame = True
        mock_shape2.TextFrame.HasText = True
        mock_shape2.TextFrame.TextRange.Text = "全球6个迪士尼乐园"

        mock_slide1 = MagicMock()
        mock_slide1.Shapes = [mock_shape1]

        mock_slide2 = MagicMock()
        mock_slide2.Shapes = [mock_shape2]

        mock_pres.Slides = [mock_slide1, mock_slide2]
        mock_ppt.Presentations.Open.return_value = mock_pres
        mock_dispatch.return_value = mock_ppt

        result = parse_ppt_with_win32com("test.ppt")

        self.assertIn("[幻灯片 1] 迪士尼乐园概述", result)
        self.assertIn("[幻灯片 2] 全球6个迪士尼乐园", result)
        mock_pres.Close.assert_called_once()
        mock_ppt.Quit.assert_called_once()

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp06_ppt_with_notes(self, mock_dispatch):
        """DP-06: 含备注的 .ppt 文件提取幻灯片文本及备注内容"""
        mock_ppt = MagicMock()
        mock_pres = MagicMock()

        mock_shape = MagicMock()
        mock_shape.HasTextFrame = True
        mock_shape.TextFrame.HasText = True
        mock_shape.TextFrame.TextRange.Text = "幻灯片正文"

        mock_notes_shape = MagicMock()
        mock_notes_shape.HasTextFrame = True
        mock_notes_shape.TextFrame.HasText = True
        mock_notes_shape.TextFrame.TextRange.Text = "备注内容"

        mock_slide = MagicMock()
        mock_slide.Shapes = [mock_shape, mock_notes_shape]

        mock_pres.Slides = [mock_slide]
        mock_ppt.Presentations.Open.return_value = mock_pres
        mock_dispatch.return_value = mock_ppt

        result = parse_ppt_with_win32com("notes_test.ppt")

        self.assertIn("幻灯片正文", result)
        self.assertIn("备注内容", result)

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp07_chinese_ppt_no_garbled(self, mock_dispatch):
        """DP-07: 含中文的 .ppt 文件正确提取中文，无乱码"""
        mock_ppt = MagicMock()
        mock_pres = MagicMock()

        mock_shape = MagicMock()
        mock_shape.HasTextFrame = True
        mock_shape.TextFrame.HasText = True
        mock_shape.TextFrame.TextRange.Text = "上海迪士尼度假区欢迎你"

        mock_slide = MagicMock()
        mock_slide.Shapes = [mock_shape]

        mock_pres.Slides = [mock_slide]
        mock_ppt.Presentations.Open.return_value = mock_pres
        mock_dispatch.return_value = mock_ppt

        result = parse_ppt_with_win32com("chinese_ppt.ppt")

        self.assertEqual(result, "[幻灯片 1] 上海迪士尼度假区欢迎你")

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_ppt_empty_slides_handled(self, mock_dispatch):
        """无文本的幻灯片应被跳过"""
        mock_ppt = MagicMock()
        mock_pres = MagicMock()

        mock_shape = MagicMock()
        mock_shape.HasTextFrame = True
        mock_shape.TextFrame.HasText = False

        mock_slide = MagicMock()
        mock_slide.Shapes = [mock_shape]

        mock_pres.Slides = [mock_slide]
        mock_ppt.Presentations.Open.return_value = mock_pres
        mock_dispatch.return_value = mock_ppt

        result = parse_ppt_with_win32com("empty_slide.ppt")

        self.assertEqual(result, "")


class TestExceptionHandling(unittest.TestCase):
    """测试用例 DP-08 到 DP-10：异常处理与降级逻辑"""

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp08_parse_failure_returns_none(self, mock_dispatch):
        """DP-08: .doc 解析失败时返回 None"""
        mock_dispatch.side_effect = Exception("COM error")

        result = parse_doc_with_win32com("broken.doc")

        self.assertIsNone(result)

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp09_ppt_parse_failure_returns_none(self, mock_dispatch):
        """DP-09: .ppt 解析失败时返回 None"""
        mock_dispatch.side_effect = Exception("COM error")

        result = parse_ppt_with_win32com("broken.ppt")

        self.assertIsNone(result)

    @patch('win32com_doc_ppt_parser.Dispatch')
    def test_dp10_no_office_prints_warning(self, mock_dispatch):
        """DP-10: 无 MS Office 时打印警告并返回 None"""
        from pywintypes import com_error
        mock_dispatch.side_effect = com_error(-1, "No COM object", None, 0)

        result = parse_doc_with_win32com("test.doc")

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
