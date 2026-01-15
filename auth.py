import streamlit as st

PASSWORD = "admin"  # Change this to whatever you want

def check_password():
    """Returns True if the user is logged in."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

def login_form():
    """Renders the login sidebar form."""
    with st.sidebar:
        if not check_password():
            st.header("Manager Login")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login"):
                if pwd == PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Wrong password")
        else:
            st.success("Logged In as Manager")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()