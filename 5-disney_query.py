# -*- coding: utf-8 -*-
"""
迪士尼RAG助手 - 查询引擎

功能：加载FAISS索引，交互式查询，媒体意图检测，LLM生成回答
"""
import os
import json
import sys
import numpy as np
import faiss
import dashscope
from http import HTTPStatus
from openai import OpenAI

# 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY2")
if not DASHSCOPE_API_KEY:
    raise ValueError("错误：请设置 'DASHSCOPE_API_KEY2' 环境变量。")

dashscope.api_key = DASHSCOPE_API_KEY

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

MULTIMODAL_EMBEDDING_MODEL = "tongyi-embedding-vision-plus"
INDEX_FILE = "disney_index.faiss"
METADATA_FILE = "disney_metadata.json"

IMAGE_KEYWORDS = ["图片", "海报", "照片", "看看", "长什么样", "图", "截图", "示意图"]
VIDEO_KEYWORDS = ["视频", "录像", "影片", "看一下", "播放"]
MEDIA_DISTANCE_THRESHOLD = 3.0


def load_index():
    """加载FAISS索引和元数据"""
    if not os.path.exists(INDEX_FILE):
        print(f"错误：索引文件不存在: {INDEX_FILE}")
        print("请先运行 4-disney_build_index.py 构建索引。")
        sys.exit(1)
    if not os.path.exists(METADATA_FILE):
        print(f"错误：元数据文件不存在: {METADATA_FILE}")
        sys.exit(1)

    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print(f"已加载索引: {index.ntotal} 条记录")
    return index, metadata


def get_text_embedding(text):
    """文本embedding"""
    resp = dashscope.MultiModalEmbedding.call(
        model=MULTIMODAL_EMBEDDING_MODEL,
        input=[{'text': text}]
    )
    if resp.status_code != HTTPStatus.OK:
        raise Exception(f"Embedding失败: {resp.message}")
    return resp.output['embeddings'][0]['embedding']


def distance_to_similarity(distance):
    """L2距离转相似度 (0-1之间，越大越相似)"""
    return 1 / (1 + distance)


def detect_media_intent(query):
    """检测query中是否包含图片/视频意图"""
    query_lower = query.lower()
    want_image = any(kw in query_lower for kw in IMAGE_KEYWORDS)
    want_video = any(kw in query_lower for kw in VIDEO_KEYWORDS)
    return want_image, want_video


def search_all(query, index, metadata):
    """检索全部条目并打印Top-20相似度结果表格"""
    query_vec = np.array([get_text_embedding(query)]).astype('float32')
    distances, indices = index.search(query_vec, index.ntotal)

    print(f"\n相似度排名 Top-20 (越大越相似):")
    print("-" * 90)
    print(f"{'排名':4s} {'ID':4s} {'类型':6s} {'距离':8s} 来源")
    print("-" * 90)

    results = []
    for rank, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        if idx == -1 or rank >= 20:
            break
        m = metadata[idx]
        source = m.get('source', '')
        if len(source) > 40:
            source = source[:37] + "..."
        marker = ""
        if m['type'] == "image":
            marker = " [图片]"
        elif m['type'] == "video":
            marker = " [视频]"
        print(f"{rank+1:4d} {idx:4d} [{m['type']:5s}] {dist:8.4f}  {source}{marker}")
        results.append({"idx": idx, "distance": dist, "similarity": distance_to_similarity(dist), "metadata": m})

    return results


def rag_ask(query, index, metadata, k=3):
    """RAG问答"""
    results = search_all(query, index, metadata)

    want_image, want_video = detect_media_intent(query)

    top_text = [r for r in results if r["metadata"]["type"] == "text"][:k]

    matched_image = None
    if want_image:
        image_results = [r for r in results if r["metadata"]["type"] == "image" and r["distance"] < MEDIA_DISTANCE_THRESHOLD]
        if image_results:
            image_results.sort(key=lambda x: x["distance"])
            matched_image = image_results[0]
            print(f"\n  -> 匹配到图片: {matched_image['metadata']['path']} (距离: {matched_image['distance']:.4f})")

    matched_video = None
    if want_video:
        video_results = [r for r in results if r["metadata"]["type"] == "video" and r["distance"] < MEDIA_DISTANCE_THRESHOLD]
        if video_results:
            video_results.sort(key=lambda x: x["distance"])
            matched_video = video_results[0]
            print(f"\n  -> 匹配到视频: {matched_video['metadata']['url']} (距离: {matched_video['distance']:.4f})")

    context_parts = []
    for i, r in enumerate(top_text):
        m = r["metadata"]
        context_parts.append(f"背景知识 {i+1} (来源: {m['source']}):\n{m['content']}")

    context_str = "\n\n".join(context_parts) if context_parts else "未找到相关背景知识。"

    prompt = f"""你是一个迪士尼客服助手。请根据以下背景知识回答用户问题。如果背景知识不足以回答，请说明你不知道。

{context_str}

用户问题：{query}"""

    print("\n调用LLM生成答案...")
    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=[
            {"role": "system", "content": "你是一个迪士尼客服助手，专业、友好地回答用户问题。"},
            {"role": "user", "content": prompt}
        ]
    )
    answer = completion.choices[0].message.content

    if matched_image:
        answer += f"\n\n[相关图片]: {matched_image['metadata']['path']}"
    if matched_video:
        answer += f"\n\n[相关视频]: {matched_video['metadata']['url']}"

    print(f"\n{'='*60}")
    print(f"回答:")
    print(f"{'='*60}")
    print(answer)
    print(f"{'='*60}")
    return answer


def interactive_mode():
    """交互式查询模式"""
    print("=" * 60)
    print("迪士尼 RAG 助手 — 交互查询模式")
    print("输入问题后回车，输入 quit/exit/q 退出")
    print("=" * 60)

    index, metadata = load_index()

    while True:
        query = input("\n请输入问题: ").strip()
        if not query:
            continue
        if query.lower() in ('quit', 'exit', 'q'):
            print("再见！")
            break
        try:
            rag_ask(query, index, metadata, k=3)
        except Exception as e:
            print(f"查询出错: {e}")


if __name__ == "__main__":
    interactive_mode()
