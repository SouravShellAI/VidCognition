import streamlit as st
import os
import chromadb
import json
import re
from datetime import datetime
from google import genai
from sentence_transformers import SentenceTransformer
from youtube_transcript_api import YouTubeTranscriptApi

# --- 1. UI ARCHITECTURE & STYLING ---
def apply_premium_ui():
    """
    Injects custom CSS to create a wide-screen, cinematic dark theme.
    Colors used: #011425 (Deep Navy), #5C7C89 (Slate Blue), #0A1F2F (Charcoal).
    """
    st.markdown(f"""
        <style>
        .block-container {{
            max-width: 100% !important;
            padding-left: 5rem !important; padding-right: 5rem !important;
            padding-top: 5rem !important; background-color: #011425;
        }}
        .stApp {{ background-color: #011425; color: #FFFFFF; }}
        h1, h2, h3 {{ color: #5C7C89 !important; font-family: 'Inter', sans-serif; letter-spacing: -1px; text-transform: uppercase; }}
        .stTextArea textarea, .stTextInput input {{
            background-color: #0A1F2F !important; color: #E0E0E0 !important;
            border: 1px solid #1F4959 !important; border-radius: 12px !important;
            padding: 15px !important; font-size: 16px !important;
        }}
        .stButton>button {{
            background: linear-gradient(145deg, #1F4959, #0A1F2F) !important;
            color: #FFFFFF !important; border: 1px solid #5C7C89 !important;
            border-radius: 10px !important; font-weight: 700 !important;
            text-transform: uppercase; letter-spacing: 1.5px; padding: 0.8rem !important;
        }}
        .stExpander, [data-testid="stChatMessage"] {{
            background-color: #0A1F2F !important; border: 1px solid #1F4959 !important; border-radius: 15px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_premium_ui()

# --- 2. BACKEND SERVICES & MODELS ---
GEMINI_API_KEY = "Your_API-key"
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash"
FEEDBACK_FILE = "feedback_logs.json"
USERS_FILE = "user_registry.json"

@st.cache_resource
def load_resources():
    """
    Loads embedding models and vector databases once and caches them to save memory.
    """
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    db_client = chromadb.PersistentClient(path="./my_ai_memory")
    collection = db_client.get_or_create_collection(name="rick_memory")
    return embed_model, collection

embed_model, collection = load_resources()

# --- 3. DATA PERSISTENCE UTILITIES ---
def save_data_to_json(file_path, new_entry):
    """Appends data to a JSON file while maintaining valid list structure."""
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try: data = json.load(f)
            except: data = []
    data.append(new_entry)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- 4. GLOBAL STATE MANAGEMENT ---
# Ensures data persists across Streamlit's frequent script reruns
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "full_transcript" not in st.session_state: st.session_state.full_transcript = "SYSTEM INITIALIZED..."
if "summary" not in st.session_state: st.session_state.summary = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "editor_key" not in st.session_state: st.session_state.editor_key = 0

# --- 5. SIDEBAR: AUTHENTICATION & FEEDBACK ---
with st.sidebar:
    st.markdown("### 👤 USER ACCESS")
    if not st.session_state.logged_in:
        with st.form("login_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            if st.form_submit_button("LOGIN / REGISTER"):
                if name and email:
                    st.session_state.logged_in = True
                    st.session_state.user_name = name
                    save_data_to_json(USERS_FILE, {"name": name, "email": email, "timestamp": str(datetime.now())})
                    st.rerun()
                else:
                    st.error("Please fill all fields")
    else:
        st.success(f"Verified User: {st.session_state.user_name}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")
    st.markdown("### 🌟 FEEDBACK & RATING")
    rating = st.select_slider("Rate Experience", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
    comment = st.text_area("Observations:", height=100)
    if st.button("SUBMIT FEEDBACK"):
        feedback_entry = {
            "user": st.session_state.user_name if st.session_state.logged_in else "Anonymous",
            "rating": rating, "comment": comment, "timestamp": str(datetime.now())
        }
        save_data_to_json(FEEDBACK_FILE, feedback_entry)
        st.toast("Feedback Logged!", icon="🚀")

# --- 6. AGENTIC PIPELINE FUNCTIONS ---
def update_vector_db(text, video_id="manual_edit"):
    """Re-chunks and re-indexes text into ChromaDB whenever edits are made."""
    with open("transcript.txt", "w", encoding="utf-8") as f: f.write(text)
    try: collection.delete(where={"source": video_id})
    except: pass
    
    chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 10]
    for i, chunk in enumerate(chunks):
        vector = embed_model.encode(chunk).tolist()
        collection.add(ids=[f"{video_id}_{i}"], embeddings=[vector], documents=[chunk], metadatas=[{"source": video_id}])
    return f"SYNC SUCCESS: {len(chunks)} fragments indexed."

def process_youtube():
    """Main pipeline: Fetches YouTube text -> Formats via AI -> Summarizes -> Stores."""
    url = st.session_state.yt_url_input
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    video_id = match.group(1) if match else None
    
    if not video_id:
        st.error("Invalid URL")
        return

    with st.spinner("EXECUTING DATA PIPELINE..."):
        try:
            # 1. Scraping
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            try: transcript = transcript_list.find_transcript(['en', 'bn'])
            except: transcript = next(iter(transcript_list))
            raw_text = " ".join([item.text for item in transcript.fetch() if "align:" not in item.text])
            
            # 2. AI Formatting (Cleaning the text)
            st.session_state.full_transcript = client.models.generate_content(model=MODEL_ID, contents=f"Format this: {raw_text[:4000]}").text
            
            # 3. AI Summarization
            st.session_state.summary = client.models.generate_content(model=MODEL_ID, contents=f"Summarize: {st.session_state.full_transcript}").text
            
            # 4. Storage & UI Sync
            st.session_state.editor_key += 1
            update_vector_db(st.session_state.full_transcript, video_id)
            st.toast("INTEGRATION COMPLETE", icon="⚡")
        except Exception as e:
            st.error(f"PIPELINE FAILURE: {str(e)}")

# --- 7. MAIN UI COMPOSITION ---
col_left, col_right = st.columns([1.3, 1], gap="large")

with col_left:
    st.markdown("### 🖋️ WORKSPACE: CONTENT EDITOR")
    # Dynamic editor that reloads when a new video is analyzed
    edited_text = st.text_area("Editor", value=st.session_state.full_transcript, height=720, key=f"editor_{st.session_state.editor_key}", label_visibility="collapsed")
    if st.button("COMMIT CHANGES TO AI MEMORY"):
        st.session_state.full_transcript = edited_text
        update_vector_db(edited_text)
        st.success("Database and Local Files Synchronized.")

with col_right:
    st.markdown("### 🛰️ COMMAND CENTER")
    with st.expander("📥 DATA INGESTION", expanded=True):
        st.text_input("YouTube Source URL", key="yt_url_input", on_change=process_youtube)
        st.button("INITIALIZE ANALYSIS", on_click=process_youtube)

    if st.session_state.summary:
        with st.expander("📊 CORE INSIGHTS", expanded=True):
            st.markdown(st.session_state.summary)

    # Chat Interaction History
    chat_container = st.container(height=480)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # User Query Input
    if prompt := st.chat_input("Query the knowledge base..."):
        if not st.session_state.logged_in:
            st.warning("Registration Required: Please use the sidebar to continue.")
        else:
            # 1. Record user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 2. Vector Retrieval (Finding relevant text snippets)
            query_vector = embed_model.encode(prompt).tolist()
            results = collection.query(query_embeddings=[query_vector], n_results=3)
            context = "\n".join(results['documents'][0])
            
            # 3. Contextual Generation (Gemini's answer)
            with st.chat_message("assistant"):
                response = client.models.generate_content(model=MODEL_ID, contents=f"Context: {context}\nQuestion: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})