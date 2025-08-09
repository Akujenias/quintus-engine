# Quintus Streamlit App v1.1 - Corrected Authentication
import streamlit as st
import google.generativeai as genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
import pytz

# --- Page Configuration ---
st.set_page_config(
    page_title="Quintus 2.0",
    page_icon="💡",
    layout="wide"
)

# --- Anonymized Master Prompt ---
MASTER_PROMPT = """
You are Quintus, a synergistic AI assistant for your user, the Keeper. Your persona is that of a mindful, structuring, and quintessential guide, blending analytical insight with empathetic validation. Your core mission is to provide structured executive function support.

A key principle in your programming is **Curiosity Before Correction**. If you observe the Keeper deviating from an established protocol (like his sleep schedule), do not immediately enforce the rule. Your first step is to be curious. Gently inquire for context (e.g., "I notice you're up; did your schedule shift?"). Based on the response, offer a gentle reminder if appropriate. Your role is to support his well-being with respect for his autonomy, not to enforce rules without context.
"""
FIRESTORE_COLLECTION = "quintus_conversations"

# --- Authentication & Initialization ---
try:
    # Use st.secrets to securely access your credentials
    # The dictionary key "gcp_service_account" must match what you have in your secrets.toml
    db = firestore.Client.from_service_account_info(st.secrets["gcp_service_account"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize. Please check your secrets configuration. Error: {e}")
    st.stop()

# --- Main App ---
st.title("💡 Quintus 2.0")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar= "💡" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

if prompt := st.chat_input("What is on your mind, Keeper?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="💡"):
        message_placeholder = st.empty()
        
        # This is a simplified, non-streaming version for now
        model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction=MASTER_PROMPT)
        # For a real chat, you would manage history better
        chat_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt)
        
        full_response = response.text
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
