# -*- coding: utf-8 -*-
"""
API 服务器测试 — 使用 Mock，不调用真实 API/DB/LLM
"""
import json
import os
import sys
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Mock FAISS 和 embedding 相关模块，必须在 import api_server 之前
mock_faiss = MagicMock()
mock_dashscope = MagicMock()
mock_numpy = MagicMock()
sys.modules['faiss'] = mock_faiss
sys.modules['dashscope'] = mock_dashscope
sys.modules['numpy'] = mock_numpy

# 模拟索引和元数据
MOCK_METADATA = [
    {"id": 0, "source": "test.txt", "type": "text", "content": "迪士尼门票价格：成人票 399 元，儿童票 299 元。"},
    {"id": 1, "source": "test.txt", "type": "text", "content": "快速通行证使用方法：第一步下载 App，第二步选择项目，第三步扫码入园。"},
    {"id": 2, "source": "test.txt", "type": "text", "content": "万圣节活动包括：夜间巡游、主题美食、限定周边。"},
    {"id": 10, "source": "images/万圣节.jpeg", "type": "image", "path": "images/万圣节.jpeg", "content": "[图片] 万圣节活动海报"},
    {"id": 11, "source": "images/烟花.jpeg", "type": "image", "path": "images/烟花.jpeg", "content": "[图片] 奇梦之光烟花秀"},
    {"id": 20, "source": "视频: 花车巡游", "type": "video", "url": "https://example.com/parade.mp4", "description": "花车巡游视频", "content": "[视频] 花车巡游"},
]

MOCK_INDEX = MagicMock()
MOCK_INDEX.ntotal = len(MOCK_METADATA)


@pytest.fixture
def client():
    """创建测试客户端，通过 sys.modules 注入 Mock"""
    # 清除已缓存的模块
    for mod_name in list(sys.modules.keys()):
        if mod_name in ('api_server', '5-disney_query'):
            del sys.modules[mod_name]

    # 直接替换 sys.modules 中的模块
    mock_dq = MagicMock()
    mock_dq.load_index.return_value = (MOCK_INDEX, MOCK_METADATA)
    mock_dq.get_text_embedding.return_value = [0.1] * 1024
    mock_dq.detect_media_intent.return_value = (False, False)
    mock_dq.search_by_intent.return_value = []
    mock_dq._find_best_media.return_value = None
    mock_dq.MEDIA_DISTANCE_THRESHOLD = 3.0
    sys.modules['5-disney_query'] = mock_dq

    import api_server
    api_server.app.state.index = MOCK_INDEX
    api_server.app.state.metadata = MOCK_METADATA

    return TestClient(api_server.app)


class TestResourceDetail:
    """测试 /api/resource/detail 端点"""

    def test_text_tag_returns_content_list(self, client):
        """text 类型标签应返回匹配的文本记录原文"""
        resp = client.post("/api/resource/detail", json={"type": "text", "label": "匹配 3 条相关记录"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) > 0
        assert "content" in data["items"][0]
        assert "source" in data["items"][0]

    def test_image_tag_returns_url(self, client):
        """image 类型标签应返回图片 URL"""
        resp = client.post("/api/resource/detail", json={"type": "image", "label": "images/万圣节.jpeg"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert "url" in data["items"][0]
        assert "path" in data["items"][0]

    def test_video_tag_returns_url(self, client):
        """video 类型标签应返回视频 URL"""
        resp = client.post("/api/resource/detail", json={"type": "video", "label": "https://example.com/parade.mp4"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert "url" in data["items"][0]
        assert "description" in data["items"][0]

    def test_unknown_type_returns_error(self, client):
        """未知类型应返回 400"""
        resp = client.post("/api/resource/detail", json={"type": "audio", "label": "test.mp3"})
        assert resp.status_code == 400

    def test_empty_label_returns_error(self, client):
        """空标签应返回 400"""
        resp = client.post("/api/resource/detail", json={"type": "text", "label": ""})
        assert resp.status_code == 400

    def test_text_not_found_returns_empty(self, client):
        """找不到匹配的文本记录应返回空列表"""
        resp = client.post("/api/resource/detail", json={"type": "text", "label": "匹配 0 条相关记录"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []

    def test_image_not_found_returns_error(self, client):
        """找不到匹配的图片应返回 404"""
        resp = client.post("/api/resource/detail", json={"type": "image", "label": "not_exist.jpeg"})
        assert resp.status_code == 404

    def test_video_not_found_returns_error(self, client):
        """找不到匹配的视频应返回 404"""
        resp = client.post("/api/resource/detail", json={"type": "video", "label": "https://not.exist/video.mp4"})
        assert resp.status_code == 404
