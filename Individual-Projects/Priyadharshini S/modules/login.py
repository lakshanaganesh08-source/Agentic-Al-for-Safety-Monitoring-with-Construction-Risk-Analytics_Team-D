import streamlit as st

# --- Demo credentials -------------------------------------------------------
# Swap this out for a real user store / hashed passwords / DB lookup later.
VALID_USERS = {
    "admin": "admin123",
    "user": "password123",
    "demo": "demo",
}


def _inject_login_css():
    st.markdown("""
        <style>
        /* Hide default streamlit chrome on the login screen for a cleaner look */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }

        @keyframes floatGlow {
            0%   { transform: translate(0px, 0px) scale(1); }
            50%  { transform: translate(20px, -25px) scale(1.08); }
            100% { transform: translate(0px, 0px) scale(1); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .login-orb-1 {
            position: fixed; top: -120px; left: -100px; width: 420px; height: 420px;
            background: radial-gradient(circle, rgba(0,229,255,0.35), transparent 70%);
            border-radius: 50%; filter: blur(10px);
            animation: floatGlow 10s ease-in-out infinite;
            z-index: 0; pointer-events: none;
        }
        .login-orb-2 {
            position: fixed; bottom: -140px; right: -100px; width: 480px; height: 480px;
            background: radial-gradient(circle, rgba(124,58,237,0.35), transparent 70%);
            border-radius: 50%; filter: blur(10px);
            animation: floatGlow 12s ease-in-out infinite reverse;
            z-index: 0; pointer-events: none;
        }

        .login-hero {
            animation: fadeInUp 0.7s ease-out;
            padding: 10px 10px 10px 4px;
        }

        .login-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.35);
            border-radius: 999px; padding: 6px 14px; font-size: 0.78rem; font-weight: 700;
            color: #00E5FF; letter-spacing: 0.5px; margin-bottom: 22px;
        }

        .login-hero h1 {
            font-size: 2.6rem !important; line-height: 1.15 !important;
            margin-bottom: 14px !important;
            background: linear-gradient(135deg, #FFFFFF 30%, #00E5FF 75%, #7C3AED 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .login-hero p.subtitle {
            color: #9BA6B4; font-size: 1.05rem; line-height: 1.6; max-width: 460px;
            margin-bottom: 28px;
        }

        .feature-row {
            display: flex; align-items: flex-start; gap: 14px;
            margin-bottom: 18px; animation: fadeInUp 0.9s ease-out;
        }
        .feature-icon {
            flex-shrink: 0; width: 42px; height: 42px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem;
            background: linear-gradient(135deg, rgba(0,229,255,0.18), rgba(124,58,237,0.18));
            border: 1px solid rgba(255,255,255,0.08);
        }
        .feature-text b { color: #F0F6FC; font-size: 0.95rem; display: block; margin-bottom: 2px; }
        .feature-text span { color: #8B949E; font-size: 0.82rem; }

        .login-card-wrap { animation: fadeInUp 0.8s ease-out; position: relative; z-index: 1; }

        .login-card {
            background: linear-gradient(180deg, rgba(22,27,34,0.9), rgba(13,17,23,0.9));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 36px 34px 28px 34px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.45), 0 0 0 1px rgba(0,229,255,0.05) inset;
            backdrop-filter: blur(20px);
        }

        .login-card-header { text-align: center; margin-bottom: 26px; }
        .login-card-header .logo-circle {
            width: 60px; height: 60px; margin: 0 auto 14px auto;
            border-radius: 16px;
            background: linear-gradient(135deg, #00E5FF 0%, #0088FF 50%, #7C3AED 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.7rem;
            box-shadow: 0 8px 24px rgba(0,229,255,0.35);
        }
        .login-card-header h3 { margin: 0 0 4px 0 !important; font-size: 1.35rem !important; }
        .login-card-header p { color: #8B949E; font-size: 0.88rem; margin: 0; }

        .stTextInput > div > div > input {
            background: #0D1117 !important;
        }

        .demo-creds {
            background: rgba(0, 229, 255, 0.06);
            border: 1px dashed rgba(0, 229, 255, 0.3);
            border-radius: 10px;
            padding: 12px 14px;
            margin-top: 18px;
            font-size: 0.78rem;
            color: #8B949E;
            text-align: center;
        }
        .demo-creds b { color: #00E5FF; }

        .login-footer {
            text-align: center; margin-top: 22px;
            color: #5C6673; font-size: 0.75rem;
        }
        </style>

        <div class="login-orb-1"></div>
        <div class="login-orb-2"></div>
    """, unsafe_allow_html=True)


def render():
    """Renders an attractive split-screen login experience."""
    _inject_login_css()

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    hero_col, form_col = st.columns([1.15, 1], gap="large")

    # ---------------- LEFT: Hero / Branding ----------------
    with hero_col:
        st.markdown("""
            <div class="login-hero">
                <span class="login-badge">🏗️ AI-POWERED CONSTRUCTION PLATFORM</span>
                <h1>Construction<br>Intelligence Hub</h1>
                <p class="subtitle">
                    Unify cost forecasting, delay-risk prediction, site safety monitoring,
                    and computer-vision inspection in one command center for your projects.
                </p>
            </div>
        """, unsafe_allow_html=True)

        features = [
            ("🤖", "AI Site Assistant", "Instant answers on codes, safety, and site operations"),
            ("📈", "Predictive Analytics", "Forecast costs and schedule delays before they happen"),
            ("👁️", "Computer Vision", "Automated PPE compliance and hazard detection"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
                <div class="feature-row">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-text">
                        <b>{title}</b>
                        <span>{desc}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ---------------- RIGHT: Login Card ----------------
    with form_col:
        st.markdown('<div class="login-card-wrap"><div class="login-card">', unsafe_allow_html=True)

        st.markdown("""
            <div class="login-card-header">
                <div class="logo-circle">🏗️</div>
                <h3>Welcome back</h3>
                <p>Sign in to access your project dashboard</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember = st.checkbox("Remember me on this device", value=True)
            submitted = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)

        if submitted:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("✅ Login successful — loading your dashboard...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")

        st.markdown("""
            <div class="demo-creds">
                <b>Demo credentials</b><br>
                admin / admin123 &nbsp;·&nbsp; user / password123 &nbsp;·&nbsp; demo / demo
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="login-footer">
                © 2026 Construction Intelligence Hub · Secure Access Portal
            </div>
        """, unsafe_allow_html=True)


def logout():
    """Clears auth-related session state and forces a rerun back to the login screen."""
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.rerun()
