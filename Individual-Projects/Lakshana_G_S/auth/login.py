import streamlit as st

from auth.auth import authenticate


def show_login():

    st.markdown("<br><br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.5, 1])

    with c2:

        st.image(
            "assets/logo.png",
            width=200 
        )

        st.title("ConstructIQ AI")

        st.caption(
            "Enterprise Construction Management Platform"
        )

        st.divider()

        st.subheader("Login")

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        remember = st.checkbox(
            "Remember Me"
        )

        login = st.button(
            "Login",
            use_container_width=True
        )

        if login:

            user = authenticate(
                email,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success(
                    f"Welcome {user['name']}"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Email or Password"
                )