import ollama

MODEL_NAME = "llama3.2"

def ask_llama(user_prompt, system_prompt):

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        options={
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 700
        }
    )

    return response["message"]["content"]