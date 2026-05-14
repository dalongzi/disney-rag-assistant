# -*- coding: utf-8 -*-
"""
迪士尼RAG助手 - Web API 服务（前后端合并部署）

提供 SSE 流式 RAG 问答 + 资源详情 API + 前端静态文件托管
"""
import os
import json
import re
import uuid
import time
import numpy as np
import faiss
import dashscope
from http import HTTPStatus
from openai import OpenAI
from flask import Flask, request, jsonify, Response, send_from_directory

app = Flask(__name__, static_folder="disney-web/dist", static_url_path="")

# 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is required.")

dashscope.api_key = DASHSCOPE_API_KEY

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

MULTIMODAL_EMBEDDING_MODEL = "multimodal-embedding-v1"
BASE_DIR = os.path.dirname(__file__)
INDEX_FILE = os.path.join(BASE_DIR, "disney_index.faiss")
METADATA_FILE = os.path.join(BASE_DIR, "disney_metadata.json")

IMAGE_KEYWORDS = ["图片", "海报", "照片", "看看", "长什么样", "图", "截图", "示意图"]
VIDEO_KEYWORDS = ["视频", "录像", "影片", "看一下", "播放"]
MEDIA_DISTANCE_THRESHOLD = 3.0

# 全局索引缓存
_index = None
_metadata = None


def load_index():
    """加载FAISS索引和元数据"""
    global _index, _metadata
    if _index is not None:
        return _index, _metadata
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(f"索引文件不存在: {INDEX_FILE}")
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"元数据文件不存在: {METADATA_FILE}")

    _index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        _metadata = json.load(f)
    print(f"已加载索引: {_index.ntotal} 条记录")
    return _index, _metadata


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
    """L2距离转相似度"""
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
    """交叉合并 text 和 media 结果"""
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
    """按意图分类型独立检索"""
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
    """检索全部条目"""
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
    return results


def _find_best_media(results, media_type, threshold):
    """从检索结果中找出指定类型且距离小于阈值的最优条目"""
    matched = [r for r in results if r["metadata"]["type"] == media_type and r["distance"] < threshold]
    matched.sort(key=lambda x: x["distance"])
    return matched[0] if matched else None


def _build_context_and_tags(query, index, metadata, k=3):
    """构建上下文、标签和完整 prompt（供流式和非流式共用）"""
    want_image, want_video = detect_media_intent(query)

    if want_image:
        results = search_all(query, index, metadata, media_intent="image")
    elif want_video:
        results = search_all(query, index, metadata, media_intent="video")
    else:
        results = search_all(query, index, metadata)

    media_threshold = MEDIA_DISTANCE_THRESHOLD * 2 if (want_image or want_video) else MEDIA_DISTANCE_THRESHOLD
    top_text = [r for r in results if r["metadata"]["type"] == "text"][:k]

    matched_image = _find_best_media(results, "image", media_threshold) if want_image else None
    matched_video = _find_best_media(results, "video", media_threshold) if want_video else None

    # 构建资源标签
    tags = []
    for r in top_text:
        m = r["metadata"]
        tags.append({"type": "text", "label": m.get("source", "")})
    if matched_image:
        tags.append({"type": "image", "label": matched_image["metadata"].get("path", "")})
    if matched_video:
        tags.append({"type": "video", "label": matched_video["metadata"].get("url", "")})

    # 构建 prompt
    context_parts = []
    for i, r in enumerate(top_text):
        m = r["metadata"]
        context_parts.append(f"背景知识 {i+1} (来源: {m['source']}):\n{m['content']}")

    context_str = "\n\n".join(context_parts) if context_parts else "未找到相关背景知识。"

    prompt = f"""你是一个迪士尼客服助手。请根据以下背景知识回答用户问题。

[背景知识]
{context_str}

用户问题：{query}"""

    return prompt, tags, top_text, matched_image, matched_video


# ==================== API 路由 ====================


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


