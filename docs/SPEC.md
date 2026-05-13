# 迪士尼 RAG 助手 — 功能规范 (SPEC)

## 1. 概述

构建一个基于命令行的迪士尼 RAG（检索增强生成）助手，用于客服场景的问答。系统从知识库文档中提取知识，通过向量检索匹配用户问题，调用大语言模型生成回答。

## 2. 系统架构

```
文档解析 → 文本切分 → Embedding → FAISS索引 → 用户查询 → 检索匹配 → LLM生成回答
```

三个核心模块：
- **索引构建模块** (`4-disney_build_index.py`)：解析文档、生成向量、保存索引
- **查询模块** (`5-disney_query.py`)：加载索引、检索匹配、生成回答
- **知识库目录** (`迪士尼RAG知识库（完整）/`)：存放原始文档

## 3. 文档解析模块

### 3.1 支持的格式

| 格式 | 扩展名 | 数量 | 解析方式 |
|------|--------|------|---------|
| Word文档(新版) | `.docx` | 34 | `python-docx` 段落迭代 + 表格解析 |
| Word文档(旧版) | `.doc` | 13 | `antiword` 命令行提取 |
| PPT演示文稿(新版) | `.pptx` | 4 | `python-pptx` 幻灯片文本 + 表格 + 备注 |
| PPT演示文稿(旧版) | `.ppt` | 5 | 旧版二进制格式，跳过并打印警告 |
| PDF文档 | `.pdf` | 4 | `pdfplumber` 逐页文本提取 |
| 图片 | `.jpeg` | 9 | `get_image_embedding` 多模态 embedding |

### 3.2 DOCX 解析规范（`.docx`）

#### 3.2.1 目录遍历
- 递归遍历 `迪士尼RAG知识库（完整）/` 目录及其所有子目录
- 跳过 `~$` 开头的 Office 临时文件
- 跳过隐藏文件（`.` 开头）
- 记录每个文件的相对路径作为 metadata

#### 3.2.2 段落提取
- 遍历 `docx.paragraphs`，提取每个段落的文本
- 跳过空白段落（`.strip()` 后为空）
- 保留段落原始顺序

#### 3.2.3 表格提取
- 遍历 `docx.tables`，将每个表格转为 Markdown 格式
- 表头行：`| 列1 | 列2 | ... |`
- 分隔行：`|---|---|---|`
- 数据行：`| 值1 | 值2 | ... |`
- 表格内单元格文本使用 `.strip()` 清理

#### 3.2.4 输出
- 段落和表格合并为一个完整文本字符串
- 段落之间用 `\n` 分隔
- 表格以 Markdown 格式插入在原文中的位置

### 3.3 DOC 解析规范（`.doc`，旧版二进制格式）

- 使用 `antiword -m UTF-8 <file>` 命令行工具提取文本
- 清理 antiword 产生的多余空行和表格占位符
- 如果 antiword 不可用或未安装，打印警告并跳过该文件
- 返回值：提取后的纯文本字符串

### 3.4 PPTX 解析规范（`.pptx`）

- 使用 `python-pptx` 库解析
- 遍历 `presentation.slides`，提取每张幻灯片的文本内容
- 提取幻灯片形状（`shape.text_frame`）中的文本
- 提取幻灯片中的表格内容（转为 Markdown 格式）
- 提取备注页文本（`notes_slide.notes_text_frame`）
- 输出格式：`[幻灯片 N] 内容...\n[备注] 备注内容`
- 段落之间用 `\n` 分隔

### 3.5 PPT 解析规范（`.ppt`，旧版二进制格式）

- 旧版二进制 PPT 格式无轻量解析工具
- 处理方式：跳过该文件，打印 `跳过: 旧版二进制PPT，暂不支持`
- 不抛出异常，继续处理其他文件

### 3.6 PDF 解析规范（`.pdf`）

