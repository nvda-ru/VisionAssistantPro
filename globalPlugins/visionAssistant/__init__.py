# -*- coding: utf-8 -*-

import addonHandler
import globalPluginHandler
import config
import gui
import wx
import json
import threading
import ui
import api
import speech
import logging
import textInfos
import os
import base64
import io
import ctypes
import re
import tempfile
import time
import datetime
from urllib import request, error

log = logging.getLogger(__name__)
addonHandler.initTranslation()

# --- تنظیمات سیستمی ---
winmm = ctypes.windll.winmm
user32 = ctypes.windll.user32

MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

BASE_LANGUAGES = [
    ("Arabic", "ar"), ("Chinese", "zh"), ("Dutch", "nl"), ("English", "en"),
    ("French", "fr"), ("German", "de"), ("Italian", "it"), ("Japanese", "ja"),
    ("Persian", "fa"), ("Portuguese", "pt"), ("Russian", "ru"),
    ("Spanish", "es"), ("Turkish", "tr")
]
SOURCE_LIST = [("Auto-detect", "auto")] + BASE_LANGUAGES
SOURCE_NAMES = [x[0] for x in SOURCE_LIST]
TARGET_LIST = BASE_LANGUAGES
TARGET_NAMES = [x[0] for x in TARGET_LIST]

confspec = {
    "proxy_url": "string(default='')",
    "api_key": "string(default='')",
    "model_name": "string(default='gemini-2.5-flash-lite')",
    "target_language": "string(default='Persian')",
    "source_language": "string(default='Auto-detect')",
    "ai_response_language": "string(default='Persian')",
    "smart_swap": "boolean(default=True)",
    "captcha_mode": "string(default='navigator')",
    "custom_prompts": "string(default='')"
}

