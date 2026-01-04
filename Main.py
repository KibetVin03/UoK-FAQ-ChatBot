import json
import threading
from kivy.clock import mainthread
from kivy.properties import StringProperty, ColorProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

# ---------------- Chat Bubble ----------------
class ChatBubble(MDBoxLayout):
    text = StringProperty("")
    bg_color = ColorProperty([1, 1, 1, 1])
    text_color = ColorProperty([0, 0, 0, 1])

# ---------------- Main App ----------------
class UOKChatBot(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_history = []
        self._processing_query = False
        # Load FAQ JSON
        with open("uok_faqs.json", "r", encoding="utf-8") as f:
            self.faq_data = json.load(f)

    def build(self):
        # Load KV file here, AFTER App is initialized
        return Builder.load_file("UI.kv")

    # ---------------- Process input ----------------
    def process_query(self, text):
        if not text.strip():
            return

        if self._processing_query:
            return
        self._processing_query = True

        # Add user message to UI
        self.add_message(text, "right")
        self.conversation_history.append({'sender': 'user', 'text': text})

        # Clear input
        self.root.ids.user_input.text = ""

        def threaded_process():
            try:
                self.threaded_logic_router(text)
            finally:
                self._processing_query = False

        threading.Thread(target=threaded_process).start()

    # ---------------- Main router ----------------
    def threaded_logic_router(self, query):
        q = query.lower().strip()

        # 1️⃣ Check FAQs first
        faq_answer = self.faq_engine(q)
        if faq_answer:
            self.post_response(faq_answer)
            return

        # 2️⃣ Greetings
        if any(greet in q for greet in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            response = "Hello! I'm your UOK assistant. How can I help you today?"
            self.post_response(response)
            return

        # 3️⃣ Default fallback
        response = "🤔 I understand your question, but I need more details. Could you rephrase or ask specifically about UOK services, courses, fees, or student life?"
        self.post_response(response)

    # ---------------- FAQ engine ----------------
    def faq_engine(self, query):
        """
        Keyword-based FAQ engine with scoring and partial matching
        """
        try:
            query = query.lower()
            best_match = None
            highest_score = 0

            for category, data in self.faq_data.items():
                score = 0
                keywords = data.get("keywords", [])
                for kw in keywords:
                    kw = kw.lower()
                    if kw in query:
                        score += 3
                    elif any(kw in word or word in kw for word in query.split()):
                        score += 1

                if score > highest_score:
                    highest_score = score
                    best_match = data

            if best_match and highest_score >= 2:
                return f"📌 {best_match['answer']}"
            return None

        except Exception as e:
            print(f"FAQ Engine Error: {e}")
            return None

    # ---------------- Post response ----------------
    @mainthread
    def post_response(self, text):
        if text:
            self.conversation_history.append({'sender': 'bot', 'text': text})
            self.add_message(text, "left")

    # ---------------- Add chat bubble ----------------
    def add_message(self, text, side):
        bg = (0.05, 0.45, 0.45, 1) if side == "right" else (0.92, 0.92, 0.92, 1)
        tc = (1, 1, 1, 1) if side == "right" else (0, 0, 0, 1)
        self.root.ids.chat_container.add_widget(
            ChatBubble(
                text=text,
                bg_color=bg,
                text_color=tc,
                size_hint_y=None,
                height=40
            )
        )

if __name__ == "__main__":
    UOKChatBot().run()