@app.route("/api/ask/stream", methods=["POST"])
def ask_stream():
    """SSE 流式 RAG 问答接口

    请求体: {"question": "..."}
    输出: SSE 事件流 (data: {token/prompt/contextItems/done})
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "缺少 question 参数"}), 400

    question = data["question"].strip()
    if not question:
        return jsonify({"error": "question 不能为空"}), 400

    try:
        index, metadata = load_index()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    def generate():
        try:
            prompt, tags, top_text, matched_image, matched_video = _build_context_and_tags(
                question, index, metadata, k=3
            )

            # 发送资源标签
            yield f"data: {json.dumps({'tags': tags, 'sourceCount': len([t for t in top_text])}, ensure_ascii=False)}\n\n"

            # 发送上下文条目（用于 ResourceDetail 展示）
            context_items = [
                {"metadata": {"source": r["metadata"]["source"], "content": r["metadata"]["content"]}}
                for r in top_text
            ]
            if matched_image:
                context_items.append({
                    "metadata": {
                        "type": "image",
                        "path": matched_image["metadata"]["path"],
                        "url": matched_image["metadata"].get("url", ""),
                        "content": matched_image["metadata"].get("content", ""),
                    }
                })
            if matched_video:
                context_items.append({
                    "metadata": {
                        "type": "video",
                        "url": matched_video["metadata"]["url"],
                        "description": matched_video["metadata"].get("description", ""),
                        "content": matched_video["metadata"].get("content", ""),
                    }
                })
            yield f"data: {json.dumps({'contextItems': context_items}, ensure_ascii=False)}\n\n"

            # 发送完整 prompt（开发模式可用）
            yield f"data: {json.dumps({'prompt': prompt}, ensure_ascii=False)}\n\n"

            # 流式调用 LLM
            completion = client.chat.completions.create(
                model="qwen-flash",
                messages=[
                    {"role": "system", "content": "你是一个迪士尼客服助手，专业、友好地回答用户问题。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

            # 添加媒体链接到回答末尾
            if matched_image:
                img_text = f"\n\n[相关图片]: {matched_image['metadata']['path']}"
                yield f"data: {json.dumps({'token': img_text}, ensure_ascii=False)}\n\n"
            if matched_video:
                vid_text = f"\n\n[相关视频]: {matched_video['metadata']['url']}"
                yield f"data: {json.dumps({'token': vid_text}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/resource/detail", methods=["POST"])
def resource_detail():
    """资源详情接口

    请求体: {"type": "text|image|video", "label": "..."}
    返回: {"items": [{"content": "...", "source": "..."}, ...]}
    """
    data = request.get_json()
    if not data or "type" not in data or "label" not in data:
        return jsonify({"error": "缺少 type 或 label 参数"}), 400

    res_type = data["type"]
    label = data["label"]

    try:
        index, metadata = load_index()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    items = []

    if res_type == "text":
        # 查找匹配的文本条目
        for m in metadata:
            if m.get("source") == label and m.get("type") == "text":
                items.append({"content": m["content"], "source": m["source"]})

    elif res_type == "image":
        for m in metadata:
            if m.get("type") == "image" and m.get("path") == label:
                items.append({
                    "url": m.get("url", ""),
                    "path": m["path"],
                    "content": m.get("content", ""),
                })

    elif res_type == "video":
        for m in metadata:
            if m.get("type") == "video" and m.get("url") == label:
                items.append({
                    "url": m["url"],
                    "description": m.get("description", ""),
                    "content": m.get("content", ""),
                })

    return jsonify({"items": items})


@app.route("/api/ask", methods=["POST"])
def ask():
    """非流式 RAG 问答接口（兼容旧版）"""
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "缺少 query 参数"}), 400

    query = data["query"].strip()
    k = data.get("k", 3)

    if not query:
        return jsonify({"error": "query 不能为空"}), 400

    try:
        index, metadata = load_index()
        prompt, tags, top_text, matched_image, matched_video = _build_context_and_tags(
            query, index, metadata, k=k
        )

        completion = client.chat.completions.create(
            model="qwen-flash",
            messages=[
                {"role": "system", "content": "你是一个迪士尼客服助手，专业、友好地回答用户问题。"},
                {"role": "user", "content": prompt}
            ]
        )
        answer = completion.choices[0].message.content

        result = {
            "answer": answer,
            "tags": tags,
            "sourceCount": len(top_text),
        }

        if matched_image:
            result["answer"] += f"\n\n[相关图片]: {matched_image['metadata']['path']}"
        if matched_video:
            result["answer"] += f"\n\n[相关视频]: {matched_video['metadata']['url']}"

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 静态文件 ====================


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """前端构建产物托管：SPA 路由回退到 index.html"""
    dist_dir = app.static_folder
    if dist_dir and os.path.exists(dist_dir):
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        return send_from_directory(dist_dir, "index.html")
    return jsonify({"error": "前端未构建，请先运行 cd disney-web && npm run build"}), 404


if __name__ == "__main__":
    load_index()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
