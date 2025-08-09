# Quintus Streamlit App v1.2 - Persistent Memory
import streamlit as st
import google.generativeai as genai
from google.cloud import firestore
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
    db = firestore.Client.from_service_account_info(st.secrets["gcp_service_account"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize. Please check your secrets configuration. Error: {e}")
    st.stop()

# --- Main App ---
st.title("💡 Quintus 2.0")

# --- Chat History Management ---
# Function to load chat history from Firestore
def load_history():
    try:
        docs = db.collection(FIRESTORE_COLLECTION).order_by("timestamp_cdt", direction=firestore.Query.DESCENDING).limit(15).stream()
        history = list(docs)
        history.reverse() # Show newest at the bottom
        
        messages = []
        for doc in history:
            entry = doc.to_dict()
            messages.append({"role": "user", "content": entry.get("user_input", "")})
            messages.append({"role": "assistant", "content": entry.get("quintus_response", "")})
        
        st.session_state.messages = messages
    except Exception as e:
        st.error(f"Failed to load conversation history: {e}")
        st.session_state.messages = []

# Initialize chat history in session state
if "messages" not in st.session_state:
    load_history()

# Display chat messages from history
for message in st.session_state.messages:
    # Use custom avatars
    avatar = "💡" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- User Input & Chat Logic ---
if prompt := st.chat_input("What is on your mind, Keeper?"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant", avatar="💡"):
        message_placeholder = st.empty()
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction=MASTER_PROMPT)
        # Prepare history for the model
        chat_history_for_model = [
            {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]
        ]
        chat = model.start_chat(history=chat_history_for_model)
        response = chat.send_message(prompt)
        
        full_response = response.text
        message_placeholder.markdown(full_response)
        
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- Save the complete exchange to Firestore ---
    try:
        central_tz = pytz.timezone('America/Chicago')
        timestamp = datetime.now(central_tz)
        text_to_index = prompt + " " + full_response
        keywords_for_doc = list(set(text_to_index.lower().split()))
        
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(timestamp.strftime('%Y-%m-%d_%H-%M-%S.%f'))
        doc_ref.set({
            'user_input': prompt,
            'quintus_response': full_response,
            'timestamp_cdt': timestamp,
            'keywords_array': keywords_for_doc
        })
    except Exception as e:
        st.error(f"Failed to save conversation to database: {e}")
