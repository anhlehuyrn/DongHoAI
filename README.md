# DongHo.AI: Multimodal Interactive Heritage Assistant

**DongHo.AI** is a multimodal artificial intelligence system designed for interactive exploration of Vietnamese Dong Ho folk paintings (specifically the iconic woodcut masterpiece *"The Mice's Wedding"* — *Đám cưới chuột*). 

The system bridges cultural heritage, computer vision, and cognitive accessibility by combining **Object Detection (YOLOv8)**, **Tactile Dwell-Time Finger Tracking (MediaPipe)**, **Zero-Latency Natural Acoustic Synthesis (Edge-TTS)**, and an **Interactive Voice-to-Voice AI Assistant (Google Gemini LLM)** tailored to diverse audience demographics and visually impaired communities.

This project serves as a research proof-of-concept (PoC) exploring Multimodal Human-Computer Interaction (HCI), semantic ontology mapping, and assistive technologies for cultural heritage preservation.
Video demo: https://share.weiyun.com/nUPhFc3k

---

## 🌟 Key Features

1. **Anti-Jitter & Tactile Dwell-Time Interaction:**
   - **Exponential Moving Average (EMA) Smoothing:** Eliminates fingertip coordinate jitter and tracking noise.
   - **Dwell-Time Engine (0.8s hold):** Requires the user to hold their index finger steadily over a character for 0.8 seconds before triggering, preventing accidental triggers and false touches.
   - **Visual Dwell Progress Ring:** Renders an animated circular progress HUD around the fingertip in real time.

2. **Zero-Latency Natural Acoustic Synthesis (Edge-TTS Offline Cache):**
   - High-fidelity natural speech synthesis powered by Microsoft Edge-TTS (e.g., *Hoài My* for Vietnamese, *Jenny* for English).
   - Pre-rendered offline audio cache (`audio_cache/`) ensuring instant **< 50ms response latency** upon touch.

3. **Interactive Voice-to-Voice AI Guide (Google Gemini LLM):**
   - Press `SPACE` to open a real-time conversational channel.
   - The user speaks a natural language question through the microphone $\rightarrow$ Speech-to-Text (STT) $\rightarrow$ Gemini LLM processes the cultural context $\rightarrow$ Synthesizes a concise, age-appropriate spoken response.

4. **Multi-Tiered Audience Stratification & Multilingual Support:**
   - **Child Mode (`1`):** Engaging, friendly, fairy-tale style explanations with animal personification.
   - **Elderly Mode (`2`):** Respectful tone emphasizing traditional moral values and historical folklore.
   - **Blindness / Tactile Mode (`3`):** Descriptive spatial cues, tactile attributes, soundscapes, and orientation details.
   - **Adult / Research Mode (`4`):** Deep analytical insights into feudal satire, socio-cultural critique, and woodblock printmaking techniques.
   - **Languages Supported:** Vietnamese (`V`), English (`E`), Chinese (`Z`).

---

## 📁 Repository Structure

```
DongHoAI/
├── config.py                  # System hyperparameters, voice mappings, API keys & paths
├── knowledge.json             # Stratified cultural ontology knowledge base
├── donghoai_best.pt           # Fine-tuned YOLOv8 model weights
├── requirements.txt           # Python dependency specifications
├── generate_audio_cache.py    # Utility script for pre-generating offline MP3 speech cache
├── audio_cache/               # Pre-rendered 0ms acoustic files (84 items)
│   ├── vi/                    # Vietnamese audio bank (child, elderly, blindness, adult)
│   ├── en/                    # English audio bank
│   └── zh/                    # Chinese audio bank
├── core/
│   ├── detector.py            # YOLOv8 local inference & Roboflow API fallback
│   ├── hand_tracker.py        # MediaPipe hand landmarks, EMA smoothing & Dwell-Time engine
│   ├── audio_manager.py       # Non-blocking audio playback & Edge-TTS engine
│   ├── voice_assistant.py     # Microphone STT & Gemini LLM conversational agent
│   └── ui_renderer.py         # On-screen HUD, Bounding Box renderer & Dwell progress arc
└── main.py                    # Main application loop & camera stream controller
```

---

## 🚀 Installation & Setup

### 1. Install Dependencies
Ensure you have Python 3.10+ installed:
```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key (For Interactive Voice Q&A)
Set your `GEMINI_API_KEY` as an environment variable:
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```
*(Or specify it directly in `config.py`)*

### 3. Generate Offline Audio Cache (Recommended for 0ms latency)
Generate the complete suite of 84 localized speech files:
```bash
python generate_audio_cache.py
```

### 4. Launch the Interactive Application
```bash
python main.py
```

---

## ⌨️ Interactive Controls

| Key | Action |
| :---: | :--- |
| `1` | Switch to **Child Mode** |
| `2` | Switch to **Elderly Mode** |
| `3` | Switch to **Blindness / Tactile Mode** |
| `4` | Switch to **Adult / Research Mode** |
| `V` | Switch audio language to **Vietnamese** |
| `E` | Switch audio language to **English** |
| `Z` | Switch audio language to **Chinese** |
| `SPACE` | **Activate Voice AI Assistant (Speak your question into microphone)** |
| `Q` | Safely quit the application |

---

## 🔬 Research Significance & Future Roadmap

- **Empirical HCI Validation:** Conducting user experience studies with visually impaired participants to evaluate tactile perception and cognitive load.
- **Physical Tactile Canvas:** Integrating 3D-relief printed woodcuts with capacitive touch sensors to bridge physical tactile feedback with digital AI narration.
- **Instance Segmentation (YOLOv8-Seg):** Transitioning from rectangular bounding boxes to precise polygon masks for intricate folk art details.
