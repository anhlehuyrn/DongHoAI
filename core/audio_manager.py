import os
import time
import threading
import asyncio
from config import AUDIO_CACHE_DIR, TEMP_AUDIO_FILE, TTS_VOICES

class AudioManager:
    def __init__(self):
        self.is_playing = False
        self.last_triggered_class = None
        self.last_trigger_time = 0
        self.debounce_duration = 2.5
        self.on_finished_callback = None
        
        self._init_mixer()

    def _init_mixer(self):
        try:
            from pygame import mixer
            mixer.init()
            print("[AudioManager] Khởi tạo Pygame Audio Mixer thành công!", flush=True)
        except Exception as e:
            print(f"[AudioManager] Lỗi khởi tạo Pygame Mixer: {e}", flush=True)

    def get_cached_audio_path(self, class_name, mode, lang):
        clean_class = class_name.lower().replace(" ", "_")
        filename = f"{clean_class}.mp3"
        return os.path.join(AUDIO_CACHE_DIR, lang, mode, filename)

    def play_character_description(self, class_name, mode, lang, text=None, on_finished=None):
        current_time = time.time()
        
        # Debounce to prevent rapid re-triggering of the exact same audio
        if class_name == self.last_triggered_class and (current_time - self.last_trigger_time) < self.debounce_duration:
            return

        self.last_triggered_class = class_name
        self.last_trigger_time = current_time
        self.on_finished_callback = on_finished

        # Check local cache first
        cached_file = self.get_cached_audio_path(class_name, mode, lang)
        
        if os.path.exists(cached_file):
            # Play 0ms latency pre-cached file
            threading.Thread(target=self._play_file, args=(cached_file,), daemon=True).start()
        elif text:
            # Generate dynamically on the fly
            threading.Thread(target=self._generate_and_play, args=(text, lang), daemon=True).start()

    def play_dynamic_speech(self, text, lang="vi", on_finished=None):
        """Used by Voice Q&A Assistant to speak AI responses."""
        self.on_finished_callback = on_finished
        threading.Thread(target=self._generate_and_play, args=(text, lang), daemon=True).start()

    def _play_file(self, filepath):
        self.is_playing = True
        try:
            from pygame import mixer
            mixer.music.load(filepath)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.05)
        except Exception as e:
            print(f"[AudioManager] Lỗi phát file audio: {e}", flush=True)
        finally:
            self.is_playing = False
            if self.on_finished_callback:
                cb = self.on_finished_callback
                self.on_finished_callback = None
                cb()

    def _generate_and_play(self, text, lang):
        self.is_playing = True
        try:
            # 1. Try edge-tts first (high naturalness)
            success = self._try_edge_tts(text, lang, TEMP_AUDIO_FILE)
            
            # 2. Fallback to gTTS if edge-tts fails
            if not success:
                self._try_gtts(text, lang, TEMP_AUDIO_FILE)

            # 3. Play generated file
            if os.path.exists(TEMP_AUDIO_FILE):
                from pygame import mixer
                mixer.music.load(TEMP_AUDIO_FILE)
                mixer.music.play()
                while mixer.music.get_busy():
                    time.sleep(0.05)
        except Exception as e:
            print(f"[AudioManager] Lỗi TTS: {e}", flush=True)
        finally:
            self.is_playing = False
            if self.on_finished_callback:
                cb = self.on_finished_callback
                self.on_finished_callback = None
                cb()

    def _try_edge_tts(self, text, lang, output_path):
        try:
            import edge_tts
            voice = TTS_VOICES.get(lang, TTS_VOICES["vi"])
            communicate = edge_tts.Communicate(text, voice)
            
            # Run async call in sync context
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            if loop.is_running():
                # In running loop, run in a separate temporary loop or executor
                new_loop = asyncio.new_event_loop()
                new_loop.run_until_complete(communicate.save(output_path))
                new_loop.close()
            else:
                loop.run_until_complete(communicate.save(output_path))
            return True
        except Exception as e:
            print(f"[AudioManager] Edge-TTS không khả dụng, dùng fallback gTTS: {e}", flush=True)
            return False

    def _try_gtts(self, text, lang, output_path):
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"[AudioManager] gTTS Error: {e}", flush=True)
            return False

    def stop(self):
        try:
            from pygame import mixer
            if mixer.get_init():
                mixer.music.stop()
        except Exception:
            pass
        self.is_playing = False