# --- توابع کمکی ---
def clean_markdown(text):
    if not text: return ""
    text = re.sub(r'\*\*|__|[*_]', '', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*-\s+', '', text, flags=re.MULTILINE)
    return text.strip()

def move_mouse(x, y):
    try:
        user32.SetCursorPos(int(x), int(y))
        ui.message(f"Mouse moved to {x}, {y}")
    except: ui.message("Failed to move mouse.")

def play_sound(freq, dur):
    import winsound
    winsound.Beep(freq, dur)

def send_ctrl_v():
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002
    try:
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    except: pass

def process_tiff_pages(path):
    pages_data = []
    # Suppress wxWidgets warnings (TIFFReadDirectory errors)
    no_log = wx.LogNull() 
    try:
        img_count = wx.Image.GetImageCount(path, wx.BITMAP_TYPE_TIFF)
        if img_count == 0: img_count = 1
        
        for i in range(img_count):
            try:
                img = wx.Image(path, wx.BITMAP_TYPE_TIFF, i)
                if img.IsOk():
                    stream = io.BytesIO()
                    img.SaveFile(stream, wx.BITMAP_TYPE_JPEG)
                    pages_data.append(base64.b64encode(stream.getvalue()).decode('utf-8'))
            except: continue
    except: pass
    return pages_data

# --- پرامپت‌ها ---
PROMPT_TRANSLATE = """
Role: Professional Translator.
Config: Primary={target_lang}, Fallback={swap_target}, SmartSwap={smart_swap}.
Task:
1. Detect input language.
2. If SmartSwap=True AND Input==Primary, translate to Fallback.
3. Else, translate to Primary.
4. Output ONLY the translation.
"""

PROMPT_UI_LOCATOR = "Analyze UI (Size: {width}x{height}). Request: '{query}'. Output JSON: {{\"x\": int, \"y\": int, \"found\": bool}}."

class VisionQADialog(wx.Dialog):
    def __init__(self, parent, title, initial_text, context_data, callback_fn, extra_info=None):
        super(VisionQADialog, self).__init__(parent, title=title, size=(550, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.context_data = context_data 
        self.callback_fn = callback_fn
        self.extra_info = extra_info
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, label="AI Response:")
        mainSizer.Add(lbl, 0, wx.ALL, 5)
        self.outputArea = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(self.outputArea, 1, wx.EXPAND | wx.ALL, 5)
        
        clean_init = clean_markdown(initial_text)
        self.outputArea.AppendText(f"AI: {clean_init}\n")
        
        self.moveMouseBtn = wx.Button(self, label="Move Mouse")
        self.moveMouseBtn.Hide()
        self.moveMouseBtn.Bind(wx.EVT_BUTTON, self.onMoveMouse)
        self.target_coords = None
        mainSizer.Add(self.moveMouseBtn, 0, wx.ALL, 5)

        inputLbl = wx.StaticText(self, label="Ask:")
        mainSizer.Add(inputLbl, 0, wx.ALL, 5)
        self.inputArea = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        mainSizer.Add(self.inputArea, 0, wx.EXPAND | wx.ALL, 5)
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.askBtn = wx.Button(self, label="Send")
        self.closeBtn = wx.Button(self, wx.ID_CANCEL, label="Close")
        btnSizer.Add(self.askBtn, 0, wx.ALL, 5)
        btnSizer.Add(self.closeBtn, 0, wx.ALL, 5)
        mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)
        
        self.SetSizer(mainSizer)
        self.inputArea.SetFocus()
        self.askBtn.Bind(wx.EVT_BUTTON, self.onAsk)
        self.inputArea.Bind(wx.EVT_TEXT_ENTER, self.onAsk)
        
        wx.CallLater(300, ui.message, clean_init)

    def onAsk(self, event):
        question = self.inputArea.Value
        if not question.strip(): return
        self.outputArea.AppendText(f"\nYou: {question}\n")
        self.inputArea.Clear()
        ui.message("Thinking...")
        is_locator = any(k in question.lower() for k in ["find", "locate", "where", "کجاست", "پیدا"])
        threading.Thread(target=self.process_question, args=(question, is_locator)).start()

    def process_question(self, question, is_locator):
        response_text, coords = self.callback_fn(self.context_data, question, is_locator, self.extra_info)
        clean_resp = clean_markdown(response_text)
        wx.CallAfter(self.update_response, clean_resp, coords)

    def update_response(self, text, coords):
        self.outputArea.AppendText(f"AI: {text}\n")
        self.outputArea.ShowPosition(self.outputArea.GetLastPosition())
        ui.message(text)
        if coords:
            self.target_coords = coords
            self.moveMouseBtn.SetLabel(f"Move Mouse to ({coords[0]}, {coords[1]})")
            self.moveMouseBtn.Show()
            self.Layout()
            ui.message("Element found.")
        else:
            self.moveMouseBtn.Hide()

    def onMoveMouse(self, event):
        if self.target_coords: move_mouse(*self.target_coords)

class ResultDialog(wx.Dialog):
    def __init__(self, parent, title, content):
        super().__init__(parent, title=title, size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        clean_content = clean_markdown(content)
        self.text_ctrl = wx.TextCtrl(self, value=clean_content, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(self, wx.ID_OK, label="Close"))
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Centre()

class SettingsPanel(gui.settingsDialogs.SettingsPanel):
    title = "Vision Assistant Pro"
    def makeSettings(self, settingsSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        
        self.apiKey = sHelper.addLabeledControl("Gemini API Key:", wx.TextCtrl)
        self.apiKey.Value = config.conf["VisionAssistant"]["api_key"]
        
        self.model = sHelper.addLabeledControl("AI Model:", wx.Choice, choices=MODELS)
        try: self.model.SetSelection(MODELS.index(config.conf["VisionAssistant"]["model_name"]))
        except: self.model.SetSelection(0)

        self.proxyUrl = sHelper.addLabeledControl("Proxy URL:", wx.TextCtrl)
        self.proxyUrl.Value = config.conf["VisionAssistant"]["proxy_url"]
        
        sHelper.addItem(wx.StaticText(self, label="--- Languages ---"))
        self.sourceLang = sHelper.addLabeledControl("Source:", wx.Choice, choices=SOURCE_NAMES)
        try: self.sourceLang.SetSelection(SOURCE_NAMES.index(config.conf["VisionAssistant"]["source_language"]))
        except: self.sourceLang.SetSelection(0)
        
        self.targetLang = sHelper.addLabeledControl("Target:", wx.Choice, choices=TARGET_NAMES)
        try: self.targetLang.SetSelection(TARGET_NAMES.index(config.conf["VisionAssistant"]["target_language"]))
        except: self.targetLang.SetSelection(0)
        
        self.aiResponseLang = sHelper.addLabeledControl("AI Response:", wx.Choice, choices=TARGET_NAMES)
        try: self.aiResponseLang.SetSelection(TARGET_NAMES.index(config.conf["VisionAssistant"]["ai_response_language"]))
        except: self.aiResponseLang.SetSelection(0)

        self.smartSwap = sHelper.addItem(wx.CheckBox(self, label="Smart Swap"))
        self.smartSwap.Value = config.conf["VisionAssistant"]["smart_swap"]

        sHelper.addItem(wx.StaticText(self, label="--- CAPTCHA Mode ---"))
        self.captchaMode = wx.RadioBox(self, label="Capture Method:", choices=["Navigator Object", "Full Screen"], style=wx.RA_SPECIFY_COLS)
        self.captchaMode.SetSelection(0 if config.conf["VisionAssistant"]["captcha_mode"] == 'navigator' else 1)
        sHelper.addItem(self.captchaMode)

        sHelper.addItem(wx.StaticText(self, label="--- Custom Prompts (Name:Content) ---"))
        self.customPrompts = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
        self.customPrompts.Value = config.conf["VisionAssistant"]["custom_prompts"]
        sHelper.addItem(self.customPrompts)

    def onSave(self):
        config.conf["VisionAssistant"]["api_key"] = self.apiKey.Value.strip()
        config.conf["VisionAssistant"]["model_name"] = MODELS[self.model.GetSelection()]
        config.conf["VisionAssistant"]["proxy_url"] = self.proxyUrl.Value.strip()
        config.conf["VisionAssistant"]["source_language"] = SOURCE_NAMES[self.sourceLang.GetSelection()]
        config.conf["VisionAssistant"]["target_language"] = TARGET_NAMES[self.targetLang.GetSelection()]
        config.conf["VisionAssistant"]["ai_response_language"] = TARGET_NAMES[self.aiResponseLang.GetSelection()]
        config.conf["VisionAssistant"]["smart_swap"] = self.smartSwap.Value
        config.conf["VisionAssistant"]["captcha_mode"] = 'navigator' if self.captchaMode.GetSelection() == 0 else 'fullscreen'
        config.conf["VisionAssistant"]["custom_prompts"] = self.customPrompts.Value.strip()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    last_translation = "" 
    is_recording = False
    temp_audio_file = os.path.join(tempfile.gettempdir(), "vision_dictate.wav")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        config.conf.spec["VisionAssistant"] = confspec
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsPanel)

    def terminate(self):
        try: gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SettingsPanel)
        except: pass

    def _call_gemini(self, prompt, attachments=[], json_mode=False):
        api_key = config.conf["VisionAssistant"]["api_key"].strip()
        proxy_url = config.conf["VisionAssistant"]["proxy_url"].strip()
        model = config.conf["VisionAssistant"]["model_name"]
        
        base_url = proxy_url.rstrip('/') if proxy_url else "https://generativelanguage.googleapis.com"
        url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        
        parts = [{"text": prompt}]
        for att in attachments:
            parts.append({"inline_data": {"mime_type": att['mime_type'], "data": att['data']}})
            
        data = {"contents": [{"parts": parts}]}
        if json_mode: data["generationConfig"] = {"response_mime_type": "application/json"}

        try:
            req = request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    res = json.loads(response.read().decode('utf-8'))
                    text = res['candidates'][0]['content']['parts'][0]['text'].strip()
                    return text if json_mode else clean_markdown(text)
        except Exception as e:
            log.error(f"Gemini Error: {e}")
            return None

    # --- Feature 1: Dictation ---
    def script_smartDictation(self, gesture):
        if not self.is_recording:
            self.is_recording = True
            play_sound(800, 100)
            winmm.mciSendStringW('open new type waveaudio alias myaudio', None, 0, 0)
            winmm.mciSendStringW('record myaudio', None, 0, 0)
            ui.message("Listening...")
        else:
            self.is_recording = False
            play_sound(500, 100)
            winmm.mciSendStringW(f'save myaudio "{self.temp_audio_file}"', None, 0, 0)
            winmm.mciSendStringW('close myaudio', None, 0, 0)
            ui.message("Typing...")
            threading.Thread(target=self._thread_dictation).start()

    def _thread_dictation(self):
        try:
            if not os.path.exists(self.temp_audio_file): return
            with open(self.temp_audio_file, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            p = "Transcribe speech. Use native script. No Fingilish. Fix stutters."
            res = self._call_gemini(p, attachments=[{'mime_type': 'audio/wav', 'data': audio_data}])
            
            if res: wx.CallAfter(self._paste_text, res)
            else: wx.CallAfter(ui.message, "No speech.")
            try: os.remove(self.temp_audio_file)
            except: pass
        except: wx.CallAfter(ui.message, "Error.")

    def _paste_text(self, text):
        api.copyToClip(text)
        preview = text[:100]
        ui.message(f"Typed: {preview}")
        wx.CallLater(800, send_ctrl_v)

    # --- Feature 2: Translator ---
    def script_translateSmart(self, gesture):
        text = self._get_text_smart()
        if not text:
            ui.message("No text.")
            return
        ui.message("Translating...") 
        threading.Thread(target=self._thread_translate, args=(text,)).start()

    def _thread_translate(self, text):
        s = config.conf["VisionAssistant"]["source_language"]
        t = config.conf["VisionAssistant"]["target_language"]
        swap = config.conf["VisionAssistant"]["smart_swap"]
        fallback = "English" if s == "Auto-detect" else s
        p = PROMPT_TRANSLATE.format(target_lang=t, swap_target=fallback, smart_swap=str(swap))
        res = self._call_gemini(f"{p}\nInput: {text}")
        if res:
            self.last_translation = res
            wx.CallAfter(self._announce_translation, res)
        else: wx.CallAfter(ui.message, "Failed.")

    def _announce_translation(self, text):
        api.copyToClip(text)
        ui.message(f"Translated: {text}")

    def _get_text_smart(self):
        try:
            info = api.getFocusObject().makeTextInfo(textInfos.POSITION_SELECTION)
            if info.text and not info.text.isspace(): return info.text
        except: pass
        try:
            obj = api.getNavigatorObject()
            content = [obj.name, obj.value, obj.description]
            if hasattr(obj, 'makeTextInfo'):
                try: content.append(obj.makeTextInfo(textInfos.POSITION_ALL).text)
                except: pass
            return " ".join(list(dict.fromkeys([c for c in content if c and not c.isspace()])))
        except: return None

    # --- Feature 3: Refiner & Custom Prompts ---
    def script_refineText(self, gesture):
        text = self._get_text_smart()
        if not text: text = "" 
        wx.CallAfter(self._open_refine_dialog, text)

    def _open_refine_dialog(self, text):
        choices = ["Summarize", "Fix Grammar", "Fix Grammar & Translate", "Explain"]
        custom_raw = config.conf["VisionAssistant"]["custom_prompts"]
        custom_dict = {}
        if custom_raw:
            for line in custom_raw.split('|'):
                if ':' in line:
                    parts = line.split(':', 1)
                    name = parts[0].strip()
                    content = parts[1].strip()
                    if name and content:
                        choices.append(f"Custom: {name}")
                        custom_dict[f"Custom: {name}"] = content
        
        dlg = wx.SingleChoiceDialog(gui.mainFrame, "Choose action:", "Refine", choices)
        if dlg.ShowModal() == wx.ID_OK:
            sel_str = dlg.GetStringSelection()
            custom_content = ""
            
            if sel_str in custom_dict:
                custom_content = custom_dict[sel_str]
            else:
                if sel_str == "Summarize": custom_content = "[summarize]"
                elif sel_str == "Fix Grammar": custom_content = "[fix_grammar]"
                elif sel_str == "Fix Grammar & Translate": custom_content = "[fix_translate]"
                elif sel_str == "Explain": custom_content = "[explain]"

            file_path = None
            needs_file = False
            wc = "Files|*.*"
            
            if "[file_ocr]" in custom_content:
                needs_file = True
                wc = "Images/PDF/TIFF|*.png;*.jpg;*.webp;*.pdf;*.tif;*.tiff"
            elif "[file_read]" in custom_content:
                needs_file = True
                wc = "Documents|*.txt;*.py;*.md;*.html;*.pdf;*.tif;*.tiff"
            elif "[file_audio]" in custom_content:
                needs_file = True
                wc = "Audio|*.mp3;*.wav;*.ogg"
            
            if needs_file:
                title = "Select File for Command"
                if "[file_ocr]" in custom_content: title = "Select Image/PDF/TIFF for OCR"
                fd = wx.FileDialog(gui.mainFrame, title, wildcard=wc, style=wx.FD_OPEN)
                if fd.ShowModal() == wx.ID_OK: file_path = fd.GetPath()
                fd.Destroy()
                if not file_path: return 

            ui.message("Processing...")
            threading.Thread(target=self._thread_refine, args=(text, custom_content, file_path)).start()
        dlg.Destroy()

    def _thread_refine(self, text, custom_content, file_path=None):
        target_lang = config.conf["VisionAssistant"]["target_language"]
        resp_lang = config.conf["VisionAssistant"]["ai_response_language"]
        
        prompt_text = custom_content
        attachments = []
        
        prompt_text = prompt_text.replace("[summarize]", f"Summarize this in {resp_lang}.")
        prompt_text = prompt_text.replace("[fix_grammar]", "Fix grammar.")
        prompt_text = prompt_text.replace("[fix_translate]", f"Fix grammar and translate to {target_lang}.")
        prompt_text = prompt_text.replace("[explain]", f"Explain in {resp_lang}.")
        
        if "[selection]" in prompt_text: prompt_text = prompt_text.replace("[selection]", text)
        if "[clipboard]" in prompt_text: prompt_text = prompt_text.replace("[clipboard]", api.getClipData())
        
        if "[screen_obj]" in prompt_text:
            d, w, h = self._capture_navigator()
            if d: attachments.append({'mime_type': 'image/png', 'data': d})
            prompt_text = prompt_text.replace("[screen_obj]", "")
            
        if "[screen_full]" in prompt_text:
            d, w, h = self._capture_fullscreen()
            if d: attachments.append({'mime_type': 'image/png', 'data': d})
            prompt_text = prompt_text.replace("[screen_full]", "")
            
        if file_path:
            try:
                if os.path.getsize(file_path) < 15*1024*1024:
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    if "[file_ocr]" in prompt_text:
                        if ext in ['.tif', '.tiff']:
                            pages = process_tiff_pages(file_path)
                            for p_data in pages:
                                attachments.append({'mime_type': 'image/jpeg', 'data': p_data})
                        elif ext == ".pdf":
                            with open(file_path, "rb") as f: raw = f.read()
                            attachments.append({'mime_type': 'application/pdf', 'data': base64.b64encode(raw).decode('utf-8')})
                        else:
                            with open(file_path, "rb") as f: raw = f.read()
                            attachments.append({'mime_type': 'image/png', 'data': base64.b64encode(raw).decode('utf-8')})
                        
                        prompt_text = prompt_text.replace("[file_ocr]", "")
                        if not prompt_text.strip(): prompt_text = "Extract all text from this file."
                    
                    elif "[file_audio]" in prompt_text:
                        mt = "audio/mpeg" if ext == ".mp3" else "audio/wav"
                        with open(file_path, "rb") as f: raw = f.read()
                        attachments.append({'mime_type': mt, 'data': base64.b64encode(raw).decode('utf-8')})
                        prompt_text = prompt_text.replace("[file_audio]", "")
                        if not prompt_text.strip(): prompt_text = f"Transcribe this audio in {resp_lang}."

                    elif "[file_read]" in prompt_text:
                        if ext == ".pdf":
                            with open(file_path, "rb") as f: raw = f.read()
                            attachments.append({'mime_type': 'application/pdf', 'data': base64.b64encode(raw).decode('utf-8')})
                            prompt_text = prompt_text.replace("[file_read]", "")
                            if not prompt_text.strip(): prompt_text = f"Analyze this document in {resp_lang}."
                        elif ext in ['.tif', '.tiff']:
                            pages = process_tiff_pages(file_path)
                            for p_data in pages:
                                attachments.append({'mime_type': 'image/jpeg', 'data': p_data})
                            prompt_text = prompt_text.replace("[file_read]", "")
                            if not prompt_text.strip(): prompt_text = f"Analyze this document in {resp_lang}."
                        else:
                            with open(file_path, "rb") as f: raw = f.read()
                            try:
                                txt = raw.decode('utf-8')
                                prompt_text = prompt_text.replace("[file_read]", f"\nFile:\n{txt}\n")
                            except: pass
            except: pass
            
        res = self._call_gemini(prompt_text, attachments=attachments)
        if res: wx.CallAfter(lambda: (api.copyToClip(res), ui.message(res)))

    # --- Feature 4: Doc QA ---
    def script_analyzeDocument(self, gesture):
        wx.CallAfter(self._open_doc_dialog)
    def _open_doc_dialog(self):
        dlg = wx.FileDialog(gui.mainFrame, "Select Document to Analyze", wildcard="Doc|*.pdf;*.tif;*.tiff;*.txt;*.py;*.md", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            threading.Thread(target=self._process_doc_file, args=(path,)).start()
        dlg.Destroy()
    def _process_doc_file(self, path):
        try:
            wx.CallAfter(ui.message, "Loading...")
            if os.path.getsize(path) > 15 * 1024 * 1024: return
            ext = os.path.splitext(path)[1].lower()
            att = []
            init_msg = "Ask about document."
            doc_text = None
            
            if ext in ['.tif', '.tiff']:
                no_log = wx.LogNull()
                pages = process_tiff_pages(path)
                for p_data in pages:
                    att.append({'mime_type': 'image/jpeg', 'data': p_data})
                init_msg = f"TIFF loaded ({len(pages)} pages)."
            elif ext == '.pdf':
                with open(path, "rb") as f: raw = f.read()
                att.append({'mime_type': 'application/pdf', 'data': base64.b64encode(raw).decode('utf-8')})
                init_msg = "PDF loaded."
            else:
                with open(path, "rb") as f: raw = f.read()
                try: doc_text = raw.decode('utf-8')
                except: doc_text = "Binary"
            
            wx.CallAfter(self._open_doc_chat_dialog, init_msg, att, doc_text)
        except: wx.CallAfter(ui.message, "Error.")
        
    def _open_doc_chat_dialog(self, init_msg, initial_attachments, doc_text):
        def doc_callback(ctx_atts, q, dum1, dum2):
            lang = config.conf["VisionAssistant"]["ai_response_language"]
            atts = ctx_atts if ctx_atts else []
            p = f"User Question: {q}\nRespond in {lang}."
            if doc_text: p = f"Document:\n{doc_text}\n\n{p}"
            # Force processing for attachments even if prompt is short
            if atts and len(q) < 5: p += " Describe/Analyze this file."
            return self._call_gemini(p, attachments=atts), None
            
        dlg = VisionQADialog(gui.mainFrame, "Doc QA", init_msg, initial_attachments, doc_callback)
        dlg.Show()

    # --- Feature 5: Vision ---
    def script_ocrFullScreen(self, gesture):
        self._start_vision(True)
    def script_describeObject(self, gesture):
        self._start_vision(False)
    def _start_vision(self, full):
        if full: d, w, h = self._capture_fullscreen()
        else: d, w, h = self._capture_navigator()
        if d:
            ui.message("Scanning...")
            threading.Thread(target=self._thread_vision, args=(d, w, h)).start()
        else: ui.message("Capture failed.")
    def _thread_vision(self, img, w, h):
        lang = config.conf["VisionAssistant"]["ai_response_language"]
        p = f"Describe concisely in {lang}."
        att = [{'mime_type': 'image/png', 'data': img}]
        desc = self._call_gemini(p, attachments=att)
        wx.CallAfter(self._open_vision_dialog, desc, att, (w, h))
        
    def _open_vision_dialog(self, text, atts, size):
        def cb(atts, q, is_loc, sz):
            if is_loc and sz:
                p = PROMPT_UI_LOCATOR.format(width=sz[0], height=sz[1], query=q)
                res = self._call_gemini(p, attachments=atts, json_mode=True)
                try:
                    d = json.loads(res)
                    if d.get("found"): return f"Found at {d['x']},{d['y']}.", (d['x'], d['y'])
                    return "Not found.", None
                except: return "Error.", None
            else:
                lang = config.conf["VisionAssistant"]["ai_response_language"]
                p = f"Context: {text}. Q: {q}. Respond in {lang}."
                return self._call_gemini(p, attachments=atts), None
        dlg = VisionQADialog(gui.mainFrame, "Vision", text, atts, cb, size)
        dlg.Show()

    # --- Feature 6: Audio ---
    def script_transcribeAudio(self, gesture):
        wx.CallAfter(self._open_audio)
    def _open_audio(self):
        dlg = wx.FileDialog(gui.mainFrame, "Select Audio File to Transcribe", wildcard="Audio|*.mp3;*.wav;*.ogg", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            threading.Thread(target=self._thread_audio, args=(dlg.GetPath(),)).start()
        dlg.Destroy()
    def _thread_audio(self, path):
        try:
            wx.CallAfter(ui.message, "Uploading...")
            if os.path.getsize(path)>15*1024*1024: return
            with open(path,"rb") as f: d = base64.b64encode(f.read()).decode('utf-8')
            wx.CallAfter(ui.message, "Analyzing...")
            lang = config.conf["VisionAssistant"]["ai_response_language"]
            p = f"Transcribe in {lang}."
            mt = "audio/mpeg" if path.endswith(".mp3") else "audio/wav"
            res = self._call_gemini(p, attachments=[{'mime_type': mt, 'data': d}])
            wx.CallAfter(lambda: ResultDialog(gui.mainFrame, "Transcript", res).ShowModal())
        except: wx.CallAfter(ui.message, "Error.")

    # --- Feature 7: Captcha ---
    def script_solveCaptcha(self, gesture):
        mode = config.conf["VisionAssistant"]["captcha_mode"]
        if mode == 'fullscreen': d, w, h = self._capture_fullscreen()
        else: d, w, h = self._capture_navigator()
        
        is_gov = False
        try:
            if "پنجره ملی خدمات دولت هوشمند" in api.getForegroundObject().name: is_gov = True
        except: pass

        if d:
            ui.message("Solving...")
            threading.Thread(target=self._thread_cap, args=(d, is_gov)).start()
        else: ui.message("Capture failed.")
        
    def _thread_cap(self, d, is_gov):
        p = "Blind user. Return CAPTCHA code only."
        if is_gov: p += " Read 5 Persian digits, convert to English."
        else: p += " Convert to English digits."
        
        r = self._call_gemini(p, attachments=[{'mime_type': 'image/png', 'data': d}])
        if r: wx.CallAfter(self._finish_captcha, r)
        else: wx.CallAfter(ui.message, "Failed.")

    def _finish_captcha(self, text):
        api.copyToClip(text)
        ui.message(f"Captcha: {text}")
        wx.CallLater(800, send_ctrl_v)

    # --- Utils ---
    def _capture_navigator(self):
        try:
            obj = api.getNavigatorObject()
            if not obj.location: return None,0,0
            x,y,w,h = obj.location
            if w<1 or h<1: return None,0,0
            bmp = wx.Bitmap(w,h)
            wx.MemoryDC(bmp).Blit(0,0,w,h,wx.ScreenDC(),x,y)
            s = io.BytesIO()
            bmp.ConvertToImage().SaveFile(s, wx.BITMAP_TYPE_PNG)
            return base64.b64encode(s.getvalue()).decode('utf-8'),w,h
        except: return None,0,0
    def _capture_fullscreen(self):
        try:
            w,h = wx.GetDisplaySize()
            bmp = wx.Bitmap(w,h)
            wx.MemoryDC(bmp).Blit(0,0,w,h,wx.ScreenDC(),0,0)
            s = io.BytesIO()
            bmp.ConvertToImage().SaveFile(s, wx.BITMAP_TYPE_PNG)
            return base64.b64encode(s.getvalue()).decode('utf-8'),w,h
        except: return None,0,0

    def script_readLastTranslation(self, gesture):
        if self.last_translation: ui.message(f"Last: {self.last_translation}")
        else: ui.message("No history.")
    def script_translateClipboard(self, gesture):
        t = api.getClipData()
        if t: self.script_translateSmart(gesture)

    __gestures = {
        "kb:NVDA+shift+t": "translateSmart",
        "kb:NVDA+shift+r": "refineText",
        "kb:NVDA+shift+o": "ocrFullScreen",
        "kb:NVDA+shift+v": "describeObject",
        "kb:NVDA+shift+d": "analyzeDocument",
        "kb:NVDA+shift+a": "transcribeAudio",
        "kb:NVDA+shift+6": "solveCaptcha",
        "kb:NVDA+shift+l": "readLastTranslation",
        "kb:NVDA+shift+y": "translateClipboard",
        "kb:NVDA+shift+s": "smartDictation",
    }