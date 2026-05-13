#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dashscope
import json
import os
from http import HTTPStatus

dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY2")

text = "上海迪士尼乐园门票分为一日票、两日票和特定日票三种类型。一日票可在购买时选定日期使用，价格根据季节浮动，平日成人票475元起"
input = [{'text': text}]
# 调用模型接口
resp = dashscope.MultiModalEmbedding.call(
    model="tongyi-embedding-vision-plus",
    input=input
)

if resp.status_code == HTTPStatus.OK:
    result = {
        "status_code": resp.status_code,
        "request_id": getattr(resp, "request_id", ""),
        "code": getattr(resp, "code", ""),
        "message": getattr(resp, "message", ""),
        "output": resp.output,
        "usage": resp.usage
    }
    print(json.dumps(result, ensure_ascii=False, indent=4))
else:
    print(f"请求失败: status_code={resp.status_code}")
    print(f"code={resp.code}, message={resp.message}")

