# -*- coding: utf-8 -*-
"""
迪士尼RAG API 服务
基于 FastAPI 提供查询接口，前端 Web 界面调用
"""
import os
import json
import sys
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio

sys.path.insert(0, os.path.dirname(__file__))
import importlib
_dq = importlib.import_module('5-disney_query')
load_index = _dq.load_index
get_text_embedding = _dq.get_text_embedding
detect_media_intent = _dq.detect_media_intent
search_by_intent = _dq.search_by_intent
_find_best_media = _dq._find_best_media
MEDIA_DISTANCE_THRESHOLD = _dq.MEDIA_DISTANCE_THRESHOLD

@asynccontextmanager
async def lifespan(app: FastAPI):
    index, metadata = load_index()
    app.state.index = index
    app.state.metadata = metadata
    yield

app = FastAPI(title="迪士尼RAG API", version="2.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class ResourceTag(BaseModel):
    type: str
    label: str

class ResourceDetailRequest(BaseModel):
    type: str
    label: str

def _prepare_context(index, metadata, question):
    """检索知识库并构建上下文，返回 (context_str, matched_image, matched_video, top_text_count)"""
    want_image, want_video = detect_media_intent(question)

    if want_image:
        results = search_by_intent(question, index, metadata, media_intent="image", text_k=20, media_k=5)
    elif want_video:
        results = search_by_intent(question, index, metadata, media_intent="video", text_k=20, media_k=5)
    else:
        query_vec = np.array([get_text_embedding(question)]).astype('float32')
        k = min(20, index.ntotal)
        distances, indices = index.search(query_vec, k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                break
            results.append({
                "idx": idx,
                "distance": dist,
                "metadata": metadata[idx],
            })

    media_threshold = MEDIA_DISTANCE_THRESHOLD * 2 if (want_image or want_video) else MEDIA_DISTANCE_THRESHOLD
    top_text = [r for r in results if r["metadata"]["type"] == "text"][:3]

    matched_image = _find_best_media(results, "image", media_threshold) if want_image else None
    matched_video = _find_best_media(results, "video", media_threshold) if want_video else None

    context_parts = []
    for i, r in enumerate(top_text):
        m = r["metadata"]
        context_parts.append(f"背景知识 {i+1} (来源: {m['source']}):\n{m['content']}")

    context_str = "\n\n".join(context_parts) if context_parts else "未找到相关背景知识。"

    tags = []
    if matched_image:
        tags.append({"type": "image", "label": matched_image["metadata"]["path"]})
    if matched_video:
        tags.append({"type": "video", "label": matched_video["metadata"]["url"]})
    if not tags:
        tags.append({"type": "text", "label": f"匹配 {len(top_text)} 条相关记录"})

    return context_str, tags, len(top_text)

def _stream_llm(prompt: str):
    """流式调用 LLM 生成回答，逐 token yield（纯 JSON payload，不含 SSE 前缀）"""
    import dashscope
    from http import HTTPStatus

    api_key = os.getenv("DASHSCOPE_API_KEY2")
    if not api_key:
        yield json.dumps({"token": "根据知识库检索，我找到了以下相关信息。"}, ensure_ascii=False)
        yield json.dumps({"done": True})
        return

    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    stream = client.chat.completions.create(
        model="qwen-flash",
        messages=[
            {"role": "system", "content": "你是一个迪士尼客服助手，专业、友好地回答用户问题。"},
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield json.dumps({"token": delta.content}, ensure_ascii=False)

    yield json.dumps({"done": True})

async def _async_generator(prompt: str):
    """将同步流式生成器转为异步"""
    loop = asyncio.get_event_loop()
    for chunk_str in _stream_llm(prompt):
        yield await loop.run_in_executor(None, lambda s=chunk_str: s)

@app.post("/api/ask/stream")
async def ask_question_stream(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    index = app.state.index
    metadata = app.state.metadata
    question = req.question

    context_str, tags, source_count = _prepare_context(index, metadata, question)

    prompt = f"""你是一个迪士尼客服助手。请根据以下背景知识回答用户问题。

[背景知识]
{context_str}

用户问题：{question}"""

    async def event_generator():
        meta = json.dumps({"tags": tags, "sourceCount": source_count}, ensure_ascii=False)
        yield f"data: {meta}\n\n"
        async for chunk_str in _async_generator(prompt):
            yield f"data: {chunk_str}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/resource/detail")
async def get_resource_detail(req: ResourceDetailRequest):
    """根据标签类型和标签返回资源详细内容"""
    if not req.type or not req.label:
        raise HTTPException(status_code=400, detail="类型和标签不能为空")

    metadata = app.state.metadata

    if req.type == "text":
        import re
        number_match = re.search(r'(\d+)\s*条', req.label)
        if number_match:
            expected_count = int(number_match.group(1))
        else:
            expected_count = 3
        text_records = [m for m in metadata if m["type"] == "text"]
        items = [
            {"content": m["content"], "source": m["source"]}
            for m in text_records[:expected_count]
        ]
        return {"items": items}

    elif req.type == "image":
        matched = [m for m in metadata if m["type"] == "image" and req.label in m.get("path", "")]
        if not matched:
            raise HTTPException(status_code=404, detail="未找到匹配的图片")
        items = [
            {"url": f"/static/images/{m['path']}", "path": m["path"], "content": m.get("content", "")}
            for m in matched
        ]
        return {"items": items}

    elif req.type == "video":
        matched = [m for m in metadata if m["type"] == "video" and req.label == m.get("url", "")]
        if not matched:
            raise HTTPException(status_code=404, detail="未找到匹配的视频")
        m = matched[0]
        items = [{"url": m["url"], "description": m.get("description", ""), "content": m.get("content", "")}]
        return {"items": items}

    else:
        raise HTTPException(status_code=400, detail=f"不支持的资源类型: {req.type}")


@app.post("/api/ask")
async def ask_question(req: QuestionRequest):
    """非流式接口（保留兼容）"""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    index = app.state.index
    metadata = app.state.metadata
    question = req.question

    context_str, tags, source_count = _prepare_context(index, metadata, question)

    prompt = f"""你是一个迪士尼客服助手。请根据以下背景知识回答用户问题。

[背景知识]
{context_str}

用户问题：{question}"""

    try:
        response = _call_llm_non_stream(prompt)
    except Exception:
        response = f"根据知识库检索，我找到了以下相关信息：\n\n{context_str}"

    return {
        "answer": response,
        "tags": tags,
        "sourceCount": source_count,
    }

def _call_llm_non_stream(prompt: str) -> str:
    """非流式 LLM 调用"""
    import dashscope
    from http import HTTPStatus

    api_key = os.getenv("DASHSCOPE_API_KEY2")
    if not api_key:
        return "根据知识库检索，我找到了以下相关信息。"

    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=[
            {"role": "system", "content": "你是一个迪士尼客服助手，专业、友好地回答用户问题。"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)