# 会话交接摘要

## 当前已验证

- `4-disney_build_index.py` 索引构建成功（mock embedding），生成 404 条记录（394 文本 + 9 图片 + 1 视频）
- `5-disney_query.py` 语法检查通过
- `disney_index.faiss` 和 `disney_metadata.json` 已生成
- 知识库目录递归遍历正确，5 个子目录全部覆盖
- `.doc` 文件 magic bytes 检测生效（OOXML 格式用 python-docx 解析，OLE2 格式用 win32com）
- `.ppt` 文件 win32com 解析生效（使用 `WithWindow=False` 替代 `Visible=False`）
- 12 个单元测试全部通过（`tests/test_win32com_parsers.py`）

## 本轮改动

| 文件 | 改动 |
|------|------|
| `requirements.txt` | 新增 `pywin32==306` |
| `win32com_doc_ppt_parser.py` | **新增模块**：`parse_doc_with_win32com()` + `parse_ppt_with_win32com()` |
| `tests/test_win32com_parsers.py` | **新增**：12 个单元测试，覆盖 .doc/.ppt 正常解析、中文、表格、异常处理 |
| `4-disney_build_index.py` | 导入 win32com 解析器，`.doc` OLE2 优先 win32com + antiword 降级，`.ppt` OLE2 使用 win32com |
| `CLAUDE.md` | 更新 `.doc`/`.ppt` 解析方式和已知限制 |
| `docs/DOC_PPT_PARSING_SPEC.md` | 精简为单一方案文档（win32com） |

## 仍损坏或未验证

- **部分 .doc OLE2 文件 win32com 失败**：如 `迪士尼动画大全.doc` 报错 `Word.Application.Quit`，降级到 antiword 后仍因 antiword 未安装而跳过
- **部分 .ppt 文件 win32com 失败**：某些 .ppt 文件在 mock 环境下能解析，真实 COM 调用可能仍有问题
- **PDF 解析**：部分 PDF 文件曾出现过错误（控制台输出有乱码），但不影响索引构建完成
- **真实端到端构建未验证**：因禁止调用真实 API，使用 mock 验证，未实际调用 embedding API

## 下一步最佳动作

1. 安装 antiword（如需完整解析旧版 .doc 文件）
2. 设置 `DASHSCOPE_API_KEY2` 环境变量，运行真实端到端构建验证
3. 验证 `python 5-disney_query.py` 交互查询模式

## 常用命令

```bash
# 安装依赖
./.venv/Scripts/python -m pip install -r requirements.txt

# 运行单元测试
./.venv/Scripts/python -m unittest tests.test_win32com_parsers -v

# 构建索引（需设置 DASHSCOPE_API_KEY2）
./.venv/Scripts/python 4-disney_build_index.py

# 交互查询
./.venv/Scripts/python 5-disney_query.py
```
