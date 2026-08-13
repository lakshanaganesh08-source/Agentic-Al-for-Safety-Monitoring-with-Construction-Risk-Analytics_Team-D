import time
import json
import threading
import urllib.parse
import hashlib
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from ollama import Client

# Constants
OLLAMA_HOST = "http://localhost:11434"
CONNECTION_TIMEOUT = 3.0
GENERATE_TIMEOUT = 90.0

# Initialize the official Ollama client with a custom timeout to prevent hangs
client = Client(host=OLLAMA_HOST, timeout=GENERATE_TIMEOUT)

def log_error(msg: str):
    """
    Logs errors to stderr and a local file for visibility.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] ERROR: {msg}\n"
    sys.stderr.write(log_msg)
    sys.stderr.flush()
    try:
        with open("ollama_integration.log", "a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass

def log_debug(msg: str):
    """
    Logs debug info to stdout and local log file for step-by-step tracing.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] DEBUG: {msg}\n"
    sys.stdout.write(log_msg)
    sys.stdout.flush()
    try:
        with open("ollama_integration.log", "a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass

# Cache state variables to prevent redundant connections
_connection_status_cached = None
_connection_status_time = 0.0

_model_status_cache = {}

def check_connection() -> tuple[bool, str]:
    """
    Checks if Ollama service is reachable. (Cached for 30 seconds to prevent overhead)
    """
    global _connection_status_cached, _connection_status_time
    now = time.time()
    if _connection_status_cached is not None and (now - _connection_status_time) < 30.0:
        return _connection_status_cached
        
    try:
        import httpx
        r = httpx.get(f"{OLLAMA_HOST}/", timeout=CONNECTION_TIMEOUT)
        if r.status_code == 200:
            _connection_status_cached = (True, "")
            _connection_status_time = now
            return _connection_status_cached
        _connection_status_cached = (False, f"Unexpected response status: {r.status_code}")
        _connection_status_time = now
        return _connection_status_cached
    except Exception as e:
        # Don't cache failure status long-term to allow immediate recovery
        _connection_status_cached = None
        return False, f"Ollama service offline on {OLLAMA_HOST}. {str(e)}"

def check_model(model_name: str = 'llama3.2') -> tuple[bool, str]:
    """
    Verifies if the specified model is pulled and ready. (Cached for 60 seconds)
    """
    global _model_status_cache
    now = time.time()
    if model_name in _model_status_cache:
        status, err, cache_time = _model_status_cache[model_name]
        if (now - cache_time) < 60.0:
            return status, err
            
    connected, conn_err = check_connection()
    if not connected:
        return False, conn_err
    try:
        models_response = client.list()
        # models_response is a ListResponse object, its models attribute is a list of Model objects
        models = getattr(models_response, 'models', [])
        for m in models:
            name = getattr(m, 'model', '')
            if model_name in name:
                _model_status_cache[model_name] = (True, "", now)
                return True, ""
        err_msg = f"Model '{model_name}' not found. Run 'ollama pull {model_name}'."
        _model_status_cache[model_name] = (False, err_msg, now)
        return False, err_msg
    except Exception as e:
        return False, f"Failed to list local models: {str(e)}"

def send_prompt(
    prompt: str,
    model_name: str = 'llama3.2',
    temperature: float = 0.3,
    num_predict: int = 250,
    num_ctx: int = 2048,
    json_format: bool = False,
    timeout: float = GENERATE_TIMEOUT,
    retries: int = 1
) -> tuple[str, str]:
    """
    Sends a structured query using a dynamically-timeouted client, with configurable automatic retries.
    """
    available, model_err = check_model(model_name)
    if not available:
        return "", model_err

    options = {
        "temperature": temperature,
        "num_predict": num_predict,
        "num_ctx": num_ctx
    }
    
    # Try retries + 1 times
    for attempt in range(retries + 1):
        try:
            req_client = Client(host=OLLAMA_HOST, timeout=timeout)
            kwargs = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "options": options,
                "keep_alive": "30m"
            }
            if json_format:
                kwargs["format"] = "json"
                
            response = req_client.chat(**kwargs)
            content = response.get("message", {}).get("content", "")
            if content.strip():
                return content, ""
            raise ValueError("Empty response received.")
        except Exception as e:
            log_error(f"Attempt {attempt + 1} failed in send_prompt: {str(e)}")
            if attempt < retries:
                time.sleep(1.0)
                continue
            return "", f"⚠️ Couldn't reach local AI. (Error: {str(e)})"

