import streamlit as st  
import google.generativeai as genai 
import os
from dotenv import load_dotenv
import json

# 1. Page Config
st.set_page_config(page_title="Chef AI-Xora", page_icon="👨‍🍳", layout="centered")

# --- THE ULTIMATE CSS FIX (FOR ASSIGNMENT SUBMISSION) ---
st.markdown("""
    <style>
    /* Main Background Black */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stBottom"] {
        background-color: #1E1E1E !important;
    }

    /* FORCING ALL TEXT TO BE PURE WHITE */
    h1, h2, h3, p, li, span, label, div, .stMarkdown, [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* BUDGET BOX FIX: White Background + Black Text (Crucial for image_140a1c) */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
    }
    div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: bold !important;
    }

    /* TABLE FIX: Making recipe details clear (Crucial for image_14161e) */
    table, th, td {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }
    thead th {
        background-color: #000000 !important;
        color: #D4AF37 !important; /* Golden headers */
    }

    /* SIDEBAR: Pure Black with White Border */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #FFFFFF !important;
    }

    /* SEARCH BAR: White Border */
    .stChatInputContainer textarea {
        border: 2px solid #FFFFFF !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* RESET BUTTON: Hover Effect */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }
    .stButton>button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Scrollbar Fix */
    ::-webkit-scrollbar-thumb { background: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Key Access
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Using 1.5-flash for stability and quota
    model = genai.GenerativeModel(model_name='gemini-1.5-flash') 
else:
    st.error("Ghalti: API Key nahi mili! Settings > Secrets mein lazmi check karein.")

# 3. Memory Logic
FILE_NAME = "chef_memory.json"
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f: return json.load(f)
    return []

def save_data(chat_history):
    new_memory = [{"role": m.role, "parts": [{"text": m.parts[0].text}]} for m in chat_history]
    with open(FILE_NAME, "w") as f: json.dump(new_memory, f, indent=4)

# 4. Sidebar Credits
with st.sidebar:
    st.title("👨‍🍳 Chef AI-Xora")
    st.markdown("---")
    st.write("**Developed by: Laiba Naeem**") 
    st.markdown("---")
    budget = st.number_input("Enter your Budget (Rs):", min_value=0, value=500, step=50)
    if st.button("🗑️ Reset Memory"):
        if os.path.exists(FILE_NAME): os.remove(FILE_NAME)
        st.rerun()

# 5. Chat Interface
st.title("Strategic Kitchen Assistant 🥗")
memory = load_data()
chat = model.start_chat(history=memory)

for msg in chat.history:
    role = "user" if msg.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.parts[0].text)

user_input = st.chat_input("Tell Chef AI-Xora what's in your kitchen...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Strategizing..."):
            try:
                # Proper context with Budget
                response = chat.send_message(f"[Budget: Rs.{budget}] {user_input}")
                st.markdown(response.text)
                save_data(chat.history)
            except Exception as e:
                if "429" in str(e):
                    st.error("Quota Over! Aaj ki requests poori ho gayi hain.")
                else:
                    st.error(f"Error: {e}")