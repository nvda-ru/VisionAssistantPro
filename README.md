# Vision Assistant Pro

**Vision Assistant Pro** is a comprehensive, AI-powered add-on designed specifically for **NVDA (NonVisual Desktop Access)** users.

🚀 **Open Sourced on the International Day of Persons with Disabilities**  
This tool is released to the community to empower blind and visually impaired individuals by leveraging the latest advancements in Artificial Intelligence (Google Gemini) to solve daily digital challenges independently.

## 🌟 Why This Add-on?

Navigating the digital world presents unique challenges. Vision Assistant Pro acts as a smart, multi-modal assistant. Whether you need to solve a complex CAPTCHA, visualize a chart, translate a document instantly, or dictate text with perfect grammar, this add-on is your companion.

## ✨ Key Features

*   **🧠 Smart Translator (Auto-Swap):** Instantly translates text. If the source language matches your target, it intelligently swaps to English (or your configured secondary language).
*   **🎙️ Smart Dictation:** A powerful voice typing tool. It listens to your voice, fixes grammar, removes stutters, adds punctuation, and types the clean text directly into your active window.
*   **👁️ Object Vision:** Describes the specific control or element under your navigator cursor (e.g., describing an icon, a button, or an image).
*   **🔍 Full Screen Vision:** Scans the entire screen. You can ask the AI to describe the overall layout, read visible text, or explain what is currently displayed on your monitor.
*   **🔓 CAPTCHA Solver:** Captures, solves, and **automatically types** CAPTCHA codes. It intelligently handles various number formats and difficult images.
*   **📄 Document QA:** Chat with your documents! Supports PDF, TIFF, and Text files. You can ask the AI to summarize, explain, or extract data from them.
*   **📝 Text Refiner:** A utility menu to Summarize, Fix Grammar, or Explain selected text using AI.
*   **🎧 Audio Transcriber:** Converts audio files (MP3, WAV, OGG) into text.

## 📥 Installation

1.  Go to the **[Releases](../../releases/latest)** page of this repository.
2.  Download the latest `.nvda-addon` file.
3.  Open the file (or press Enter on it).
4.  NVDA will ask for confirmation. Select **Yes**.
5.  Restart NVDA.

## ⌨️ Shortcuts

| Shortcut | Function |
| :--- | :--- |
| `NVDA + Shift + T` | **Smart Translator** (Selection or Object) |
| `NVDA + Shift + S` | **Smart Dictation** (Voice Typing) |
| `NVDA + Shift + R` | **Text Refiner** (Menu for Summary, Grammar, etc.) |
| `NVDA + Shift + 6` | **CAPTCHA Solver** (Auto-Type) |
| `NVDA + Shift + V` | **Object Vision** (Describe focused object) |
| `NVDA + Shift + O` | **Full Screen Vision** |
| `NVDA + Shift + D` | **Document QA** (Chat with Files) |
| `NVDA + Shift + A` | **Transcribe Audio File** |

## ⚙️ Configuration

Go to **NVDA Menu > Preferences > Settings > Vision Assistant Pro**:
1.  **API Key:** Enter your Google Gemini API Key.
2.  **Model:** Choose between `gemini-2.5-flash-lite` (Fastest) or other variants.
3.  **Languages:** Set your Source, Target, and AI Response languages.
4.  **Custom Prompts:** Define your own workflows using variables like `[selection]`, `[file_ocr]`, etc.

## 🤝 Contributing

This project is open-source. Contributions and bug reports are welcome to make this tool even better for the community.