def send_prompt_stream(
    messages: list,
    model_name: str = 'llama3.2',
    temperature: float = 0.3,
    num_predict: int = 300,
    num_ctx: int = 2048
):
    """
    Streams a response chunk-by-chunk using the official client, with one automatic retry.
    """
    available, model_err = check_model(model_name)
    if not available:
        log_error(f"send_prompt_stream failed: Model unavailable - {model_err}")
        yield f"⚠️ Local LLM Offline: {model_err}"
        return

    options = {
        "temperature": temperature,
        "num_predict": num_predict,
        "num_ctx": num_ctx
    }

    start_time = time.time()
    log_debug(f"Starting stream query for model '{model_name}' with {len(messages)} messages...")

    success = False
    for attempt in range(2):
        try:
            stream = client.chat(
                model=model_name,
                messages=messages,
                options=options,
                stream=True,
                keep_alive="30m"
            )
            chunk_count = 0
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    chunk_count += 1
                    yield content
            elapsed = time.time() - start_time
            log_debug(f"Stream finished successfully in {elapsed:.2f}s across {chunk_count} chunks.")
            success = True
            break
        except Exception as e:
            log_error(f"Attempt {attempt + 1} failed in send_prompt_stream: {str(e)}")
            if attempt == 0:
                time.sleep(1.0)
                continue
            yield f"⚠️ Stream connection failed. (Error: {str(e)})"
            
    if not success:
        log_error("Streaming completely failed after 2 attempts.")

def get_recommendation(inputs: dict) -> tuple[str, str]:
    """
    Generates a structured engineering report.
    """
    prompt = f"""
You are a senior civil engineer. 
Analyze the specs and generate a highly concise design overview (under 150 words total).

### Land Details:
- Total Land Area: {inputs.get('total_area')} sq ft
- Plot Dimensions: {inputs.get('width')} ft wide x {inputs.get('length')} ft long
- Location: {inputs.get('location')}

### Project Specifications:
- Number of Residents: {inputs.get('family_size')}
- Target Floor Profile: {inputs.get('floor_pref')}
- Base Style: {inputs.get('construction_type')}
- Material Tier: {inputs.get('material_quality')}
- Parking Space: {"Required" if inputs.get('parking_needed') else "None"}
- Landscape Garden: {"Required" if inputs.get('garden_needed') else "None"}
- Expansion Option: {"Enabled" if inputs.get('future_expansion') else "Disabled"}

Format output exactly with these headers:
### Recommendation
### Reasoning
### Advantages
### Possible Limitations
### Construction Suggestions
### Additional Observations
"""
    return send_prompt(prompt, temperature=0.3, num_predict=250, timeout=30.0, retries=0)

def get_recommendation_cached(inputs: dict) -> tuple[str, str]:
    """
    Loads cached recommendation from disk, or requests and caches new ones.
    Rounds input dimensions to optimize cache hit rate.
    """
    rounded_width = round(float(inputs.get("width", 40)) / 10) * 10
    rounded_length = round(float(inputs.get("length", 60)) / 10) * 10
    rounded_inputs = {
        "total_area": rounded_width * rounded_length,
        "length": rounded_length,
        "width": rounded_width,
        "location": inputs.get("location", "Urban Core"),
        "floor_pref": inputs.get("floor_pref", "Single Floor"),
        "family_size": inputs.get("family_size", 4),
        "construction_type": inputs.get("construction_type", "Smart/Futuristic"),
        "material_quality": inputs.get("material_quality", "Premium"),
        "parking_needed": inputs.get("parking_needed", True),
        "garden_needed": inputs.get("garden_needed", True),
        "future_expansion": inputs.get("future_expansion", False)
    }
    try:
        serialized = json.dumps(rounded_inputs, sort_keys=True)
        cache_hash = hashlib.md5(serialized.encode('utf-8')).hexdigest()
        cache_dir = "templates/cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{cache_hash}.txt")
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read(), ""
    except Exception as e:
        log_error(f"Cache read error: {str(e)}")

    resp, err = get_recommendation(rounded_inputs)
    if not err and resp:
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(resp)
        except Exception as e:
            log_error(f"Cache write error: {str(e)}")
            
    return resp, err

