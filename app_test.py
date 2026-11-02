import streamlit as st
import yaml
import bcrypt
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="Admin Verification",
    page_icon="🔒",
    layout="centered"
)

# -------------------------------------------------------------------
# Load configuration
# -------------------------------------------------------------------
with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=SafeLoader)

ADMIN_USERNAME = "saiful"

ADMIN_HASHED_PW = config["credentials"]["usernames"][ADMIN_USERNAME]["password"]

# -------------------------------------------------------------------
# Initialize authentication session state
# -------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def check_credentials(username_input, password_input):

    if username_input != ADMIN_USERNAME:
        return False

    return bcrypt.checkpw(
        password_input.encode("utf-8"),
        ADMIN_HASHED_PW.encode("utf-8")
    )


# -------------------------------------------------------------------
# Login Form
# -------------------------------------------------------------------
def login_form():

    st.markdown(
        "<h2 style='text-align: center;'>🔒 Admin Login</h2>",
        unsafe_allow_html=True
    )

    st.write(
        "Please sign in to access the private recovery dashboard."
    )

    with st.form("login_box"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        submit_button = st.form_submit_button(
            "Sign In",
            use_container_width=True
        )

        if submit_button:

            if check_credentials(username, password):

                st.session_state.authenticated = True

                st.success("Login successful!")

                st.rerun()

            else:

                st.error("Invalid username or password.")


# -------------------------------------------------------------------
# Access Control
# -------------------------------------------------------------------
if not st.session_state.authenticated:

    login_form()

    st.stop()


# -------------------------------------------------------------------
# Private Admin Dashboard
# -------------------------------------------------------------------
st.sidebar.write(
    f"Logged in as **{ADMIN_USERNAME}**"
)

if st.sidebar.button("Logout"):

    st.session_state.authenticated = False

    st.rerun()


st.title("🎉 Welcome, Saiful!")

st.success(
    "Access Granted: You are in the private dashboard area."
)