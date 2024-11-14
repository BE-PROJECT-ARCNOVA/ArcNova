from huggingface_hub import InferenceClient

client = InferenceClient(api_key="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")

messages = [
	{
		"role": "user",
		"content": "How to deploy a website on EC2 with RDS as a database?"
	}
]

stream = client.chat.completions.create(
    model="microsoft/Phi-3.5-mini-instruct", 
	messages=messages, 
	max_tokens=500,
	stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")