def get_safety_fallback(inputs: dict) -> str:
    """
    Returns a dynamic, parameter-specific fallback JSON for safety precautions.
    """
    location = inputs.get('location', 'Urban Core')
    house_type = inputs.get('houseType', 'Duplex')
    expansion = inputs.get('expansion')
    
    safeties = [
        "Ensure all site workers wear Level 1 PPE (Hard hats, steel-toe boots, reflective vests).",
        "Erect barricades and safety netting around the plot perimeter to protect adjacent structures."
    ]
    if "Duplex" in house_type or "Villa" in house_type:
        safeties.append("Install double-stage scaffolding with safety harnesses for all masonry and plastering works above 10 feet.")
    if expansion:
        safeties.append("Clearly mark starter bar extension zones to avoid impalement hazards (use protective cap fittings).")
    
    if location == "Coastal District":
        safeties.append("Implement high-salinity corrosion mitigation and soil stabilization protocols during excavation.")
    elif location == "Mountain Terrain":
        safeties.append("Install temporary retaining walls or shoring to prevent soil sliding and rockfalls during excavation.")
    elif location == "Urban Core":
        safeties.append("Establish strict noise control barriers and schedule heavy concrete pours during approved municipal hours.")
    else:
        safeties.append("Designate a secure material storage yard away from overhead power lines.")
        
    return json.dumps({"safety": safeties})

def get_safety_cached(inputs: dict) -> tuple[str, str]:
    """
    Retrieves safety precautions from cache, or generates them with a short timeout.
    Falls back to a dynamic rule-based response if offline or timed out.
    """
    location = inputs.get('location', 'Urban Core')
    width = round(float(inputs.get('width', 40)) / 10) * 10
    length = round(float(inputs.get('length', 60)) / 10) * 10
    house_type = inputs.get('houseType', 'Duplex')
    built_area = round(float(inputs.get('builtArea', 1700)) / 100) * 100
    budget = round(float(inputs.get('budget', 5000000)) / 500000) * 500000
    expansion = "Enabled" if inputs.get('expansion') else "Disabled"
    
    rounded_inputs = {
        "location": location,
        "width": width,
        "length": length,
        "house_type": house_type,
        "built_area": built_area,
        "budget": budget,
        "expansion": expansion
    }
    
    try:
        serialized = json.dumps(rounded_inputs, sort_keys=True)
        cache_hash = hashlib.md5(serialized.encode('utf-8')).hexdigest()
        cache_dir = "templates/cache/safety"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{cache_hash}.json")
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read(), ""
    except Exception as e:
        log_error(f"Safety cache read error: {str(e)}")
        
    from utils.prompts import PROMPT_SAFETY
    prompt = PROMPT_SAFETY.format(
        location=location,
        width=width,
        length=length,
        house_type=house_type,
        built_area=built_area,
        budget=budget,
        expansion=expansion
    )
    
    # 4.0-second timeout to keep the UI snappy
    resp, err = send_prompt(prompt, temperature=0.3, num_predict=350, json_format=True, timeout=4.0, retries=0)
    
    if err or not resp:
        log_debug(f"Safety generation timed out or failed. Returning dynamic safety fallback.")
        fallback = get_safety_fallback(inputs)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(fallback)
        except Exception as e:
            log_error(f"Safety cache write error (fallback): {str(e)}")
        return fallback, ""
        
    # Verify it is valid JSON
    try:
        json.loads(resp)
        # Cache it
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(resp)
        except Exception as e:
            log_error(f"Safety cache write error: {str(e)}")
        return resp, ""
    except Exception:
        log_debug("Safety LLM response was not valid JSON, returning fallback.")
        return get_safety_fallback(inputs), ""

