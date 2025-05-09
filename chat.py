
import os
import requests
from dotenv import load_dotenv
from langdetect import detect
from sentence_transformers import SentenceTransformer

# 🔄 Load environment variables
load_dotenv()

class Chatbot:
    def __init__(self):
        # Load both English and Multilingual models
        self.models = {
            "english": SentenceTransformer("BAAI/bge-large-en"),
            "multilang": SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")
        }
        self.chat_history = []

    def get_embedding(self, text):
        """Get sentence embeddings using the appropriate model based on language."""
        try:
            lang = detect(text)
            model_key = "english" if lang == "en" else "multilang"
            print(f"🧠 Detected language: {lang}, using model: {model_key}")
            return self.models[model_key].encode(text)
        except Exception as e:
            print(f"⚠ Language detection error: {e}")
            return self.models["english"].encode(text)  # fallback

    def get_response(self, user_input):
        """Handle user input and return response."""
        if not user_input.strip():
            return "⚠ Please enter a valid question."
        return self.call_groq(user_input)

    def call_groq(self, user_input):
        """Generate a response via the Groq API."""
        print("🚀 Calling Groq API...")
        try:
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                return "❌ Groq API key not set."

            self.chat_history.append({"role": "user", "content": user_input})
            messages = [{"role": "system", "content": "You are a helpful assistant."}] + self.chat_history

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": messages
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content'].strip()
                self.chat_history.append({"role": "assistant", "content": content})
                return content
            else:
                return f"⚠ Groq error {response.status_code}: {response.text}"
        except Exception as e:
            return f"❌ Failed to contact Groq: {e}"

    def chat(self):
        print("🤖 Hello! I am your chatbot. Type 'bye' to exit.")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'bye':
                print("Chatbot: Goodbye! 👋")
                break
            response = self.get_response(user_input)
            print(f"Chatbot: {response}")

if __name__ == "__main__":
    bot = Chatbot()
    bot.chat()
