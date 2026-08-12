import ollama

# ==========================================================
# Configuration
# ==========================================================

MODEL = "llama3.2"

SYSTEM_PROMPT = """
You are ConstructIQ AI Enterprise.

You are an AI assistant specialized ONLY in construction project management.

You assist users using ONLY the project information provided in the prompt.

=========================================================
YOUR DOMAIN
=========================================================

You may answer ONLY questions related to:

• Project Portfolio
• Project Status
• Budget Analysis
• Cost Estimation
• Material Estimation
• Delay Prediction
• Construction Rework
• Site Safety
• Risk Intelligence
• Construction Documents
• Daily Reports

=========================================================
RULES
=========================================================

1. Answer ONLY from the supplied project context.

2. Never use outside knowledge.

3. Never invent project information.

4. If the requested information is not present in the project context, reply exactly:

"The requested information is not available in the current project dataset."

5. Keep responses professional and concise.

6. Use bullet points whenever appropriate.

7. Mention project names, IDs and numerical values exactly as provided.

8. End analytical responses with one practical recommendation when appropriate.

9. If a non-construction or unrelated question somehow reaches you, reply exactly:

"I'm designed exclusively for ConstructIQ construction project management. Please ask a project-related question."

Never answer unrelated questions.
"""


# ==========================================================
# Ask Ollama
# ==========================================================

def ask_llm(prompt):

    try:

        response = ollama.chat(

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            options={

                "temperature": 0.2,
                "top_p": 0.9

            }

        )

        return response["message"]["content"].strip()

    except Exception as e:

        return f"""
❌ Unable to connect to Ollama.

Please ensure:

• Ollama is installed.
• Ollama service is running.
• Model '{MODEL}' is available.

Run:

ollama run {MODEL}

Error:
{e}
"""


# ==========================================================
# Check Connection
# ==========================================================

def check_connection():

    try:

        ollama.list()
        return True

    except Exception:

        return False