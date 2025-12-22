import streamlit as st
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")
