import streamlit as st
from streamlit_chat import message
import requests
# import os
import time

# Set page config
st.set_page_config(
    page_title="MentiChat",
    page_icon="../assets/sun.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("Mental Health AI Chat")
st.sidebar.markdown("""
Welcome to the AI-powered mental health chatbot. 
Feel free to ask questions or discuss your thoughts in a safe, non-judgmental space. 💙
""")
st.sidebar.image("https://plus.unsplash.com/premium_photo-1661389446461-1e22c995e48b?q=80&w=1467&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)


# Model Selection (Hugging Face Inference API)
st.sidebar.subheader("Model Selection")
model_name = st.sidebar.selectbox("Choose a model:", [
    "numind/NuExtract-1.5",
    "facebook/blenderbot-400M-distill",
    "microsoft/Phi-3.5-mini-instruct",
    # Edit this for your own model (in Hugging Face API Mode)
])

# Hugging Face API Key
HF_API_KEY = st.sidebar.text_input("Enter your Hugging Face API Key", type="password")


# Chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Chat Interface
st.title("🧠 MentiChat")

def get_response_from_huggingface(user_text, model_name, api_key):
    if not api_key:
        return "⚠️ Error: Hugging Face API key is missing!"
    
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {api_key}"}

    payload = {"inputs": user_text, "options":{"wait_for_model":True}}  

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        if isinstance(response.json(), list):  # Handling different response formats
            return response.json()[0]["generated_text"]
        elif isinstance(response.json(), dict) and "generated_text" in response.json():
            return response.json()["generated_text"]
        else:
            return "Unexpected response format from API. Check the model's expected output."  # More informative error message

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")
        return f"Error: {e}"
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return f"Error: {e}"

# User input with "send" button and icon
with st.form(key="user_input_form"):  # Use a form to group the input and button
    col1, col2 = st.columns([9, 1])  # Create two columns for layout

    with col1:
        user_input = st.text_input(" ", placeholder="What's on your mind today?", key="user_input_text", label_visibility="collapsed")

    with col2:
        submit_button = st.form_submit_button("➡️") # Use arrow as send button


# Handle user input and responses (using the form submit)
if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    ai_response = get_response_from_huggingface(user_input, model_name, HF_API_KEY) # Replace with your API call function

    st.session_state.chat_history.append({"role": "bot", "text": ai_response})

# Display loading animation for AI response
def show_typing_indicator():
    with st.empty():
        typing_animation = "..."
        for _ in range(3):
            st.text(f"Bot is typing{typing_animation}")
            time.sleep(0.5)
            typing_animation += "."
            st.text(f"Bot is typing{typing_animation}")
            time.sleep(0.5)
            st.text("")

# Handle user input and responses
if user_input:
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    # Show typing indicator while fetching response
    show_typing_indicator()

    # Auto-remove typing indicator after response
    time.sleep(2)

    ai_response = get_response_from_huggingface(user_input, model_name, HF_API_KEY)
    st.session_state.chat_history.append({"role": "bot", "text": ai_response})

# Display chat history (reversed, with the latest message at the bottom)
for i, msg in enumerate(reversed(st.session_state.chat_history)):
    if msg["role"] == "user":
        message(msg["text"], is_user=True, key=f"user_{i}")
    else:
        message(msg["text"], key=f"bot_{i}")

# Footer
st.markdown("""
---
*This chatbot is designed to provide general mental health support but is not a substitute for professional advice.*
""")