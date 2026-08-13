"""
Unified Enterprise Authentication Module for Construction Intelligence Hub.

Provides a single, secure login & registration interface with real SQLite
database persistence, PBKDF2 password hashing, role-based session state,
and clean form validation.
"""

from __future__ import annotations

import re
import streamlit as st
from database import db, models

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def _inject_login_css():
    st.markdown("""
        <style>
        /* Hide sidebar on authentication page */
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
            position: fixed; top: -120px; left: -100px; width: 440px; height: 440px;
            background: radial-gradient(circle, rgba(0,229,255,0.3), transparent 70%);
            border-radius: 50%; filter: blur(14px);
            animation: floatGlow 10s ease-in-out infinite;
            z-index: 0; pointer-events: none;
        }
        .login-orb-2 {
            position: fixed; bottom: -140px; right: -100px; width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(124,58,237,0.3), transparent 70%);
            border-radius: 50%; filter: blur(14px);
            animation: floatGlow 12s ease-in-out infinite reverse;
            z-index: 0; pointer-events: none;
        }

        .login-hero {
            animation: fadeInUp 0.7s ease-out;
            padding: 10px 10px 10px 4px;
        }

        .login-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(0, 229, 255, 0.12); border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 999px; padding: 6px 14px; font-size: 0.8rem; font-weight: 700;
            color: #00E5FF; letter-spacing: 0.5px; margin-bottom: 20px;
        }

        .login-hero h1 {
            font-size: 2.6rem !important; line-height: 1.15 !important;
            margin-bottom: 14px !important; color: #FFFFFF !important;
            background: linear-gradient(135deg, #FFFFFF 30%, #00E5FF 75%, #7C3AED 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .login-hero p.subtitle {
            color: #C9D1D9 !important; font-size: 1.02rem; line-height: 1.6; max-width: 480px;
            margin-bottom: 28px;
        }

        .feature-row {
            display: flex; align-items: flex-start; gap: 14px;
            margin-bottom: 18px; animation: fadeInUp 0.9s ease-out;
        }
        .feature-icon {
            flex-shrink: 0; width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem;
            background: linear-gradient(135deg, rgba(0,229,255,0.18), rgba(124,58,237,0.18));
            border: 1px solid rgba(255,255,255,0.12);
        }
        .feature-text b { color: #F0F6FC !important; font-size: 0.98rem; display: block; margin-bottom: 2px; }
        .feature-text span { color: #9BA6B4 !important; font-size: 0.85rem; }

        .login-card-wrap { animation: fadeInUp 0.8s ease-out; position: relative; z-index: 1; }

        .login-card {
            background: linear-gradient(180deg, rgba(22,27,34,0.96), rgba(13,17,23,0.96));
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 20px;
            padding: 30px 28px 24px 28px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,229,255,0.12) inset;
            backdrop-filter: blur(20px);
        }

        .login-card-header { text-align: center; margin-bottom: 18px; }
        .login-card-header .logo-circle {
            width: 56px; height: 56px; margin: 0 auto 10px auto;
            border-radius: 16px;
            background: linear-gradient(135deg, #00E5FF 0%, #0088FF 50%, #7C3AED 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8rem;
            box-shadow: 0 8px 24px rgba(0,229,255,0.35);
        }
        .login-card-header h3 { margin: 0 0 4px 0 !important; font-size: 1.35rem !important; color: #FFFFFF !important; }
        .login-card-header p { color: #8B949E !important; font-size: 0.88rem; margin: 0; line-height: 1.4; }

        .login-footer {
            text-align: center; margin-top: 18px;
            color: #8B949E !important; font-size: 0.78rem;
        }
        </style>

        <div class="login-orb-1"></div>
        <div class="login-orb-2"></div>
    """, unsafe_allow_html=True)


def validate_password_strength(password: str) -> str | None:
    """Validate password length and character complexity."""
    if len(password) < 8:
        return "Password must contain at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number (0-9)."
    return None


