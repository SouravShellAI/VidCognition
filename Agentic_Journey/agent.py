import os
import time
from google import genai
from google.api_core import exceptions

# Authenticate with Google GenAI using the API Key
client = genai.Client(api_key="Your_API_key")

# Define the LLM Model ID
MODEL_ID = "gemini-2.5-flash"

def start_agent():
    """
    Launches a terminal-based chatbot that uses 'transcript.txt' as its core knowledge.
    """
    print(f"--- AGENT BRAIN ONLINE (Model: {MODEL_ID}) ---")

    # Verify that the knowledge source exists
    try:
        if not os.path.exists("transcript.txt"):
            print("❌ Error: 'transcript.txt' missing. Please run ingest.py first.")
            return

        with open("transcript.txt", "r", encoding="utf-8") as f:
            context_data = f.read()

    except Exception as e:
        print(f"❌ File Access Error: {e}")
        return

    # Chat loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]: break 

        # Construct a RAG (Retrieval-Augmented Generation) prompt
        # We inject the entire file into the context window for accurate answering
        prompt = (
            f"You are a helpful assistant. Use the provided text to answer the question.\n"
            f"CONTEXT FROM FILE:\n{context_data}\n\n"
            f"QUESTION: {user_input}"
        )

        try:
            # Send the context + question to Gemini
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            
            if response.text:
                print(f"Agent: {response.text}")
            else:
                print("Agent: [No response generated]")             

        except exceptions.ResourceExhausted:
            # Handle Free Tier limits gracefully
            print("⚠️ Quota Exceeded! Sleeping for 60s...")
            time.sleep(60)
        except Exception as e:
            print(f"❌ AI Error: {e}")

if __name__ == "__main__":
    start_agent()