- 使用 `pdfplumber` 库逐页提取文本
- 遍历 `pdf.pages`，调用 `page.extract_text()`
- 输出格式：`[第N页] 页面文本内容`
- 如果某页无文本内容，跳过该页
- 所有页面文本用 `\n` 分隔

### 3.7 图片处理规范（`.jpeg` / `.jpg` / `.png` / `.gif` / `.bmp`）

- 图片不参与文本解析，直接调用 `get_image_embedding()` 生成向量
- metadata 中记录 `"type": "image"`、`"path"`（相对路径）
- content 字段存储 `"[图片] 文件名"`

### 3.8 测试用例

| 编号 | 输入 | 预期行为 |
|------|------|---------|
| P-01 | 纯文本段落 docx | 正确提取所有非空段落 |
| P-02 | 包含表格的 docx | 表格转为 Markdown 格式 |
| P-03 | 子目录中的 docx | 递归找到并解析 |
| P-04 | 含空白段落的 docx | 跳过空白段落 |
| P-05 | ~$ 临时文件 | 跳过不处理 |
| P-06 | 空 docx 文件 | 返回空字符串，不报错 |
| P-07 | 旧版 .doc 文件 | antiword 提取文本，失败时打印警告 |
| P-08 | .pptx 文件 | 提取幻灯片文本 + 备注 |
| P-09 | 旧版 .ppt 文件 | 跳过并打印警告 |
| P-10 | .pdf 文件 | 逐页提取文本 |
| P-11 | .jpeg 图片 | 生成 image embedding，metadata 记录路径 |

## 4. 文本切分模块

### 4.1 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | 500 | 每个 chunk 的最大字符数 |
| `CHUNK_OVERLAP` | 50 | chunk 之间的重叠字符数 |

### 4.2 切分算法
- 按固定窗口滑动切分
- 起始位置 `start = 0`
- 每次取 `text[start : start + CHUNK_SIZE]`
- 下一次起始位置 `start = start + CHUNK_SIZE - CHUNK_OVERLAP`
- 跳过切分后 `.strip()` 为空的 chunk
- 最后一个 chunk 可能不足 `CHUNK_SIZE`

### 4.3 测试用例

| 编号 | 输入 | 预期行为 |
|------|------|---------|
| C-01 | 空字符串 | 返回空列表 `[]` |
| C-02 | 300字符文本 | 返回 1 个 chunk |
| C-03 | 600字符文本 | 返回 2 个 chunk，第二个 chunk 包含前一个的后50字符重叠 |
| C-04 | 1550字符文本 | 返回 4 个 chunk (500/500/500/50) |
| C-05 | 全是空白的文本 | 返回空列表 `[]` |

## 5. Embedding 模块

### 5.1 配置

| 配置项 | 值 |
|--------|-----|
| API Key 环境变量 | `DASHSCOPE_API_KEY2` |
| 模型 | `tongyi-embedding-vision-plus` |
| SDK | `dashscope.MultiModalEmbedding.call()` |

### 5.2 文本 Embedding
- 输入：切分后的文本 chunk
- 调用 `dashscope.MultiModalEmbedding.call(model='tongyi-embedding-vision-plus', input=[{'text': chunk}])`
- 输出：向量列表（第一个 embedding）
- 失败时抛出异常并打印错误信息

### 5.3 图片 Embedding
- 输入：本地图片文件路径
- 读取文件为 base64，格式化为 `data:image/{ext};base64,{base64_data}`
- jpg 扩展名转为 jpeg MIME 类型
- 调用 `dashscope.MultiModalEmbedding.call(model='tongyi-embedding-vision-plus', input=[{'image': image_data}])`
- 输出：向量列表

### 5.4 视频 Embedding
- 输入：视频 URL
- 调用 `dashscope.MultiModalEmbedding.call(model='tongyi-embedding-vision-plus', input=[{'video': url}])`
- 多帧 embedding 时取 `np.mean` 平均
- 单帧时直接返回
- 输出：向量列表

