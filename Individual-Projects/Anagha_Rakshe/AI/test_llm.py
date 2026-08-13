from llm import ask_llama

question = """
Suggest five safety precautions for workers on a high-rise construction site.
"""

answer = ask_llama(question)

print("\nResponse from Llama 3.2:\n")
print(answer)