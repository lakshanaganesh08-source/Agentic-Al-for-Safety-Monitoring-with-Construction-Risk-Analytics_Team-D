import streamlit as st
import base64

class UIComponents:
    """
    Houses reusable styling configurations, custom CSS styles, premium card generators, 
    and animated canvas backgrounds for the Construction Intelligence Hub.
    """
    
    @staticmethod
    def inject_global_css():
        """
        Injects custom, high-end CSS styling directly into the Streamlit app DOM
        to override defaults and build a futuristic glassmorphism UI.
        """
        css = """
        <style>
        /* Import Premium Typography */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset & Typography */
        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Outfit', sans-serif !important;
            color: #E2E8F0;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            color: #FFFFFF !important;
        }

        /* App Background Overrides */
        .stApp {
            background: transparent;
        }
        
        /* Custom Header Removal */
        header {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        #MainMenu {
            visibility: hidden;
        }

        /* Sidebar Styling Override */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 12, 22, 0.7) !important;
            backdrop-filter: blur(15px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #E2E8F0;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            position: relative;
            overflow: hidden;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border-color: rgba(77, 57, 233, 0.4) !important;
            box-shadow: 0 12px 40px 0 rgba(77, 57, 233, 0.15) !important;
        }

        /* Neon Border Highlight Card */
        .neon-card-blue {
            border-left: 4px solid #00B4D8 !important;
        }
        
        .neon-card-purple {
            border-left: 4px solid #8A2BE2 !important;
        }
        
        .neon-card-green {
            border-left: 4px solid #00F5D4 !important;
        }
        
        .neon-card-orange {
            border-left: 4px solid #FF9F1C !important;
        }

        /* Custom Input Fields Styling */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="number-input"] {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            transition: all 0.3s !important;
        }
        
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #00B4D8 !important;
            box-shadow: 0 0 10px rgba(0, 180, 216, 0.2) !important;
        }

        input {
            color: #FFFFFF !important;
        }

        label {
            color: #A0AEC0 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            margin-bottom: 5px !important;
        }

        /* Metric styling overrides */
        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #FFFFFF 0%, #A0AEC0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        [data-testid="stMetricLabel"] {
            color: #A0AEC0 !important;
            font-size: 0.85rem !important;
        }

        /* Premium Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4D39E9 0%, #00B4D8 100%) !important;
            border: none !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            padding: 12px 28px !important;
            border-radius: 30px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 15px rgba(77, 57, 233, 0.4) !important;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.9rem;
        }
        
        .stButton>button:hover {
            transform: scale(1.02) translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 180, 216, 0.6) !important;
            background: linear-gradient(135deg, #00B4D8 0%, #4D39E9 100%) !important;
        }
        
        .stButton>button:active {
            transform: scale(0.98);
        }

        /* Tabs styling */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            color: #A0AEC0 !important;
            font-weight: 500 !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.3s !important;
        }
        
        button[aria-selected="true"] {
            color: #00B4D8 !important;
            border-bottom-color: #00B4D8 !important;
            font-weight: 600 !important;
        }

        /* Chat area custom styles */
        .chat-msg {
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 10px;
            max-width: 80%;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        .chat-user {
            background: rgba(0, 180, 216, 0.15);
            border: 1px solid rgba(0, 180, 216, 0.3);
            margin-left: auto;
            color: #E2E8F0;
            border-bottom-right-radius: 2px;
        }
        .chat-ai {
            background: rgba(77, 57, 233, 0.15);
            border: 1px solid rgba(77, 57, 233, 0.3);
            margin-right: auto;
            color: #FFFFFF;
            border-bottom-left-radius: 2px;
        }

        /* Progress bars custom design */
        .stProgress > div > div > div > div {
            background: linear-gradient(to right, #4D39E9, #00B4D8) !important;
            border-radius: 10px !important;
        }
        
        /* Floating Button Container */
        .floating-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .floating-action-btn {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4D39E9 0%, #00B4D8 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 20px rgba(77, 57, 233, 0.5);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .floating-action-btn:hover {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 8px 30px rgba(0, 180, 216, 0.7);
        }

        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        
    @staticmethod
    def render_particles_background():
        """
        Renders an interactive animated canvas particles background
        that runs natively in the browser background behind the application layout.
        """
        canvas_html = """
        <canvas id="particles-canvas" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -100; pointer-events: none; background: radial-gradient(circle at 50% 50%, #100f23 0%, #040409 100%);"></canvas>
        <script>
            const canvas = document.getElementById('particles-canvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            const particles = [];
            const particleCount = 75;

            class Particle {
                constructor() {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.size = Math.random() * 2 + 0.5;
                    this.speedX = Math.random() * 0.3 - 0.15;
                    this.speedY = Math.random() * 0.3 - 0.15;
                    this.color = Math.random() > 0.5 ? 'rgba(77, 57, 233, ' + (Math.random() * 0.3 + 0.1) + ')' : 'rgba(0, 180, 216, ' + (Math.random() * 0.3 + 0.1) + ')';
                }

                update() {
                    this.x += this.speedX;
                    this.y += this.speedY;

                    if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
                    if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
                }

                draw() {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = Math.random() > 0.8 ? 10 : 0;
                    ctx.shadowColor = this.color;
                    ctx.fill();
                }
            }

            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle());
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                // Re-create background gradient dynamically
                let grad = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 0, canvas.width/2, canvas.height/2, canvas.width);
                grad.addColorStop(0, '#0e0b1f');
                grad.addColorStop(1, '#030307');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                for (let i = 0; i < particles.length; i++) {
                    particles[i].update();
                    particles[i].draw();
                    
                    // Draw micro-lines connecting nearby particles
                    for (let j = i + 1; j < particles.length; j++) {
                        const dx = particles[i].x - particles[j].x;
                        const dy = particles[i].y - particles[j].y;
                        const dist = Math.sqrt(dx*dx + dy*dy);
                        if (dist < 100) {
                            ctx.beginPath();
                            ctx.strokeStyle = 'rgba(77, 57, 233, ' + (0.05 * (1 - dist/100)) + ')';
                            ctx.lineWidth = 0.5;
                            ctx.moveTo(particles[i].x, particles[i].y);
                            ctx.lineTo(particles[j].x, particles[j].y);
                            ctx.stroke();
                        }
                    }
                }
                requestAnimationFrame(animate);
            }
            animate();
        </script>
        """
        # Embed the background using custom HTML container
        st.components.v1.html(canvas_html, height=0, width=0)

    @staticmethod
    def render_glass_card(content: str, title: str = "", card_type: str = "default"):
        """
        Creates a custom glassmorphism HTML structure inside Streamlit
        using Markdown rendering.
        """
        border_class = ""
        if card_type == "blue":
            border_class = "neon-card-blue"
        elif card_type == "purple":
            border_class = "neon-card-purple"
        elif card_type == "green":
            border_class = "neon-card-green"
        elif card_type == "orange":
            border_class = "neon-card-orange"
            
        header_html = f"<h3 style='margin-top:0;margin-bottom:15px;font-size:1.2rem;display:flex;align-items:center;'>{title}</h3>" if title else ""
        
        card_html = f"""
        <div class="glass-card {border_class}">
            {header_html}
            <div>{content}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    @staticmethod
    def get_hero_section():
        """
        Builds the animated premium Hero Title block.
        """
        hero_html = """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 40px; padding: 20px; border-radius: 20px; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03);">
            <h1 style="font-size: 3.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #FFFFFF 30%, #4D39E9 70%, #00B4D8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px rgba(77, 57, 233, 0.2);">
                🏗️ Construction Intelligence Hub
            </h1>
            <p style="font-size: 1.4rem; font-weight: 300; color: #A0AEC0; margin-bottom: 30px; letter-spacing: 0.05em;">
                "AI-Powered Smart Construction Planning & Space Optimization"
            </p>
        </div>
        """
        st.markdown(hero_html, unsafe_allow_html=True)

    @staticmethod
    def render_footer():
        """
        Renders the luxurious dark-mode footer showing the tech stack.
        """
        footer_html = """
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 50px; margin-bottom: 20px;">
        <div style="text-align: center; padding: 10px; font-size: 0.85rem; color: #718096; letter-spacing: 0.05em; line-height: 1.6;">
            Made with ❤️ using <br>
            <span style="color: #4D39E9; font-weight: 500;">Python</span> • 
            <span style="color: #00B4D8; font-weight: 500;">Streamlit</span> • 
            <span style="color: #00F5D4; font-weight: 500;">Plotly</span> • 
            <span style="color: #FF9F1C; font-weight: 500;">OpenCV</span> • 
            <span style="color: #E2E8F0; font-weight: 500;">Machine Learning</span> & 
            <span style="color: #FFFFFF; font-weight: 500; text-shadow: 0 0 10px rgba(255,255,255,0.3);">Artificial Intelligence</span>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)

    @staticmethod
    def render_floating_assistant():
        """
        Renders the premium floating AI assistant elements in HTML/CSS.
        These interface buttons simulate interactive AI controls.
        """
        floating_html = """
        <div class="floating-container">
            <div class="floating-action-btn" id="voice-assistant-btn" onclick="alert('🎙️ Voice Command activation triggered: Listening for vocal input parameters...')" title="Voice Assistant">
                🎙️
            </div>
            <div class="floating-action-btn" id="chat-assistant-btn" onclick="alert('🤖 AI Assistant opened. Please write your query in the Chatbot section!')" title="Chatbot Assistant">
                💬
            </div>
        </div>
        """
        st.markdown(floating_html, unsafe_allow_html=True)