def get_risks_fallback(inputs: dict) -> str:
    """
    Returns a dynamic, parameter-specific fallback JSON for design risks.
    """
    location = inputs.get('location', 'Urban Core')
    house_type = inputs.get('houseType', 'Duplex')
    budget = float(inputs.get('budget', 5000000))
    built_area = float(inputs.get('builtArea', 1700))
    expansion = inputs.get('expansion')
    
    risks = []
    
    # Budget risk
    est_cost = built_area * 3500 * 1.3
    if est_cost > budget:
        risks.append({
            "title": "Budget Deficit Risk",
            "reason": f"Projected construction cost (₹{est_cost/100000:.1f}L) exceeds your budget (₹{budget/100000:.1f}L) by ~{int((est_cost-budget)/budget*100)}%."
        })
    else:
        risks.append({
            "title": "Material Escalation Risk",
            "reason": "Fluctuations in steel and cement prices could increase estimated structural costs by 8-12%."
        })
        
    # Location risk
    if location == "Coastal District":
        risks.append({
            "title": "High Moisture & Saline Corrosion",
            "reason": "Saline air accelerates steel reinforcement oxidation, requiring epoxy-coated rebars."
        })
    elif location == "Mountain Terrain":
        risks.append({
            "title": "Slope Instability Hazard",
            "reason": "Significant excavation on sloped terrain risks landslide unless shoring pile foundation is used."
        })
    elif location == "Urban Core":
        risks.append({
            "title": "Access & Logistic Constraints",
            "reason": "Narrow urban street boundaries limit heavy transit access for concrete transit mixers."
        })
    else:
        risks.append({
            "title": "Subsurface Soil Variability",
            "reason": "Lack of detailed geotechnical reports could lead to unexpected foundation settlement."
        })
        
    # Expansion risk
    if expansion:
        risks.append({
            "title": "Foundation Stress Overload",
            "reason": "Future vertical expansion requires reinforced structural pillars to handle future load stresses."
        })
    else:
        risks.append({
            "title": "Lack of Vertical Flexibility",
            "reason": "Single-floor design optimization prevents any future vertical addition without structural reinforcement."
        })
        
    return json.dumps({"risks": risks})

def get_risks_cached(inputs: dict) -> tuple[str, str]:
    """
    Retrieves design risks from cache, or generates them with a short timeout.
    Falls back to a dynamic rule-based response if offline or timed out.
    """
    location = inputs.get('location', 'Urban Core')
    width = round(float(inputs.get('width', 40)) / 10) * 10
    length = round(float(inputs.get('length', 60)) / 10) * 10
    house_type = inputs.get('houseType', 'Duplex')
    built_area = round(float(inputs.get('builtArea', 1700)) / 100) * 100
    budget = round(float(inputs.get('budget', 5000000)) / 500000) * 500000
    expansion = "Enabled" if inputs.get('expansion') else "Disabled"
    
    rounded_inputs = {
        "location": location,
        "width": width,
        "length": length,
        "house_type": house_type,
        "built_area": built_area,
        "budget": budget,
        "expansion": expansion
    }
    
    try:
        serialized = json.dumps(rounded_inputs, sort_keys=True)
        cache_hash = hashlib.md5(serialized.encode('utf-8')).hexdigest()
        cache_dir = "templates/cache/risks"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{cache_hash}.json")
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read(), ""
    except Exception as e:
        log_error(f"Risks cache read error: {str(e)}")
        
    from utils.prompts import PROMPT_RISKS
    prompt = PROMPT_RISKS.format(
        location=location,
        width=width,
        length=length,
        house_type=house_type,
        built_area=built_area,
        budget=budget,
        expansion=expansion
    )
    
    # 4.0-second timeout to keep the UI snappy
    resp, err = send_prompt(prompt, temperature=0.3, num_predict=350, json_format=True, timeout=4.0, retries=0)
    
    if err or not resp:
        log_debug(f"Risks generation timed out or failed. Returning dynamic risks fallback.")
        fallback = get_risks_fallback(inputs)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(fallback)
        except Exception as e:
            log_error(f"Risks cache write error (fallback): {str(e)}")
        return fallback, ""
        
    # Verify it is valid JSON
    try:
        json.loads(resp)
        # Cache it
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(resp)
        except Exception as e:
            log_error(f"Risks cache write error: {str(e)}")
        return resp, ""
    except Exception:
        log_debug("Risks LLM response was not valid JSON, returning fallback.")
        return get_risks_fallback(inputs), ""

