# Library yang digunakan
import os
# import time
import requests
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import google.generativeai as genai


# Deployment API (Streamlit)
API_DB = st.secrets["API_KEY"]["API_DB"]
API_HF_KEY = st.secrets["API_KEY"]["API_HF_KEY"]
MODEL_NAME = st.secrets["API_KEY"]["MODEL_NAME"]

# # Memanggil API dari env file (Local File API Setting)
# load_dotenv()
# API_DB = os.getenv("API_DB")
# API_HF_KEY =  os.getenv("API_HF_KEY")
# MODEL_NAME = os.getenv("MODEL_NAME")

# Fungsi Reset Chat (General) 
def reset_chat_history():
    st.session_state.chat_history = []
    st.session_state.input_key = 0 

# Setup bar di dalam streamlit
st.set_page_config(
    page_title="MentiChat",
    page_icon="../assets/sun.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Setup Sidebar ada apa aja
st.sidebar.title("Mental Health AI Chat")
st.sidebar.markdown("""
Welcome to the AI-powered mental health chatbot.
Feel free to ask questions or discuss your thoughts in a safe, non-judgmental space. 💙
""")
st.sidebar.image("https://plus.unsplash.com/premium_photo-1661389446461-1e22c995e48b?q=80&w=1467&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)


# Tambahkan tombol reset di sidebar dengan styling
st.sidebar.markdown("""
    <style>
        .center-button {
            display: flex;
            justify-content: center;
            margin: 1em 0;
        }
    </style>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Reset Chat History", key="reset_button", use_container_width=True):
    reset_chat_history()
    st.rerun()

# Sidebar - Model Selection
st.sidebar.subheader("Model Selection")
model_provider = st.sidebar.selectbox(
    "Choose a model provider:",
    ["Hugging Face", "Google"],
    key="model_provider_selectbox"
)

if model_provider == "Hugging Face":
    model_name = st.sidebar.selectbox(
        "Choose a Hugging Face model:",
        ["numind/NuExtract-1.5", "facebook/blenderbot-400M-distill", "microsoft/Phi-3.5-mini-instruct"],
        key="huggingface_model_selectbox"
    )
    HF_API_KEY = API_HF_KEY
else:
    model_name = None

if model_provider == "Google":
    API_DB = API_DB
    if not API_DB:
        st.sidebar.error("Google API key not found in .env file!")


# Chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Chat Interface
st.markdown("""
<div style="background-color:#f0f0f5; padding:10px; border-radius:10px; text-align:center;">
    <h1 style="color:#336699;">🧠 MentiChat</h1>
    <p style="color:#666;">Your AI Mental Health Companion</p>
</div>
""", unsafe_allow_html=True)


# Respons dari GEN AI (Google atau Hugging Face API)
def get_response(user_text, model_provider, model_name=None, hf_api_key=None):
    if model_provider == "Hugging Face":
        return get_response_from_huggingface(user_text, model_name, hf_api_key)
    elif model_provider == "Google":
        return get_response_from_google(user_text)
    else:
        return "Invalid model provider selected."

def get_response_from_huggingface(user_text, model_name, api_key):

    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": user_text, "options": {"wait_for_model": True}}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return data[0]["generated_text"]
        elif isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        else:
            return "Unexpected response format from Hugging Face API."

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Hugging Face API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_response_from_google(user_text):
    if not API_DB:
        return "⚠️ Error: Google API key is missing!"

    genai.configure(api_key=API_DB) 

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(user_text)
        return response.text

    except Exception as e:
        return f"An error occurred with API : {e}"

# Inisialisasi state untuk clear input
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Function to increment key and clear input
def clear_input():
    st.session_state.input_key += 1

# User input question form
with st.form(key="user_input_form"):
    col1, col2 = st.columns([9, 1])

    with col1:
        user_input = st.text_input(
            " ", 
            placeholder="What's on your mind today?", 
            key=f"user_input_text_{st.session_state.input_key}", 
            label_visibility="collapsed"
        )
    with col2:
        submit_button = st.form_submit_button("➡️")

# State menghandle interakasi user dengan bot
if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    if model_provider == "Hugging Face" and model_name:
        ai_response = get_response_from_huggingface(user_input, model_name, HF_API_KEY)
    elif model_provider == "Google":
        ai_response = get_response_from_google(user_input)
    else:
        ai_response = "⚠️ Error: Model provider or model not selected!"

    st.session_state.chat_history.append({"role": "bot", "text": ai_response})
    
    # Clear input by changing the input key
    clear_input()
    st.rerun()

# Display chat history
for i, msg in enumerate(reversed(st.session_state.chat_history)):
    if msg["role"] == "user":
        message(msg["text"], is_user=True, key=f"user_{i}")
    else:
        # Handle potential variations in response format
        if hasattr(msg["text"], 'response'): 
            response_text = msg["text"].response
        elif hasattr(msg["text"], 'result'):
            response_text = msg["text"].result
        elif isinstance(msg["text"], str): 
            response_text = msg["text"]
        else: # Fallback for unexpected types, displays the type for debugging
            response_text = f"Error: Unexpected response type: {type(msg['text'])}. Please check your API integration."

        message(response_text, key=f"bot_{i}")


# Footer (DISCLAIMER)
st.markdown("""
---
*This chatbot is designed to provide general mental health support but is not a substitute for professional advice.*
""")