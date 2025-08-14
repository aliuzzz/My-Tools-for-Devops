from pathlib import Path
from openai import OpenAI


client = OpenAI(
    api_key="", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
    base_url="https://api.moonshot.cn/v1",
)

file_object = client.files.create(file=Path("daily_cacti_data.html"), purpose="file-extract")

file_content = client.files.content(file_id=file_object.id).text

messages = [
    {
        "role": "system",
        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
    },
    {
        "role": "system",
        "content": file_content, # <-- 这里，我们将抽取后的文件内容（注意是文件内容，而不是文件 ID）放置在请求中
    },
    {"role": "user", "content": "请解析 daily_cacti_data.html 文件的具体内容，并根据内容，总结哪些机房的哪些客户打峰，确定哪些客户的95值显著增加或减少，这里的“显著”可根据文件中数据的整体分布和变化幅度来判断，最后给出总结。总体字数不要太多，需要做到一目了然。"},
]

# 然后调用 chat-completion, 获取 Kimi 的回答
completion = client.chat.completions.create(
    model="kimi-k2-0711-preview",
    messages=messages,
    temperature=0.6,
)
md = completion.choices[0].message.content
with open("output.md", "w", encoding="utf-8") as f:
    f.write(md)
