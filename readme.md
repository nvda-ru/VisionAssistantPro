Vision Assistant Pro Documentation

# Vision Assistant Pro

**Vision Assistant Pro** is an advanced, multi-modal AI assistant for NVDA. It leverages Google's Gemini models to provide intelligent screen reading, translation, voice dictation, and document analysis capabilities.

_This add-on was released to the community in honor of the International Day of Persons with Disabilities._

## 1. Setup & Configuration

Go to **NVDA Menu > Preferences > Settings > Vision Assistant Pro**.

- **API Key:** Required. Get a free key from [Google AI Studio](https://aistudio.google.com/).
- **Model:** Choose `gemini-2.5-flash-lite` (Fastest) or standard Flash models.
- **Languages:** Set Source, Target, and AI Response languages.
- **Smart Swap:** Automatically swaps languages if the source text matches the target language.

## 2. Global Shortcuts

To ensure maximum compatibility with laptop layouts, all shortcuts use **NVDA + Control + Shift**.

| Shortcut                    | Function             | Description                                                                 |
|-----------------------------|----------------------|-----------------------------------------------------------------------------|
| NVDA+Ctrl+Shift+T           | Smart Translator     | Translates the text under the navigator cursor. Prioritizes selection.     |
| NVDA+Ctrl+Shift+Y           | Clipboard Translator | Translates clipboard content. **Recommended for web browsers**.            |
| NVDA+Ctrl+Shift+S           | Smart Dictation      | Converts speech to text. Press once to start, again to stop and type.       |
| NVDA+Ctrl+Shift+R           | Text Refiner         | Summarize, Fix Grammar, Explain, or run **Custom Prompts**.                 |
| NVDA+Ctrl+Shift+C           | CAPTCHA Solver       | Captures and solves CAPTCHA automatically.                                 |
| NVDA+Ctrl+Shift+V           | Object Vision        | Describes the navigator object with follow-up chat.                         |
| NVDA+Ctrl+Shift+O           | Full Screen Vision   | Analyzes entire screen layout and content.                                  |
| NVDA+Ctrl+Shift+D           | Document Analysis    | Chat with PDF/TXT/MD/PY files.                                              |
| NVDA+Ctrl+Shift+F           | File OCR             | Direct OCR from image/PDF file.                                             |
| NVDA+Ctrl+Shift+A           | Audio Transcription  | Transcribe MP3/WAV/OGG files.                                               |
| NVDA+Ctrl+Shift+L           | Last Translation     | Re-read last translation without API.                                      |
| NVDA+Ctrl+Shift+U           | Update Check         | Check GitHub for latest version.                                            |

## 3. Custom Prompts & Variables

Create commands in Settings: `Name:Prompt Text` (separate with `|` or new lines).

### Available Variables

| Variable         | Description                                      | Input Type       |
|------------------|--------------------------------------------------|------------------|
| `[selection]`    | Currently selected text                          | Text             |
| `[clipboard]`    | Clipboard content                                | Text             |
| `[screen_obj]`   | Screenshot of navigator object                   | Image            |
| `[screen_full]`  | Full screen screenshot                           | Image            |
| `[file_ocr]`     | Select image/PDF/TIFF (defaults to "Extract text")| Image, PDF, TIFF |
| `[file_read]`    | Select text document                             | TXT, Code, PDF   |
| `[file_audio]`   | Select audio file                                | MP3, WAV, OGG    |

### Example Custom Prompts

- **Quick OCR:** `My OCR:[file_ocr]`
- **Translate Image:** `Translate Img:Extract text from this image and translate to Persian. [file_ocr]`
- **Analyze Audio:** `Summarize Audio:Listen to this recording and summarize the main points. [file_audio]`
- **Code Debugger:** `Debug:Find bugs in this code and explain them: [selection]`

**Note:** File uploads limited to 15MB. Internet required. Multi-page TIFFs supported.