def get_chat_response_stream(query: str, context: dict = None, doc_context: str = None, history: list = None):
    """
    Prepares chat context and returns streaming assistant turns.
    """
    global _active_doc_chunks
    if _active_doc_chunks and not doc_context:
        try:
            from utils.document_parser import retrieve_relevant_chunks
            doc_context = retrieve_relevant_chunks(query, _active_doc_chunks, top_n=2)
        except Exception as e:
            log_error(f"Failed to retrieve doc chunks: {str(e)}")

    from utils.prompts import PROMPT_CHATBOT

    messages = [{"role": "system", "content": PROMPT_CHATBOT}]

    context_str = ""
    if context:
        raw = context.get('raw_inputs', {})
        est_cost = context.get('estimated_cost')
        budget_val = raw.get('budget')
        try:
            est_cost_formatted = f"{int(float(est_cost)):,}" if est_cost is not None else "0"
        except Exception:
            est_cost_formatted = str(est_cost) if est_cost is not None else "0"
        try:
            budget_formatted = f"{int(float(budget_val)):,}" if budget_val is not None else "0"
        except Exception:
            budget_formatted = str(budget_val) if budget_val is not None else "0"

        context_str += f"""Active Project Specifications:
- Layout Option: {context.get('suitable_type', 'N/A')}
- Plot Dimensions: {raw.get('width', 'N/A')} ft x {raw.get('length', 'N/A')} ft (Total Area: {raw.get('total_area', 'N/A')} sq ft)
- Construction Style: {raw.get('construction_type', 'N/A')}
- Material Quality Tier: {raw.get('material_quality', 'N/A')}
- Estimated Build Cost: ₹{est_cost_formatted}
- Project Budget: ₹{budget_formatted}
- Safety Index Score: {context.get('safety_score', 'N/A')}%
- Parking Space: {"Required" if raw.get('parking_needed') else "Not Needed"}
- Green Garden: {"Required" if raw.get('garden_needed') else "Not Needed"}
- Future Vertical Expansion: {"Enabled" if raw.get('future_expansion') else "Disabled"}
- Location Zone: {raw.get('location', 'Urban Core')}
"""
    if doc_context:
        context_str += f"\nUploaded Document Excerpts:\n{doc_context}\n"

    if context_str:
        messages.append({
            "role": "system", 
            "content": f"You MUST ground your answers in the following project context:\n{context_str}"
        })

    # Limit turns to last 6 turns (3 exchanges)
    if history:
        for turn in history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": turn.get("content", "")})

    messages.append({"role": "user", "content": query})
    return send_prompt_stream(messages, temperature=0.3, num_predict=300)

def get_chat_response(query: str, context: dict = None, doc_context: str = None, history: list = None) -> tuple[str, str]:
    try:
        chunks = []
        for chunk in get_chat_response_stream(query, context, doc_context, history):
            chunks.append(chunk)
        full_text = "".join(chunks)
        if full_text.startswith("⚠️"):
            return "", full_text
        return full_text, ""
    except Exception as e:
        return "", f"Error assembling chat: {str(e)}"

# --- Background HTTP API Server ---
_active_doc_chunks = None
_active_doc_name = None

class ChatAPIRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/chat':
            query_params = urllib.parse.parse_qs(parsed_url.query)
            query = query_params.get('q', [''])[0]
            response, err = get_chat_response(query)
            if err:
                response = f"⚠️ Local LLM Offline: {err}"
                
            response_bytes = json.dumps({"response": response}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_bytes)
            
        elif parsed_url.path == '/clear_doc':
            global _active_doc_chunks, _active_doc_name
            _active_doc_chunks = None
            _active_doc_name = None
            
            response_bytes = json.dumps({"success": True}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_bytes)
            
        elif parsed_url.path == '/projects/list':
            try:
                query_params = urllib.parse.parse_qs(parsed_url.query)
                user_id = int(query_params.get('user_id', ['0'])[0])
                from db_manager import DBManager
                projects = DBManager.get_user_projects(user_id)
                response_bytes = json.dumps({"success": True, "projects": projects}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        elif parsed_url.path == '/download':
            try:
                query_params = urllib.parse.parse_qs(parsed_url.query)
                download_type = query_params.get('type', ['pdf'])[0]
                
                width = float(query_params.get('width', ['40'])[0])
                length = float(query_params.get('length', ['60'])[0])
                occupants = int(query_params.get('occupants', ['4'])[0])
                parking = query_params.get('parking', ['true'])[0].lower() == 'true'
                garden = query_params.get('garden', ['true'])[0].lower() == 'true'
                expansion = query_params.get('expansion', ['true'])[0].lower() == 'true'
                budget = float(query_params.get('budget', ['5000000'])[0])
                location = query_params.get('location', ['Urban Core'])[0]
                
                from utils.analysis_engine import AnalysisEngine
                data = AnalysisEngine.analyze_construction(
                    total_area=width*length,
                    length=length,
                    width=width,
                    location=location,
                    budget=budget,
                    construction_type="Smart/Futuristic",
                    material_quality="Premium",
                    parking_needed=parking,
                    garden_needed=garden,
                    future_expansion=expansion,
                    floor_pref="Duplex" if occupants > 2 else "Single Floor",
                    family_size=occupants
                )
                data['raw_inputs']['budget'] = budget
                
                # Fetch recommendation (cached or fall back)
                inputs = {
                    "total_area": width * length,
                    "length": length,
                    "width": width,
                    "location": location,
                    "budget": budget,
                    "construction_type": "Smart/Futuristic",
                    "material_quality": "Premium",
                    "parking_needed": parking,
                    "garden_needed": garden,
                    "future_expansion": expansion,
                    "floor_pref": "Duplex" if occupants > 2 else "Single Floor",
                    "family_size": occupants
                }
                
                ollama_resp, err = get_recommendation_cached(inputs)
                if not err and ollama_resp:
                    # Parse and extract insights
                    lines = [line.strip().replace('**', '').replace('*', '') for line in ollama_resp.split('\n') if line.strip()]
                    valid_insights = []
                    current_section = ""
                    for line in lines:
                        if line.startswith('###'):
                            current_section = line.replace('###', '').strip()
                        elif line.startswith('-') or line.startswith('•'):
                            cleaned_line = line.lstrip('-• ').strip()
                            if len(cleaned_line) > 10:
                                valid_insights.append(f"{current_section}: {cleaned_line}" if current_section else cleaned_line)
                        elif len(line) > 20 and not line.startswith('#'):
                            valid_insights.append(f"{current_section}: {line}" if current_section else line)
                    if valid_insights:
                        data['insights'] = valid_insights[:6]
                        
                if download_type == 'pdf':
                    from utils.pdf_generator import PDFGenerator
                    file_data = PDFGenerator.generate_report(data)
                    mime_type = "application/pdf"
                    filename = "Construction_Intelligence_Report.pdf"
                else:
                    from utils.excel_generator import ExcelGenerator
                    file_data = ExcelGenerator.generate_report(data)
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    filename = "Construction_Intelligence_Ledger.xlsx"
                    
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(file_data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(file_data)
            except Exception as e:
                log_error(f"Download API failed: {str(e)}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"Error generating download: {str(e)}".encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def do_POST(self):
        global _active_doc_chunks, _active_doc_name
        parsed_url = urllib.parse.urlparse(self.path)
        
        if parsed_url.path == '/upload':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                filename = data.get('filename')
                file_data_b64 = data.get('file_data')
                
                import base64
                file_bytes = base64.b64decode(file_data_b64)
                
                from utils.document_parser import extract_text_from_file, chunk_text
                text = extract_text_from_file(filename, file_bytes)
                chunks = chunk_text(text)
                
                _active_doc_chunks = chunks
                _active_doc_name = filename
                
                summary = ""
                if text.strip():
                    from utils.prompts import PROMPT_DOCUMENT
                    summary_prompt = f"{PROMPT_DOCUMENT}\n\nDocument Name: {filename}\nContent:\n{text[:4000]}"
                    summary, err = send_prompt(summary_prompt, temperature=0.3, num_predict=250)
                    if err:
                        summary = f"Indexed successfully ({len(chunks)} chunks). Could not query model for summary: {err}"
                else:
                    summary = "The document was empty."
                
                response_bytes = json.dumps({
                    "success": True,
                    "filename": filename,
                    "chunks_count": len(chunks),
                    "summary": summary
                }).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                log_error(f"Upload handler failed: {str(e)}")
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
                
        elif parsed_url.path == '/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                query = data.get('query', '')
                project_data = data.get('project_data', None)
                history = data.get('history', None)
                
                context = None
                if project_data:
                    context = {
                        "suitable_type": project_data.get("houseType"),
                        "estimated_cost": project_data.get("estimatedCost"),
                        "safety_score": project_data.get("safetyScore", 95),
                        "raw_inputs": {
                            "width": project_data.get("width"),
                            "length": project_data.get("length"),
                            "total_area": project_data.get("width", 0) * project_data.get("length", 0),
                            "construction_type": project_data.get("constructionType"),
                            "material_quality": project_data.get("materialQuality"),
                            "parking_needed": project_data.get("parking"),
                            "garden_needed": project_data.get("garden"),
                            "future_expansion": project_data.get("expansion"),
                            "budget": project_data.get("budget"),
                            "location": project_data.get("location")
                        }
                    }
                
                doc_context = None
                if _active_doc_chunks:
                    try:
                        from utils.document_parser import retrieve_relevant_chunks
                        doc_context = retrieve_relevant_chunks(query, _active_doc_chunks, top_n=2)
                    except Exception as e:
                        log_error(f"Retrieval error: {str(e)}")
                    
                stream_requested = data.get('stream', False) or self.headers.get('Accept') == 'text/event-stream'
                
                if stream_requested:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Connection', 'close')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.close_connection = True
                    
                    try:
                        for chunk in get_chat_response_stream(query, context, doc_context, history):
                            self.wfile.write(f"data: {json.dumps({'chunk': chunk})}\n\n".encode('utf-8'))
                            self.wfile.flush()
                    except Exception as e:
                        log_error(f"Error in chat stream write: {str(e)}")
                        try:
                            self.wfile.write(f"data: {json.dumps({'chunk': f'⚠️ Error: {str(e)}'})}\n\n".encode('utf-8'))
                            self.wfile.flush()
                        except Exception:
                            pass
                else:
                    response, err = get_chat_response(query, context, doc_context, history)
                    if err:
                        response = f"⚠️ Local LLM Offline: {err}"
                        
                    response_bytes = json.dumps({"response": response}).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(response_bytes)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response_bytes)
            except Exception as e:
                log_error(f"Chat POST handler failed: {str(e)}")
                response_bytes = json.dumps({"error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
                
        elif parsed_url.path == '/safety':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                response_text, err = get_safety_cached(data)
                
                response_bytes = response_text.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                log_error(f"Safety handler failed: {str(e)}")
                fallback_text = get_safety_fallback(data if 'data' in locals() else {})
                response_bytes = fallback_text.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
                
        elif parsed_url.path == '/risks':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                response_text, err = get_risks_cached(data)
                
                response_bytes = response_text.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                log_error(f"Risks handler failed: {str(e)}")
                fallback_text = get_risks_fallback(data if 'data' in locals() else {})
                response_bytes = fallback_text.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        elif parsed_url.path == '/auth/signup':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                from db_manager import DBManager
                user_info, err = DBManager.register_user(
                    username=data.get('username', ''),
                    email=data.get('email', ''),
                    password=data.get('password', ''),
                    confirm_password=data.get('confirm_password', '')
                )
                if err:
                    response_bytes = json.dumps({"success": False, "error": err}).encode('utf-8')
                else:
                    response_bytes = json.dumps({"success": True, "user": user_info}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        elif parsed_url.path == '/auth/login':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                from db_manager import DBManager
                user_info, err = DBManager.login_user(
                    username_or_email=data.get('username', ''),
                    password=data.get('password', '')
                )
                if err:
                    response_bytes = json.dumps({"success": False, "error": err}).encode('utf-8')
                else:
                    response_bytes = json.dumps({"success": True, "user": user_info}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        elif parsed_url.path == '/projects/save':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                from db_manager import DBManager
                project_id, err = DBManager.save_project(
                    user_id=data.get('user_id'),
                    project_name=data.get('project_name', 'Untitled Project'),
                    structure_type=data.get('structure_type', 'house'),
                    plot_data=data.get('plot_data', {})
                )
                if err:
                    response_bytes = json.dumps({"success": False, "error": err}).encode('utf-8')
                else:
                    response_bytes = json.dumps({"success": True, "project_id": project_id}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        elif parsed_url.path == '/projects/delete':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                from db_manager import DBManager
                ok = DBManager.delete_user_project(
                    project_id=data.get('project_id'),
                    user_id=data.get('user_id')
                )
                response_bytes = json.dumps({"success": ok}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                response_bytes = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_bytes)

        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

# Server instance
_api_server_instance = None
_server_lock = threading.Lock()
_active_port = 8502

def get_active_port():
    global _active_port
    return _active_port

def start_background_server():
    """
    Launches a dedicated daemon thread serving LLM prompts on localhost:8502.
    """
    global _api_server_instance
    with _server_lock:
        if _api_server_instance is not None:
            return
            
        def run():
            global _api_server_instance, _active_port
            for port in [8502, 8503, 8504]:
                try:
                    server = ThreadingHTTPServer(('0.0.0.0', port), ChatAPIRequestHandler)
                    _api_server_instance = server
                    _active_port = port
                    
                    try:
                        with open('templates/port.json', 'w') as f:
                            json.dump({"port": port}, f)
                    except Exception:
                        pass
                        
                    server.serve_forever()
                    break
                except Exception:
                    continue
                    
        t = threading.Thread(target=run, daemon=True)
        t.start()
