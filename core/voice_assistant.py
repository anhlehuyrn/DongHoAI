import os
import threading
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

class VoiceAssistant:
    def __init__(self, audio_manager, knowledge_base=None):
        self.audio_manager = audio_manager
        self.knowledge_base = knowledge_base or {}
        self.api_key = GEMINI_API_KEY
        
        # State: IDLE, LISTENING, THINKING, SPEAKING
        self.state = "IDLE"
        self.last_user_query = ""
        self.last_ai_response = ""
        self.current_context_character = None
        self.current_mode = "adult"
        self.current_lang = "vi"

        self.recognizer = None
        self._init_speech_recognizer()

    def _init_speech_recognizer(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            print("[VoiceAssistant] Khởi tạo Bộ thu âm (SpeechRecognition) thành công!", flush=True)
        except Exception as e:
            print(f"[VoiceAssistant] Cảnh báo speech_recognition: {e}", flush=True)

    def set_context(self, character_name, mode, lang):
        self.current_context_character = character_name
        self.current_mode = mode
        self.current_lang = lang

    def start_listening_async(self):
        """Kích hoạt lắng nghe người dùng trong một luồng riêng biệt"""
        if self.state != "IDLE":
            return
        threading.Thread(target=self._listen_and_answer_worker, daemon=True).start()

    def _listen_and_answer_worker(self):
        if self.recognizer is None:
            self._fallback_text_query("Microphone STT library not available.")
            return

        import speech_recognition as sr

        self.state = "LISTENING"
        print("[VoiceAssistant] Đang lắng nghe câu hỏi từ người dùng...", flush=True)

        user_text = ""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                # Listen up to 6 seconds
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=8)
            
            self.state = "THINKING"
            print("[VoiceAssistant] Đang chuyển giọng nói thành văn bản (STT)...", flush=True)
            
            stt_lang = "vi-VN" if self.current_lang == "vi" else ("en-US" if self.current_lang == "en" else "zh-CN")
            user_text = self.recognizer.recognize_google(audio, language=stt_lang)
            print(f"[VoiceAssistant] Người dùng hỏi: '{user_text}'", flush=True)
            self.last_user_query = user_text

        except sr.WaitTimeoutError:
            print("[VoiceAssistant] Hết thời gian chờ (Timeout - không nghe thấy giọng nói).", flush=True)
            self.state = "IDLE"
            return
        except sr.UnknownValueError:
            print("[VoiceAssistant] Không nhận diện được âm thanh rõ ràng.", flush=True)
            msg = "Xin lỗi, tôi chưa nghe rõ câu hỏi. Bạn vui lòng nói lại nhé!" if self.current_lang == "vi" else "Sorry, I could not hear your question clearly."
            self.state = "SPEAKING"
            self.audio_manager.play_dynamic_speech(msg, lang=self.current_lang, on_finished=self._reset_state)
            return
        except Exception as e:
            print(f"[VoiceAssistant] Lỗi micro: {e}", flush=True)
            self.state = "IDLE"
            return

        # Query LLM (Gemini)
        self._query_llm_and_speak(user_text)

    def _fallback_text_query(self, query):
        self.last_user_query = query
        self.state = "THINKING"
        self._query_llm_and_speak(query)

    def _query_llm_and_speak(self, user_question):
        char_info = ""
        if self.current_context_character and self.current_context_character in self.knowledge_base:
            char_data = self.knowledge_base[self.current_context_character]
            char_info = str(char_data.get(self.current_mode, {}))

        prompt = f"""
Bạn là Hướng dẫn viên Di sản Văn hóa chuyên về tranh dân gian Đông Hồ Việt Nam.
Bức tranh đang thuyết minh: "Đám cưới chuột".
Nhân vật/Chi tiết người dùng vừa chạm vào: {self.current_context_character or 'Tổng thể bức tranh'}.
Thông tin cơ sở về nhân vật: {char_info}
Chế độ người nghe (Audience Mode): {self.current_mode} (child: Trẻ em, elderly: Người cao tuổi, blindness: Người khiếm thị, adult: Người lớn/Nghiên cứu).
Ngôn ngữ trả lời: {self.current_lang}.

Câu hỏi của người dùng: "{user_question}"

QUY TẮC PHẢN HỒI:
1. Trả lời trực tiếp, súc tích trong 2-3 câu ngắn để người dùng dễ nghe.
2. Tone giọng phù hợp với độ tuổi:
   - child: Vui tươi, dễ thương, dùng phép nhân hóa sinh động.
   - elderly: Tôn trọng, nhấn mạnh giá trị văn hóa truyền thống và đạo lý.
   - blindness: Miêu tả xúc giác, vị trí không gian, hình dung trực quan chi tiết.
   - adult: Phân tích ý nghĩa trào phúng, nghệ thuật khắc gỗ dân gian.
3. Không dùng các ký tự markdown như dấu sao (*), gạch đầu dòng, chỉ trả về văn bản thuần để đọc bằng giọng nói.
"""

        ai_response = self._call_gemini_api(prompt)
        print(f"[VoiceAssistant] AI trả lời: {ai_response}", flush=True)
        self.last_ai_response = ai_response

        self.state = "SPEAKING"
        self.audio_manager.play_dynamic_speech(ai_response, lang=self.current_lang, on_finished=self._reset_state)

    def _call_gemini_api(self, prompt):
        # 1. Try google.genai (New SDK)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key) if self.api_key else genai.Client()
            response = client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            pass

        # 2. Try google.generativeai (Legacy SDK)
        try:
            import google.generativeai as genai_legacy
            if self.api_key:
                genai_legacy.configure(api_key=self.api_key)
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e2:
            pass

        # Fallback offline response
        if self.current_lang == "vi":
            return f"Nhân vật {self.current_context_character} trong tranh Đám cưới chuột thể hiện nét độc đáo của nghệ thuật dân gian Đông Hồ."
        return f"The {self.current_context_character} character represents a unique satirical tradition in Dong Ho folk art."

    def _reset_state(self):
        self.state = "IDLE"
