# Vision Assistant Pro

**Vision Assistant Pro** is a comprehensive accessibility add-on for NVDA that integrates Google's Gemini AI models. It provides a suite of tools designed to assist blind and visually impaired users with daily digital tasks, ranging from image recognition to advanced translation and document processing.

*Note: This project was originally released to the community in honor of the **International Day of Persons with Disabilities**, aiming to leverage AI for greater digital independence.*

## Key Features

*   **Smart Translation:** Automatically detects languages and translates text. Includes a dedicated clipboard mode for better compatibility with web browsers.
*   **Smart Dictation:** A voice typing tool that listens to speech, corrects grammar/punctuation, and types the text directly into the active application.
*   **Visual Analysis:** Describes the object under the navigator cursor or the entire screen content. Supports interactive follow-up questions via a chat dialog.
*   **CAPTCHA Solver:** Recognizes CAPTCHA images from the screen and automatically types the result.
*   **Document Analysis:** Allows users to select documents (PDF, Images, Text) and ask questions about their content.
*   **Text Refiner:** A utility menu to summarize, explain, or correct the grammar of selected text.
*   **Audio Transcription:** Converts audio files (MP3, WAV, OGG) to text.
*   **Auto-Update:** Automatically checks for new versions and installs them seamlessly.

## Installation

1.  Download the latest `.nvda-addon` file from the **[Latest Releases](https://github.com/mahmoodhozhabri/VisionAssistantPro/releases/latest)** page.
2.  Open the file to launch the NVDA add-on installer.
3.  Confirm the installation and restart NVDA.

## Configuration

1.  Go to **NVDA Menu > Preferences > Settings > Vision Assistant Pro**.
2.  **API Key:** Enter your Google Gemini API Key (obtainable from Google AI Studio).
3.  **Model:** Select the desired AI model (e.g., `gemini-2.5-flash-lite`).
4.  **Languages:** Configure Source, Target, and AI Response languages.

## Shortcuts

To prevent conflicts with system or laptop layouts, all shortcuts use **NVDA+Control+Shift**:

*   `NVDA+Ctrl+Shift+T`: Translate Text/Object
*   `NVDA+Ctrl+Shift+Y`: Translate Clipboard (Recommended for Browsers)
*   `NVDA+Ctrl+Shift+S`: Smart Dictation (Toggle)
*   `NVDA+Ctrl+Shift+V`: Describe Navigator Object
*   `NVDA+Ctrl+Shift+O`: Describe Full Screen
*   `NVDA+Ctrl+Shift+C`: Solve CAPTCHA
*   `NVDA+Ctrl+Shift+R`: Text Refiner Menu
*   `NVDA+Ctrl+Shift+D`: Document Analysis
*   `NVDA+Ctrl+Shift+F`: File OCR
*   `NVDA+Ctrl+Shift+A`: Transcribe Audio File
*   `NVDA+Ctrl+Shift+L`: Read Last Translation
*   `NVDA+Ctrl+Shift+U`: Check for Updates

## Contributing

We welcome contributions from the community! Whether you want to report a bug, suggest a new feature, or improve the code, your help is appreciated.

Feel free to fork the repository and submit a Pull Request on **[GitHub](https://github.com/mahmoodhozhabri/VisionAssistantPro)**.

## License

This project is open-source and distributed under the MIT License.