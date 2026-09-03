# DongHo.AI: Multimodal Interactive Heritage Assistant

**DongHo.AI** là hệ thống trợ lý ảo tương tác đa phương thức (Multimodal AI) dành cho di sản văn hóa tranh dân gian Đông Hồ (tiêu biểu là bức tranh *Đám cưới chuột*). Dự án kết hợp thị giác máy tính (**Computer Vision**), theo dõi xúc giác ngón tay (**Dwell-Time Finger Tracking**), âm thanh siêu tốc 0ms (**Edge-TTS Cache**) và **Trợ lý Đối thoại Giọng nói (Voice Q&A Assistant với Google Gemini)** để mang lại trải nghiệm thuyết minh sống động theo từng độ tuổi và hỗ trợ người khiếm thị.

---

## 🌟 Các Tính Năng Nâng Cấp Nổi Bật

1. **Khắc phục triệt để lỗi "Chạm ảo" (Dwell-Time & EMA Smoothing):**
   - Bộ lọc **Exponential Moving Average (EMA)** làm mượt tọa độ đầu ngón tay trỏ.
   - Cơ chế **Dwell-Time (Giữ ngón 0.8 giây)**: Hiển thị vòng tròn tiến trình (Progress Ring) trực quan quanh đầu ngón tay trước khi kích hoạt âm thanh, loại bỏ tình trạng quẹt tay vô tình.
2. **Âm thanh Tự nhiên & Không Độ Trễ (Edge-TTS Offline Cache):**
   - Kho âm thanh MP3 chất lượng cao tạo bởi Microsoft Edge-TTS (giọng Hoài My / Nam Minh truyền cảm).
   - Phát tức thì trong **< 0.05 giây** khi chạm vào nhân vật.
3. **Trợ lý AI Đàm thoại Giọng nói (Voice-to-Voice AI với Gemini):**
   - Nhấn phím `SPACE` để kích hoạt chế độ lắng nghe giọng nói.
   - Nhận diện câu hỏi của người dùng qua Micro $\rightarrow$ Gemini LLM giải thích ngữ cảnh bức tranh $\rightarrow$ Đọc câu trả lời bằng giọng nói.
4. **Phân Tầng Thuyết Minh 4 Chế Độ Độ Tuổi & 3 Ngôn Ngữ:**
   - **Child (Trẻ em):** Giọng điệu vui tươi, gần gũi, nhân hoá động vật.
   - **Elderly (Người cao tuổi):** Nhấn mạnh giá trị văn hoá, đạo lý truyền thống.
   - **Blindness (Khiếm thị / Xúc giác):** Mô tả chi tiết hình khối, âm thanh và vị trí.
   - **Adult (Người lớn / Nghiên cứu):** Phân tích ý nghĩa trào phúng và nghệ thuật khắc gỗ.
   - Ngôn ngữ hỗ trợ: **Tiếng Việt (`V`), Tiếng Anh (`E`), Tiếng Trung (`Z`)**.

---

## 📁 Cấu Trúc Mã Nguồn

```
DongHo_AIcode/
├── config.py                  # Cấu hình ngưỡng Dwell-time, đường dẫn, phím tắt, giọng đọc
├── knowledge.json             # Cơ sở tri thức tranh Đông Hồ đa chế độ & đa ngôn ngữ
├── donghoai_best.pt           # Model trọng số YOLOv8
├── requirements.txt           # Danh sách thư viện cần cài đặt
├── generate_audio_cache.py    # Script tự động sinh kho file MP3 chất lượng cao
├── audio_cache/               # Thư mục lưu trữ file âm thanh (0ms delay)
├── core/
│   ├── detector.py            # Quản lý YOLOv8 Local & Roboflow API
│   ├── hand_tracker.py        # MediaPipe Hand Tracking + EMA Smoothing + Dwell Engine
│   ├── audio_manager.py       # Quản lý phát âm thanh đa luồng & Edge-TTS
│   ├── voice_assistant.py     # Module STT thu âm Micro + Gemini LLM Q&A
│   └── ui_renderer.py         # Vẽ HUD giao diện, Dwell-ring và trạng thái Voice AI
└── main.py                    # Chương trình chính
```

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### 2. Thiết lập Gemini API Key (cho tính năng hỏi đáp giọng nói):
* Đặt biến môi trường `GEMINI_API_KEY`:
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```
*(Hoặc điền trực tiếp vào file `config.py`)*

### 3. Tạo sẵn kho âm thanh MP3 (Khuyên dùng để không bị trễ):
```bash
python generate_audio_cache.py
```

### 4. Khởi chạy ứng dụng:
```bash
python main.py
```

---

## ⌨️ Phím Tắt Điều Khiển

| Phím | Chức năng |
| :---: | :--- |
| `1` | Chuyển chế độ **Trẻ Em (Child)** |
| `2` | Chuyển chế độ **Người Cao Tuổi (Elderly)** |
| `3` | Chuyển chế độ **Người Khiếm Thị (Blindness/Tactile)** |
| `4` | Chuyển chế độ **Người Lớn (Adult)** |
| `V` | Đổi ngôn ngữ sang **Tiếng Việt** |
| `E` | Đổi ngôn ngữ sang **Tiếng Anh** |
| `Z` | Đổi ngôn ngữ sang **Tiếng Trung** |
| `SPACE` | **Kích hoạt Micro để hỏi đáp Voice AI với Gemini** |
| `Q` | Thoát chương trình |