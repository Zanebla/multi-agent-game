from openai import OpenAI
client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    # sk-xxx替换为自己的key
    api_key='sk-xxx'
)
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(completion.choices[0].message)