### 5.5 测试用例

| 编号 | 输入 | 预期行为 |
|------|------|---------|
| E-01 | 正常文本 | 返回固定维度的浮点向量 |
| E-02 | 空字符串 | API 返回错误，程序抛出异常 |
| E-03 | 本地图片路径 | 返回图片 embedding |
| E-04 | 视频 URL | 返回视频 embedding（多帧取平均） |
| E-05 | 未配置 API Key | 启动时提示错误并退出 |

## 6. FAISS 索引构建

### 6.1 索引类型
- `faiss.IndexFlatL2(dim)` — L2 距离的暴力搜索索引
- `dim` 从第一个向量的长度自动获取

### 6.2 Metadata 结构
每个条目包含：
```json
{
  "id": 0,
  "source": "相对/文件/路径.docx",
  "type": "text",
  "content": "chunk内容..."
}
```
图片条目额外包含 `"path"` 和 `"type": "image"`，视频条目包含 `"url"` 和 `"type": "video"`。

### 6.3 构建流程
1. 调用 `collect_all_files(DOCS_DIR)` 递归收集所有文件
2. 按类型依次处理：docx → doc(判断 magic bytes 选解析器) → pptx → ppt(跳过旧版) → pdf → 图片 → 视频
3. 每种类型生成向量后追加到 `all_vectors` 列表和 `metadata_store` 列表
4. 用 `np.array(all_vectors).astype('float32')` 创建 numpy 数组
5. `index.add(vectors)` 添加到 FAISS
6. `faiss.write_index(index, "disney_index.faiss")` 保存索引
7. `json.dump(metadata_store, ...)` 保存元数据到 `disney_metadata.json`

### 6.4 文件格式检测

对于 `.doc` 和 `.ppt` 文件，通过读取文件前 8 字节 magic bytes 判断实际格式：
- `PK` 开头（0x504B）→ OOXML 格式，可用对应库解析（`python-docx` / `python-pptx`）
- `d0cf11e0` 开头 → OLE2 旧版二进制格式，需特殊工具处理

### 6.5 测试用例

| 编号 | 场景 | 预期行为 |
|------|------|---------|
| I-01 | 正常构建 | 生成 `disney_index.faiss` 和 `disney_metadata.json` |
| I-02 | 空知识库 | 不生成索引文件，打印提示 |
| I-03 | 混合类型 | 索引中包含 text + image + video 向量 |
| I-04 | 重复构建 | 覆盖原有索引文件 |

## 7. 查询模块

### 7.1 加载索引
- 从 `disney_index.faiss` 加载 FAISS 索引
- 从 `disney_metadata.json` 加载元数据
- 文件不存在时提示错误

### 7.2 查询流程

#### 7.2.1 获取查询向量
- 使用与索引构建相同的 embedding 模型
- 对用户输入文本调用 `get_text_embedding(query)`

#### 7.2.2 向量检索
- `index.search(query_vector, k=len(metadata))` 检索全部条目
- 计算 L2 距离，按距离升序排序
- 打印 Top-20 相似度结果表格（ID、类型、来源、距离）

#### 7.2.3 媒体意图检测
- 图片关键词：`["图片", "海报", "照片", "看看", "长什么样", "图", "截图", "示意图"]`
- 视频关键词：`["视频", "录像", "影片", "看一下", "播放"]`
- 检测方式：用户查询中是否包含上述关键词

#### 7.2.4 结果选择
- **文本结果**：取 Top-k（默认 k=3）最近的文本条目作为 RAG 上下文
- **图片匹配**：在距离阈值 3.0 内找最近的 image 类型条目
- **视频匹配**：在距离阈值 3.0 内找最近的 video 类型条目

