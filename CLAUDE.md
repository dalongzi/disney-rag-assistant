# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

迪士尼 RAG 客服助手。解析知识库文档生成向量索引，用户查询时检索知识片段并调用 LLM 生成回答。

## 常用命令

```bash
./.venv/Scripts/python -m pip install -r requirements.txt   # 安装依赖
./.venv/Scripts/python 4-disney_build_index.py              # 构建索引
./.venv/Scripts/python 5-disney_query.py                    # 运行交互查询
```

## 环境变量

- `DASHSCOPE_API_KEY2` — DashScope API 密钥（必须设置）

## 架构

数据流：`文档解析 → 文本分块(500/50) → embedding → FAISS索引 → 查询检索 → LLM回答`

| 文件 | 职责 |
|------|------|
| `4-disney_build_index.py` | 索引构建：递归解析知识库、文档分块、多模态 embedding、保存 FAISS 索引 |
| `5-disney_query.py` | 查询引擎：加载索引、检索、媒体意图检测、LLM 生成回答 |
| `session-handoff.md` | 会话交接摘要：当前验证状态、本轮改动、已知问题、下一步建议 |

关键配置：embedding 模型 `tongyi-embedding-vision-plus`，LLM `qwen-flash`，知识库目录 `迪士尼RAG知识库（完整）/`。

## 知识库结构

```
迪士尼RAG知识库（完整）/
├── 1-产品与服务详情/          # 37 文件
├── 2-运营流程与标准作业程序/   # 6 文件
├── 3-特殊情况与应急预案/       # 1 文件
├── 4-客户关系与支持话术/       # 1 文件
└── 5-内部知识与工具/           # 17 文件
```

## 文档解析支持格式

| 格式 | 解析方式 | 备注 |
|------|---------|------|
| `.docx` | `python-docx` 段落+表格 | 主格式 |
| `.doc` | magic bytes 检测 → OOXML 用 `python-docx`，OLE2 用 `win32com` → 降级 antiword | 需安装 MS Office，antiword 为降级选项 |
| `.pptx` | `python-pptx` 幻灯片+表格+备注 | |
| `.ppt` | magic bytes 检测 → OOXML 用 `python-pptx`，OLE2 用 `win32com` | 需安装 MS Office |
| `.pdf` | `pdfplumber` 逐页提取 | |
| `.jpeg/.jpg/.png/.gif/.bmp` | `get_image_embedding` 多模态 | |
| 视频 | `get_video_embedding` URL | 硬编码在 `VIDEO_KNOWLEDGE` |

## 已知限制

1. **win32com 需 MS Office**：`.doc`/`.ppt` OLE2 格式依赖 MS Office COM 组件，无 Office 时降级到 antiword 或跳过
2. **视频库硬编码**：`VIDEO_KNOWLEDGE` 仅包含 1 条测试视频
3. **索引文件在 gitignore 中**：`*.faiss` 已忽略，每次需重新构建

## 开发约定

1. **TDD**：新功能先写失败测试，再写实现，遵循 TDD 红-绿-重构循环。
2. **测试隔离**：禁止调用真实的 API，使用 Mock，避免造成额外的 token 消耗。