def render():
    """Renders the unified enterprise authentication portal."""
    _inject_login_css()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    hero_col, form_col = st.columns([1.1, 1], gap="large")

    # ---------------- LEFT: Branding & Platform Info ----------------
    with hero_col:
        st.markdown("""
            <div class="login-hero">
                <span class="login-badge">🏗️ ENTERPRISE CONSTRUCTION INTELLIGENCE</span>
                <h1>Construction<br>Intelligence Hub</h1>
                <p class="subtitle">
                    Unified platform for project analytics, cost estimation, schedule delay prediction,
                    safety risk assessment, and material estimation.
                </p>
            </div>
        """, unsafe_allow_html=True)

        features = [
            ("📊", "Executive Dashboard", "Live project KPIs, progress metrics, and budget tracking"),
            ("🛡️", "Safety & Risk Intelligence", "Predictive site risk scoring and incident management"),
            ("💰", "Predictive Cost & Schedule ML", "AI-driven cost forecasting and delay risk evaluation"),
            ("🧱", "Material & Resource Estimation", "Instant BOQ calculation, labor analysis, and waste control"),
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

    # ---------------- RIGHT: Unified Authentication Card ----------------
    with form_col:
        st.markdown('<div class="login-card-wrap"><div class="login-card">', unsafe_allow_html=True)

        st.markdown("""
            <div class="login-card-header">
                <div class="logo-circle">🏗️</div>
                <h3>Construction Hub Portal</h3>
                <p>Access your construction intelligence, project analytics, cost estimation &amp; safety tools.</p>
            </div>
        """, unsafe_allow_html=True)

        # Tab Toggle Interface
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

        # ---------------- 🔑 MODE 1: SIGN IN ----------------
        with tab_login:
            st.markdown("<p style='color:#C9D1D9; font-size:0.9rem; margin-bottom:14px;'>Welcome back to Construction Intelligence Hub</p>", unsafe_allow_html=True)

            # Flash registration success message if user just created an account
            if st.session_state.get("reg_success_msg"):
                st.success(st.session_state.pop("reg_success_msg"))

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="Enter your email address", key="login_email")
                show_pass = st.checkbox("👁️ Show Password", key="show_login_pass")
                # Fix: Streamlit text_input type parameter must ONLY be "default" or "password"
                password_type = "default" if show_pass else "password"
                password = st.text_input("Password", type=password_type, placeholder="Enter your password", key="login_password")

                remember_me = st.checkbox("Remember me", value=True)
                submitted = st.form_submit_button("🔑 Sign In to Construction Hub", type="primary", use_container_width=True)

            if submitted:
                if not email.strip():
                    st.error("Please enter your email address.")
                elif not password:
                    st.error("Please enter your password.")
                else:
                    with db.get_db() as conn:
                        user, err = models.authenticate_user(conn, email, password)

                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.username = user.get("full_name") or user.get("email")
                        st.session_state.role = user.get("role", "User")
                        st.success("✅ Login successful. Redirecting to dashboard...")
                        st.rerun()
                    else:
                        st.error(f"❌ {err or 'Email or password is incorrect.'}")

        # ---------------- 📝 MODE 2: CREATE ACCOUNT ----------------
        with tab_register:
            st.markdown("<p style='color:#C9D1D9; font-size:0.9rem; margin-bottom:14px;'>Create your Construction Intelligence Hub account</p>", unsafe_allow_html=True)

            with st.form("register_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
                reg_email = st.text_input("Email Address", placeholder="Enter your email address", key="reg_email")

                show_reg_pass = st.checkbox("👁️ Show Password", key="show_reg_pass")
                reg_pass_type = "default" if show_reg_pass else "password"

                reg_password = st.text_input("Password", type=reg_pass_type, placeholder="Create a strong password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type=reg_pass_type, placeholder="Confirm your password", key="reg_confirm")

                reg_submitted = st.form_submit_button("📝 Create Construction Hub Account", type="primary", use_container_width=True)

            if reg_submitted:
                full_name_clean = full_name.strip()
                email_clean = reg_email.strip().lower()

                # Validation checks
                if not full_name_clean or len(full_name_clean) < 3:
                    st.error("Please enter your full name (at least 3 characters).")
                elif not email_clean or not EMAIL_REGEX.match(email_clean):
                    st.error("Please enter a valid email address.")
                elif not reg_password:
                    st.error("Please enter a password.")
                else:
                    strength_err = validate_password_strength(reg_password)
                    if strength_err:
                        st.error(strength_err)
                    elif reg_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        # Internal Backend Role Assignment: New accounts are automatically assigned role="User"
                        with db.get_db() as conn:
                            user, err = models.create_user(
                                conn,
                                full_name=full_name_clean,
                                email=email_clean,
                                password=reg_password,
                                role="User",
                            )

                        if err:
                            st.error(f"❌ {err}")
                        else:
                            st.session_state.reg_success_msg = "✅ Account created successfully. Please sign in."
                            st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="login-footer">
                © 2026 Construction Intelligence Hub · Enterprise Security Secured
            </div>
        """, unsafe_allow_html=True)


def logout():
    """Clears all authentication session state and redirects to unified login."""
    st.session_state.authenticated = False
    st.session_state.pop("user", None)
    st.session_state.pop("username", None)
    st.session_state.pop("role", None)
    st.session_state.pop("page", None)
    st.rerun()