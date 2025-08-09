# Quintus Streamlit App v1.0 - Full Engine
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

You have access to a persistent Firestore database and a `search_firestore_history` tool. When the user asks a question about past conversations, you should use this tool to find relevant information. Analyze the user's natural language to determine the keywords for the search.
"""
FIRESTORE_COLLECTION = "quintus_conversations"

# --- Authentication & Initialization ---
# Initialize connections using Streamlit's secrets management
try:
    # Use st.secrets to securely access your credentials
    creds = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    db = firestore.Client(credentials=firestore.credentials.Credentials.from_service_account_info(creds))
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize database or Gemini. Please check your secrets. Error: {e}")
    st.stop()


# --- Tool Definition & Function ---
# (Search function will be defined here in a real implementation)
# For now, we'll focus on the chat functionality.


# --- Main App ---
st.title("💡 Quintus 2.0")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # You could add a step here to load initial history from Firestore

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is on your mind, Keeper?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="💡"):
        message_placeholder = st.empty()
        full_response = ""
        
        # NOTE: For a better user experience, we would use streaming.
        # This is a simplified, non-streaming example for now.
        model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction=MASTER_PROMPT)
        response = model.generate_content(prompt)
        
        full_response = response.text
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
