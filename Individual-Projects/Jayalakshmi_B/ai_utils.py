import ollama
import pdfplumber
import pytesseract
from PIL import Image
import io

# ------------------- LLM Call -------------------
def call_llm(prompt, system_prompt="You are a professional AI Construction Engineer and Project Management Assistant."):
    """
    Send a prompt to Llama 3.2 and return the response.
    """
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"❌ Error: {str(e)}. Make sure Ollama is running (type 'ollama serve' in terminal)."

# ------------------- Document Text Extraction -------------------
def extract_text_from_pdf(file_bytes):
    """Extract all text from a PDF file."""
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_image(file_bytes):
    """Try Tesseract first, then EasyOCR as fallback."""
    text = ""
    try:
        from PIL import Image
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        if text.strip():
            return text
    except:
        pass

    # Fallback: EasyOCR
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)  # use CPU
        image = Image.open(io.BytesIO(file_bytes))
        result = reader.readtext(image, paragraph=True)
        text = "\n".join([item[1] for item in result])
        return text
    except:
        return ""
    
def extract_text_from_uploaded_file(uploaded_file):
    """
    Determine file type and extract text accordingly.
    Returns (extracted_text, error_message)
    """
    file_type = uploaded_file.type
    file_bytes = uploaded_file.read()  # read once
    
    if file_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
    elif file_type.startswith("image/"):
        text = extract_text_from_image(file_bytes)
    elif file_type == "text/plain":
        text = file_bytes.decode("utf-8")
    else:
        return None, "Unsupported file type. Please upload PDF, image, or TXT."
    
    if not text.strip():
        return None, "No text could be extracted from the file."
    
    return text, None