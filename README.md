# 🛰️ Agentic Journey: Modular RAG Workspace

**Agentic Journey** is a professional-grade Full-Stack AI application that transforms YouTube video content into a searchable, interactive knowledge base. Utilizing **Retrieval-Augmented Generation (RAG)**, the system allows users to ingest video transcripts, edit them for accuracy, and chat with an AI Agent that has "perfect memory" of the content.

---

## 🚀 Key Features

* **Multi-Source Ingestion:** Extract transcripts from YouTube URLs in multiple languages (English, Bengali, and more).

* **Modular RAG Pipeline:**
    * **Ingest:** Raw data extraction via `YouTubeTranscriptApi`.
    * **Memory:** Vector embedding and storage using `ChromaDB` and `Sentence-Transformers`.
    * **Agent:** Context-aware response generation using `Google Gemini 1.5/2.5 Flash`.

* **Human-in-the-Loop Workspace:** A dedicated editor allowing users to manually correct AI-formatted transcripts before committing them to the Vector Database.

* **Secure Access Wall:** Integrated user registration and login system with email validation.

* **Cinematic UI:** A custom-styled, high-contrast Dark Mode interface built with Streamlit.

* **Feedback System:** Built-in rating and logging system to track user experience and feature requests.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Custom CSS Theming)
* **LLM:** [Google Gemini API](https://ai.google.dev/)
* **Vector Database:** [ChromaDB](https://www.trychroma.com/)
* **Embeddings:** `all-MiniLM-L6-v2` (Sentence-Transformers)
* **Language:** Python 3.9+

---

## 📂 Project Structure

```text
Agentic_Journey/
├── app.py                # Main Streamlit app (UI + logic)
├── ingest.py             # YouTube transcript extraction
├── memory.py             # Vector DB indexing/testing
├── agent.py              # CLI-based RAG agent
├── requirements.txt      # Dependencies
├── .gitignore            # Ignore sensitive/local files
└── README.md             # Documentation
```
## ⚙️ Installation & Setup

### 1. Clone the Repository
   
```text
git clone [https://github.com/your-username/Agentic_Journey.git](https://github.com/your-username/Agentic_Journey.git)
cd Agentic_Journey
```

### 2. Install Dependencies

```text
pip install -r requirements.txt
```

### 3. Configure API Key

Open app.py, agent.py, and ingest.py and replace the placeholder with your **Google Gemini API key**:

```text
client = genai.Client(api_key="Your_API_Key")
```

### 4. Run the Application

```text
python -m streamlit run app.py
```

## 🛡️ Security & Best Practices

* **Data Privacy:** Local JSON files (user_registry.json, feedback_logs.json) and the ChromaDB folder are listed in .gitignore to prevent the leakage of personal user data or machine-specific binaries to GitHub.

* **Modular Architecture:** The project is separated into logic-specific files (ingest, memory, agent) to allow for easy debugging and scaling.

* **Validation:** Strict Regex-based email validation ensures data integrity during user registration.

## 🌟 Future Roadmap

 * Implementation of OAuth2 (Google Login)
   
 * Support for PDF and document ingestion
   
 * Export AI-generated insights to PDF/Markdown
   
## 👨‍💻 Author

**Sourav Mondal**

_Exploring the intersection of LLMs and Vector Search._
