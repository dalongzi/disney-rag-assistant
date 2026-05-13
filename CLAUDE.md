# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

迪士尼 RAG 客服助手。解析知识库文档生成向量索引，用户查询时检索知识片段并调用 LLM 生成回答。

## 常用命令

```bash
./.venv/Scripts/python -m pip install -r requirements.txt   # 安装依赖
./.venv/Scripts/python 4-disney_build_index.py              # 构建索引
./.venv/Scripts/python 5-disney_query.py                    # 运行查询
```

## 环境变量

- `DASHSCOPE_API_KEY2` — DashScope API 密钥（必须设置）

## 架构

数据流：`文档解析 → 文本分块(500/50) → embedding → FAISS索引 → 查询检索 → LLM回答`

| 文件 | 职责 |
|------|------|
| `4-disney_build_index.py` | 索引构建：文档解析、分词、embedding、保存 FAISS 索引 |
| `5-disney_query.py` | 查询引擎：加载索引、检索、媒体意图检测、LLM 生成回答 |

关键配置：embedding 模型 `tongyi-embedding-vision-plus`，LLM `qwen-flash`，知识库目录 `迪士尼RAG知识库（完整）/`。

## 已知问题

1. `DOCS_DIR` 路径指向 `disney_knowledge_base`，实际目录是 `迪士尼RAG知识库（完整）`
2. 不递归子目录，知识库文件分布在 5 个子目录中
3. 仅支持 `.docx`，实际还有 `.doc`、`.pptx`、`.ppt`、`.pdf`、`.jpeg`
4. 查询使用 4 个硬编码测试用例，无交互模式
5. 完整规范见 `SPEC.md`

## 开发约定

遵循 TDD 红-绿-重构循环。
