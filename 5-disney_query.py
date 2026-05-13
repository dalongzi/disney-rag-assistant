# -*- coding: utf-8 -*-
"""
迪士尼RAG助手 - 查询引擎

功能：加载FAISS索引，交互式查询，媒体意图检测，LLM生成回答
"""
import os
import json
import sys
import re
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

MULTIMODAL_EMBEDDING_MODEL = "multimodal-embedding-v1"
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


def _make_result(idx, dist, metadata):
    """构建统一的检索结果字典"""
    return {
        "idx": idx,
        "distance": dist,
        "similarity": distance_to_similarity(dist),
        "metadata": metadata
    }


def detect_media_intent(query):
    """检测query中是否包含图片/视频意图"""
    query_lower = query.lower()
    want_image = any(kw in query_lower for kw in IMAGE_KEYWORDS)
    want_video = any(kw in query_lower for kw in VIDEO_KEYWORDS)
    return want_image, want_video


def _interleave_results(text_results, media_results):
    """交叉合并 text 和 media 结果，确保媒体结果在前排有固定曝光

    合并策略：第1条放最佳 media，之后每 3 条 text 穿插 1 条 media。
    例如：media[0], text[0], text[1], text[2], media[1], ...
    """
    merged = []
    ti, mi = 0, 0
    interval = 3
    text_count = 0

    if mi < len(media_results):
        merged.append(media_results[mi])
        mi += 1
    elif ti < len(text_results):
        merged.append(text_results[ti])
        ti += 1

    while ti < len(text_results) or mi < len(media_results):
        if text_count >= interval and mi < len(media_results):
            merged.append(media_results[mi])
            mi += 1
            text_count = 0
        elif ti < len(text_results):
            merged.append(text_results[ti])
            ti += 1
            text_count += 1
        elif mi < len(media_results):
            merged.append(media_results[mi])
            mi += 1

    return merged


def search_by_intent(query, index, metadata, media_intent=None, text_k=20, media_k=5):
    """按意图分类型独立检索，确保媒体类型被充分召回

    Args:
        query: 用户查询文本
        index: FAISS 索引
        metadata: 元数据列表
        media_intent: "image" / "video" / None
        text_k: text 类型的召回数量，默认 20
        media_k: media 类型的召回数量，默认 5

    Returns:
        合并后的结构化结果列表（按 distance 排序）
    """
    query_vec = np.array([get_text_embedding(query)]).astype('float32')
    distances, indices = index.search(query_vec, index.ntotal)

    text_results = []
    media_results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            break
        m = metadata[idx]
        result = _make_result(idx, dist, m)
        if m["type"] == "text":
            text_results.append(result)
        else:
            media_results.append(result)

    if media_intent in ("image", "video"):
        media_results.sort(key=lambda x: x["distance"])
        top_media = media_results[:media_k]
        text_results.sort(key=lambda x: x["distance"])
        top_text = text_results[:text_k]
        return _interleave_results(top_text, top_media)
    else:
        text_results.sort(key=lambda x: x["distance"])
        return text_results[:text_k]


def search_all(query, index, metadata, media_intent=None):
    """检索全部条目并打印相似度结果表格

    当有 media_intent 时，内部调用 search_by_intent 做分类型检索；
    否则保持原有的全量 Top-K 检索行为。
    """
    if media_intent:
        results = search_by_intent(query, index, metadata,
                                   media_intent=media_intent,
                                   text_k=20, media_k=5)
    else:
        query_vec = np.array([get_text_embedding(query)]).astype('float32')
        k = min(20, index.ntotal)
        distances, indices = index.search(query_vec, k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                break
            results.append(_make_result(idx, dist, metadata[idx]))

    print(f"\n相似度排名 Top-{len(results)} (越大越相似):")
    if media_intent:
        print(f"  [分类型检索: {media_intent}, text_k=20, media_k=5]")
    print("-" * 90)
    print(f"{'排名':4s} {'ID':4s} {'类型':6s} {'距离':8s} 来源")
    print("-" * 90)

    for rank, r in enumerate(results):
        m = r["metadata"]
        source = m.get('source', '')
        if len(source) > 40:
            source = source[:37] + "..."
        marker = ""
        if m['type'] == "image":
            marker = " [图片]"
        elif m['type'] == "video":
            marker = " [视频]"
        print(f"{rank+1:4d} {r['idx']:4d} [{m['type']:5s}] {r['distance']:8.4f}  {source}{marker}")

    return results


def _find_best_media(results, media_type, threshold):
    """从检索结果中找出指定类型且距离小于阈值的最优条目"""
    matched = [r for r in results if r["metadata"]["type"] == media_type and r["distance"] < threshold]
    matched.sort(key=lambda x: x["distance"])
    return matched[0] if matched else None


def rag_ask(query, index, metadata, k=3):
    """RAG问答"""
    want_image, want_video = detect_media_intent(query)
    print(f"\n意图检测: 需要图片={want_image}, 需要视频={want_video}")

    if want_image:
        results = search_all(query, index, metadata, media_intent="image")
    elif want_video:
        results = search_all(query, index, metadata, media_intent="video")
    else:
        results = search_all(query, index, metadata)

    media_threshold = MEDIA_DISTANCE_THRESHOLD * 2 if (want_image or want_video) else MEDIA_DISTANCE_THRESHOLD
    top_text = [r for r in results if r["metadata"]["type"] == "text"][:k]

    matched_image = _find_best_media(results, "image", media_threshold) if want_image else None
    if matched_image:
        print(f"\n  -> 匹配到图片: {matched_image['metadata']['path']} (距离: {matched_image['distance']:.4f})")

    matched_video = _find_best_media(results, "video", media_threshold) if want_video else None
    if matched_video:
        print(f"\n  -> 匹配到视频: {matched_video['metadata']['url']} (距离: {matched_video['distance']:.4f})")

    context_parts = []
    for i, r in enumerate(top_text):
        m = r["metadata"]
        context_parts.append(f"背景知识 {i+1} (来源: {m['source']}):\n{m['content']}")

    context_str = "\n\n".join(context_parts) if context_parts else "未找到相关背景知识。"

    prompt = f"""你是一个迪士尼客服助手。请根据以下背景知识回答用户问题。

[背景知识]
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
