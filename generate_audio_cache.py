import os
import json
import asyncio
import sys

# Force UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from config import KNOWLEDGE_BASE_FILE, AUDIO_CACHE_DIR, TTS_VOICES

async def generate_single_audio(text, lang, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Try Edge-TTS first
    try:
        import edge_tts
        voice = TTS_VOICES.get(lang, TTS_VOICES["vi"])
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        print(f"  [OK - EdgeTTS] {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"  [Fallback gTTS] {os.path.basename(output_path)} (Reason: {e})")

    # Fallback to gTTS
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        print(f"  [OK - gTTS] {os.path.basename(output_path)}")
        return True
    except Exception as e2:
        print(f"  [ERROR] Không thể sinh audio cho {output_path}: {e2}")
        return False

async def generate_all_cache():
    print("==================================================")
    print("   TẠO KHO ÂM THANH OFFLINE CHO TRANH ĐÔNG HỒ    ")
    print("==================================================")

    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        print(f"Lỗi: Không tìm thấy file {KNOWLEDGE_BASE_FILE}")
        return

    with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
        knowledge = json.load(f)

    tasks = []
    total_count = 0

    for character_name, modes in knowledge.items():
        clean_name = character_name.lower().replace(" ", "_")
        for mode, lang_data in modes.items():
            if isinstance(lang_data, dict):
                for lang, text in lang_data.items():
                    out_path = os.path.join(AUDIO_CACHE_DIR, lang, mode, f"{clean_name}.mp3")
                    tasks.append((text, lang, out_path))
                    total_count += 1
            elif isinstance(lang_data, str):
                # Default lang vi
                out_path = os.path.join(AUDIO_CACHE_DIR, "vi", mode, f"{clean_name}.mp3")
                tasks.append((lang_data, "vi", out_path))
                total_count += 1

    print(f"Phát hiện tổng cộng: {total_count} mục âm thanh cần sinh.")
    print(f"Đang tiến hành tạo file vào thư mục: {AUDIO_CACHE_DIR}\n")

    for text, lang, out_path in tasks:
        await generate_single_audio(text, lang, out_path)

    print("\n Hoàn tất sinh kho âm thanh! Toàn bộ âm thanh khi chạm sẽ phát tức thì (0ms latency).")

if __name__ == "__main__":
    asyncio.run(generate_all_cache())