#### 7.2.5 LLM 生成回答
- **系统提示词**：迪士尼客服角色设定，要求基于提供的知识回答
- **模型**：`qwen-flash`（通过 DashScope 兼容 API 调用）
- **用户消息**：RAG prompt 模板，包含 Top-k 知识片段 + 用户问题
- 回答中附加匹配的图片和视频路径/URL

### 7.3 交互模式
- 启动后进入 `while True` 循环
- 提示用户输入问题：`"请输入问题: "`
- 输入空行时重新提示
- 输入 `quit`/`exit`/`q` 时退出
- 调用 `rag_ask(query, index, metadata, k=3)` 处理查询

### 7.4 测试用例

| 编号 | 查询类型 | 示例输入 | 预期行为 |
|------|---------|---------|---------|
| Q-01 | 纯文本 | "门票退款流程" | 返回 Top-3 文本 chunk + LLM 回答 |
| Q-02 | 图片意图 | "万圣节活动海报" | 返回文本回答 + 匹配图片路径 |
| Q-03 | 视频意图 | "汽车剐蹭视频" | 返回文本回答 + 匹配视频 URL |
| Q-04 | 无匹配结果 | "火星上的迪士尼" | 返回低相似度提示 + LLM 基于有限知识的回答 |
| Q-05 | 空输入 | "" | 重新提示输入 |
| Q-06 | 退出命令 | "quit" | 正常退出 |
| Q-07 | 索引不存在 | 未构建索引时查询 | 提示错误并退出 |

## 8. 项目结构

```
CASE-Disney-RAG-Assistant/
├── .venv/                              # Python虚拟环境
├── requirements.txt                    # 依赖清单
├── 4-disney_build_index.py             # 索引构建脚本
├── 5-disney_query.py                   # 查询脚本
├── disney_index.faiss                  # FAISS索引文件（生成）
├── disney_metadata.json                # 元数据文件（生成）
├── SPEC.md                             # 本规范文档
└── 迪士尼RAG知识库（完整）/              # 知识库目录
    ├── 1-产品与服务详情/
    ├── 2-运营流程与标准作业程序/
    ├── 3-特殊情况与应急预案/
    ├── 4-客户关系与支持话术/
    └── 5-内部知识与工具/
```

## 9. 依赖清单

| 包 | 用途 |
|----|------|
| `dashscope` | DashScope 多模态 embedding + LLM 调用 |
| `faiss_cpu` | FAISS 向量索引存储和检索 |
| `numpy` | 向量运算（平均值、数组转换） |
| `openai` | OpenAI 兼容 API 客户端（调用 DashScope chat） |
| `python_docx` | DOCX 文档解析 |
| `python-pptx` | PPTX 演示文稿解析 |
| `pdfplumber` | PDF 文档解析 |
| `antiword` | 旧版 .doc 文件文本提取（系统命令行工具，非 Python 包） |

## 10. 端到端测试流程

```
# 1. 安装依赖
./.venv/Scripts/python -m pip install -r requirements.txt

# 2. 安装 antiword（Windows 可用 Cygwin/MSYS2 版本，或跳过.doc 解析）
#    下载地址: http://www.winfield.demon.nl/

# 3. 构建索引
./.venv/Scripts/python 4-disney_build_index.py

# 4. 验证输出
#    检查 disney_index.faiss 和 disney_metadata.json 存在
#    检查 metadata 中文本/图片/视频条目数符合预期
#    预期: ~34 docx + ~13 doc(依赖antiword) + ~4 pptx + ~4 pdf(旧版ppt跳过) + ~9 jpeg

# 5. 启动查询
./.venv/Scripts/python 5-disney_query.py

# 6. 手动测试
#    输入 "迪士尼门票有哪几种" → 验证返回回答（命中docx）
#    输入 "迪士尼公司组织架构" → 验证返回回答（命中.doc）
#    输入 "万圣节海报" → 验证返回回答 + 图片路径
#    输入 "汽车剐蹭视频" → 验证返回回答 + 视频URL
#    输入 "quit" → 验证正常退出
```
