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

## 关键文件

| 文件 | 职责 |
|------|------|
| `4-disney_build_index.py` | 索引构建：递归解析知识库、文档分块、多模态 embedding、保存 FAISS 索引 |
| `5-disney_query.py` | 查询引擎：加载索引、检索、媒体意图检测、LLM 生成回答 |
| `session-handoff.md` | 会话交接摘要：当前验证状态、本轮改动、已知问题、下一步建议 |
| `迪士尼RAG知识库（完整）/` | 知识库源文件 |

## 项目核心开发约定 (Core Development Protocols)

> **核心原则**：在编写任何业务代码前，必须无条件遵守以下两条“红线”规则。

##  强制开发流程

1. **严格执行 TDD (红-绿-重构)**
   - **禁止**直接编写功能实现代码。
   - **必须先写测试**：针对新需求或 Bug 修复，第一步必须是编写一个**会失败**的测试用例。
   - **最小化实现**：编写刚好能让测试通过的最简代码。
   - **重构**：在测试通过的前提下优化代码结构。

2. **绝对的测试隔离 (Zero Real API Calls)**
   - **严禁**在测试中调用真实的外部 API、数据库或第三方服务。
   - **强制 Mock**：所有外部依赖（HTTP 请求、DB 连接、文件系统）必须使用 Mock 或 Stub。
   - **目的**：确保测试运行速度极快，且绝不产生额外的 Token 消耗或费用。

---

##  上下文与行为准则

- **自我修正**：在输出代码块之前，请先在内心自省：“我是否先写了测试？我是否使用了 Mock？”如果答案是否定的，请重新生成。
- **错误处理**：如果生成的代码导致测试失败（非预期的失败），优先检查是否违反了上述 Mock 规则。
- **文档指引**：关于具体的测试框架语法或 Mock 库用法，请参考项目现有的测试文件，保持风格一致。