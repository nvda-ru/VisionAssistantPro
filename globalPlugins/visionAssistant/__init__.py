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
import hashlib
import gc
from urllib import request, error

log = logging.getLogger(__name__)
addonHandler.initTranslation()

MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

BASE_LANGUAGES = [
    ("Arabic", "ar"), ("Chinese", "zh"), ("Czech", "cs"), ("Danish", "da"),
    ("Dutch", "nl"), ("English", "en"), ("Finnish", "fi"), ("French", "fr"),
    ("German", "de"), ("Greek", "el"), ("Hebrew", "he"), ("Hindi", "hi"),
    ("Hungarian", "hu"), ("Indonesian", "id"), ("Italian", "it"), ("Japanese", "ja"),
    ("Korean", "ko"), ("Norwegian", "no"), ("Persian", "fa"), ("Polish", "pl"),
    ("Portuguese", "pt"), ("Romanian", "ro"), ("Russian", "ru"), ("Spanish", "es"),
    ("Swedish", "sv"), ("Thai", "th"), ("Turkish", "tr"), ("Ukrainian", "uk"),
    ("Vietnamese", "vi")
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

GITHUB_REPO = "mahmoodhozhabri/VisionAssistantPro"

def clean_markdown(text):
    if not text: return ""
    text = re.sub(r'\*\*|__|[*_]', '', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*-\s+', '', text, flags=re.MULTILINE)
    return text.strip()

def play_sound(freq, dur):
    try:
        import winsound
        winsound.Beep(freq, dur)
    except: pass

def send_ctrl_v():
    try:
        user32 = ctypes.windll.user32
        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    except: pass

def process_tiff_pages(path):
    pages_data = []
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

PROMPT_TRANSLATE = """
Role: Translator.
Directives:
1. Translate text inside "===" to {target_lang}.
2. IF SmartSwap={smart_swap} AND input is {target_lang} THEN translate to {swap_target}.
3. Output ONLY the translation.

Text:
===
{text_content}
===
"""

PROMPT_UI_LOCATOR = "Analyze UI (Size: {width}x{height}). Request: '{query}'. Output JSON: {{\"x\": int, \"y\": int, \"found\": bool}}."

class UpdateManager:
    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.current_version = addonHandler.getCodeAddon().manifest['version']

    def check_for_updates(self, silent=True):
        threading.Thread(target=self._check_thread, args=(silent,), daemon=True).start()

    def _check_thread(self, silent):
        try:
            url = f"https://api.github.com/repos/{self.repo_name}/releases/latest"
            req = request.Request(url, headers={"User-Agent": "NVDA-Addon"})
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    latest_tag = data.get("tag_name", "").lstrip("v")
                    
                    if self._compare_versions(latest_tag, self.current_version) > 0:
                        download_url = None
                        for asset in data.get("assets", []):
                            if asset["name"].endswith(".nvda-addon"):
                                download_url = asset["browser_download_url"]
                                break
                        
                        if download_url:
                            wx.CallAfter(self._prompt_update, latest_tag, download_url, data.get("body", ""))
                        elif not silent:
                            wx.CallAfter(ui.message, "Update found but no .nvda-addon file in release.")
                    elif not silent:
                        wx.CallAfter(ui.message, "You have the latest version.")
        except Exception as e:
            if not silent:
                wx.CallAfter(ui.message, f"Update check failed: {e}")

    def _compare_versions(self, v1, v2):
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            return (parts1 > parts2) - (parts1 < parts2)
        except:
            return 0 if v1 == v2 else 1

    def _prompt_update(self, version, url, changes):
        msg = f"A new version ({version}) of Vision Assistant is available.\n\nChanges:\n{changes}\n\nDownload and Install?"
        dlg = wx.MessageDialog(gui.mainFrame, msg, "Update Available", wx.YES_NO | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES:
            threading.Thread(target=self._download_install_worker, args=(url,), daemon=True).start()
        dlg.Destroy()

    def _download_install_worker(self, url):
        try:
            wx.CallAfter(ui.message, "Downloading update...")
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, "VisionAssistant_Update.nvda-addon")
            
            with request.urlopen(url) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
            
            wx.CallAfter(os.startfile, file_path)
        except Exception as e:
            wx.CallAfter(ui.message, f"Download failed: {e}")

class VisionQADialog(wx.Dialog):
    def __init__(self, parent, title, initial_text, context_data, callback_fn, extra_info=None):
        super(VisionQADialog, self).__init__(parent, title=title, size=(550, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.context_data = context_data 
        self.callback_fn = callback_fn
        self.extra_info = extra_info
        self.chat_history = [] 
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, label="AI Response:")
        mainSizer.Add(lbl, 0, wx.ALL, 5)
        self.outputArea = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(self.outputArea, 1, wx.EXPAND | wx.ALL, 5)
        
        clean_init = clean_markdown(initial_text)
        self.outputArea.AppendText(f"AI: {clean_init}\n")
        
        self.chat_history.append({"role": "model", "parts": [{"text": initial_text}]})

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
        threading.Thread(target=self.process_question, args=(question,), daemon=True).start()

    def process_question(self, question):
        response_text, _ = self.callback_fn(self.context_data, question, self.chat_history, self.extra_info)
        clean_resp = clean_markdown(response_text)
        
        if response_text:
            self.chat_history.append({"role": "user", "parts": [{"text": question}]})
            self.chat_history.append({"role": "model", "parts": [{"text": response_text}]})
            
        wx.CallAfter(self.update_response, clean_resp)

    def update_response(self, text):
        self.outputArea.AppendText(f"AI: {text}\n")
        self.outputArea.ShowPosition(self.outputArea.GetLastPosition())
        ui.message(text)

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
    scriptCategory = "Vision Assistant"
    
    last_translation = "" 
    is_recording = False
    temp_audio_file = os.path.join(tempfile.gettempdir(), "vision_dictate.wav")
    
    translation_cache = {}
    _last_source_text = None
    _last_params = None
    update_timer = None

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        config.conf.spec["VisionAssistant"] = confspec
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsPanel)
        
        self.updater = UpdateManager(GITHUB_REPO)
        # Check for updates 5 seconds after startup
        self.update_timer = wx.CallLater(5000, self.updater.check_for_updates, True)

    def terminate(self):
        try: gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SettingsPanel)
        except: pass
        
        if self.update_timer and self.update_timer.IsRunning():
            self.update_timer.Stop()
        
        if self.is_recording:
            try:
                ctypes.windll.winmm.mciSendStringW('close myaudio', None, 0, 0)
            except: pass
        
        self.translation_cache = {}
        self._last_source_text = None
        gc.collect()

    def _call_gemini(self, prompt_or_contents, attachments=[], json_mode=False):
        api_key = config.conf["VisionAssistant"]["api_key"].strip()
        proxy_url = config.conf["VisionAssistant"]["proxy_url"].strip()
        model = config.conf["VisionAssistant"]["model_name"]
        
        if not api_key:
            wx.CallAfter(ui.message, "API Key missing.")
            return None

        base_url = proxy_url.rstrip('/') if proxy_url else "https://generativelanguage.googleapis.com"
        url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        
        contents = []
        if isinstance(prompt_or_contents, list):
            contents = prompt_or_contents
        else:
            parts = [{"text": prompt_or_contents}]
            for att in attachments:
                parts.append({"inline_data": {"mime_type": att['mime_type'], "data": att['data']}})
            contents = [{"parts": parts}]
            
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.0, 
                "topK": 40
            }
        }
        if json_mode: data["generationConfig"]["response_mime_type"] = "application/json"

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                req = request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
                with request.urlopen(req, timeout=60) as response:
                    if response.status == 200:
                        res = json.loads(response.read().decode('utf-8'))
                        text = res['candidates'][0]['content']['parts'][0]['text'].strip()
                        return text if json_mode else clean_markdown(text)
            except error.HTTPError as e:
                if e.code == 503 and attempt < max_retries:
                    time.sleep(1)
                    continue
                log.error(f"Gemini HTTP Error: {e.code} - {e.reason}")
                return None
            except Exception as e:
                log.error(f"Gemini General Error: {e}")
                return None
        return None

    def script_smartDictation(self, gesture):
        """Toggles voice dictation."""
        if not self.is_recording:
            self.is_recording = True
            play_sound(800, 100)
            try:
                ctypes.windll.winmm.mciSendStringW('open new type waveaudio alias myaudio', None, 0, 0)
                ctypes.windll.winmm.mciSendStringW('record myaudio', None, 0, 0)
                ui.message("Listening...")
            except Exception as e:
                ui.message("Audio error")
                self.is_recording = False
        else:
            self.is_recording = False
            play_sound(500, 100)
            try:
                ctypes.windll.winmm.mciSendStringW(f'save myaudio "{self.temp_audio_file}"', None, 0, 0)
                ctypes.windll.winmm.mciSendStringW('close myaudio', None, 0, 0)
                ui.message("Typing...")
                threading.Thread(target=self._thread_dictation, daemon=True).start()
            except Exception as e:
                ui.message("Save error")

    def _thread_dictation(self):
        try:
            if not os.path.exists(self.temp_audio_file): return
            with open(self.temp_audio_file, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            p = "Transcribe speech. Use native script. No Fingilish. Fix stutters."
            res = self._call_gemini(p, attachments=[{'mime_type': 'audio/wav', 'data': audio_data}])
            
            if res: wx.CallAfter(self._paste_text, res)
            else: wx.CallAfter(ui.message, "No speech recognized.")
            try: os.remove(self.temp_audio_file)
            except: pass
        except: wx.CallAfter(ui.message, "Dictation Error.")

    def _paste_text(self, text):
        api.copyToClip(text)
        preview = text[:100]
        ui.message(f"Typed: {preview}")
        wx.CallLater(800, send_ctrl_v)

    def script_translateSmart(self, gesture):
        """Translates the selected text or navigator object."""
        text = self._get_text_smart()
        
        if not text:
            ui.message("No text found.")
            return
            
        ui.message("Translating...") 
        threading.Thread(target=self._thread_translate, args=(text,), daemon=True).start()

    def _thread_translate(self, text):
        s = config.conf["VisionAssistant"]["source_language"]
        t = config.conf["VisionAssistant"]["target_language"]
        swap = config.conf["VisionAssistant"]["smart_swap"]
        fallback = "English" if s == "Auto-detect" else s
        
        current_params = f"{t}|{swap}"
        if text == self._last_source_text and current_params == self._last_params and self.last_translation:
            wx.CallAfter(self._announce_translation, self.last_translation)
            return

        safe_text = text.replace('{', '{{').replace('}', '}}')
        p = PROMPT_TRANSLATE.format(
            target_lang=t, 
            swap_target=fallback, 
            smart_swap=str(swap),
            text_content=safe_text
        )
        res = self._call_gemini(p)
        if res:
            self._last_source_text = text
            self._last_params = current_params
            self.last_translation = res
            wx.CallAfter(self._announce_translation, res)
        else: wx.CallAfter(ui.message, "Translation failed.")

    def _announce_translation(self, text):
        api.copyToClip(text)
        ui.message(f"Translated: {text}")

    def _get_text_smart(self):
        try:
            focus_obj = api.getFocusObject()
            if focus_obj:
                info = focus_obj.makeTextInfo(textInfos.POSITION_SELECTION)
                if info and info.text and not info.text.isspace():
                    return info.text
        except: pass

        try:
            obj = api.getNavigatorObject()
            if not obj: return None
            
            content = []
            if obj.name: content.append(obj.name)
            if obj.value: content.append(obj.value)
            if obj.description: content.append(obj.description)
            
            if hasattr(obj, 'makeTextInfo'):
                try: 
                    content.append(obj.makeTextInfo(textInfos.POSITION_ALL).text)
                except: pass
                
            final_text = " ".join(list(dict.fromkeys([c for c in content if c and not c.isspace()])))
            return final_text if final_text else None
        except Exception: 
            return None

    def script_refineText(self, gesture):
        """Opens a menu to Explain, Summarize, or Fix the selected text."""
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
            threading.Thread(target=self._thread_refine, args=(text, custom_content, file_path), daemon=True).start()
        dlg.Destroy()

    def _thread_refine(self, text, custom_content, file_path=None):
        target_lang = config.conf["VisionAssistant"]["target_language"]
        source_lang = config.conf["VisionAssistant"]["source_language"]
        smart_swap = config.conf["VisionAssistant"]["smart_swap"]
        resp_lang = config.conf["VisionAssistant"]["ai_response_language"]
        
        prompt_text = custom_content
        attachments = []
        
        if "[fix_translate]" in prompt_text:
            fallback = "English" if source_lang == "Auto-detect" else source_lang
            swap_instr = f"If text is in {target_lang}, translate to {fallback}." if smart_swap else ""
            prompt_text = prompt_text.replace("[fix_translate]", 
                f"Fix grammar and translate to {target_lang}. {swap_instr} Output ONLY the result.")
        
        prompt_text = prompt_text.replace("[summarize]", f"Summarize the text below in {resp_lang}.")
        prompt_text = prompt_text.replace("[fix_grammar]", "Fix grammar in the text below. Output ONLY the fixed text.")
        prompt_text = prompt_text.replace("[explain]", f"Explain the text below in {resp_lang}.")
        
        used_selection = False
        if "[selection]" in prompt_text: 
            prompt_text = prompt_text.replace("[selection]", text)
            used_selection = True
            
        if "[clipboard]" in prompt_text: 
            prompt_text = prompt_text.replace("[clipboard]", api.getClipData())
        
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
                    if "[file_ocr]" in prompt_text:
                         with open(file_path, "rb") as f: raw = f.read()
                         attachments.append({'mime_type': 'image/png', 'data': base64.b64encode(raw).decode('utf-8')})
                         prompt_text = prompt_text.replace("[file_ocr]", "")
                         if not prompt_text.strip(): prompt_text = "Extract text."
                    elif "[file_read]" in prompt_text:
                        with open(file_path, "rb") as f: raw = f.read()
                        try:
                            txt = raw.decode('utf-8')
                            prompt_text = prompt_text.replace("[file_read]", f"\nFile Content:\n{txt}\n")
                        except: pass
            except: pass
            
        if text and not used_selection and not file_path:
            prompt_text += f"\n\n---\nInput Text:\n{text}\n---\n"
            
        res = self._call_gemini(prompt_text, attachments=attachments)
        
        if res:
             wx.CallAfter(self._open_refine_result_dialog, res, attachments, text)

    def _open_refine_result_dialog(self, result_text, attachments, original_text):
        def refine_callback(ctx, q, history, dum2):
            atts, orig = ctx
            current_user_msg = {"role": "user", "parts": [{"text": q}]}
            
            messages = []
            if not history:
                context_msg = f"Context Text: {orig}\n\nTask: Answer questions."
                parts = [{"text": context_msg}]
                for att in atts:
                    parts.append({"inline_data": {"mime_type": att['mime_type'], "data": att['data']}})
                
                messages.append({"role": "user", "parts": parts})
                messages.append({"role": "model", "parts": [{"text": result_text}]})
            else:
                messages.extend(history)
            
            messages.append(current_user_msg)
            return self._call_gemini(messages), None

        context = (attachments, original_text)
        dlg = VisionQADialog(gui.mainFrame, "Vision Assistant - Refine Result", result_text, context, refine_callback)
        dlg.Show()

    def script_analyzeDocument(self, gesture):
        """Allows asking questions about a selected document (PDF/Text/Image)."""
        wx.CallAfter(self._open_doc_dialog)
    def _open_doc_dialog(self):
        dlg = wx.FileDialog(gui.mainFrame, "Select Document to Analyze", wildcard="Doc|*.pdf;*.tif;*.tiff;*.txt;*.py;*.md", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            threading.Thread(target=self._process_doc_file, args=(path,), daemon=True).start()
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
        except: wx.CallAfter(ui.message, "Error loading doc.")
        
    def _open_doc_chat_dialog(self, init_msg, initial_attachments, doc_text):
        def doc_callback(ctx_atts, q, history, dum2):
            lang = config.conf["VisionAssistant"]["ai_response_language"]
            atts = ctx_atts if ctx_atts else []
            
            current_user_msg = {"role": "user", "parts": [{"text": f"{q} (STRICTLY Respond in {lang})"}]}
            
            messages = []
            if not history:
                parts = []
                if doc_text: parts.append({"text": f"Document Content:\n{doc_text}\n\nTask: Analyze. Language: {lang}."})
                else: parts.append({"text": f"Analyze this file. Respond in {lang}."})
                
                for att in atts:
                    parts.append({"inline_data": {"mime_type": att['mime_type'], "data": att['data']}})
                
                messages.append({"role": "user", "parts": parts})
                messages.append({"role": "model", "parts": [{"text": init_msg}]})
            else:
                messages.extend(history)
                
            messages.append(current_user_msg)
            return self._call_gemini(messages), None
            
        dlg = VisionQADialog(gui.mainFrame, "Vision Assistant - Document Chat", init_msg, initial_attachments, doc_callback)
        dlg.Show()

    def script_ocrFullScreen(self, gesture):
        self._start_vision(True)
    def script_describeObject(self, gesture):
        self._start_vision(False)
    def _start_vision(self, full):
        if full: d, w, h = self._capture_fullscreen()
        else: d, w, h = self._capture_navigator()
        if d:
            ui.message("Scanning...")
            threading.Thread(target=self._thread_vision, args=(d, w, h), daemon=True).start()
        else: ui.message("Capture failed.")
    def _thread_vision(self, img, w, h):
        lang = config.conf["VisionAssistant"]["ai_response_language"]
        p = f"Analyze this image and describe it. Language: {lang}. Ensure the response is strictly in {lang}."
        att = [{'mime_type': 'image/png', 'data': img}]
        desc = self._call_gemini(p, attachments=att)
        wx.CallAfter(self._open_vision_dialog, desc, att, None)
        
    def _open_vision_dialog(self, text, atts, size):
        def cb(atts, q, history, sz):
            lang = config.conf["VisionAssistant"]["ai_response_language"]
            current_user_msg = {"role": "user", "parts": [{"text": f"{q} (Answer strictly in {lang})"}]}
            
            messages = []
            if not history:
                parts = [{"text": f"Image Context. Target Language: {lang}"}]
                for att in atts:
                    parts.append({"inline_data": {"mime_type": att['mime_type'], "data": att['data']}})
                messages.append({"role": "user", "parts": parts})
                messages.append({"role": "model", "parts": [{"text": text}]})
            else:
                messages.extend(history)
                
            messages.append(current_user_msg)
            return self._call_gemini(messages), None
            
        dlg = VisionQADialog(gui.mainFrame, "Vision Assistant - Image Analysis", text, atts, cb, None)
        dlg.Show()

    def script_transcribeAudio(self, gesture):
        wx.CallAfter(self._open_audio)
    def _open_audio(self):
        dlg = wx.FileDialog(gui.mainFrame, "Select Audio File to Transcribe", wildcard="Audio|*.mp3;*.wav;*.ogg", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            threading.Thread(target=self._thread_audio, args=(dlg.GetPath(),), daemon=True).start()
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
            wx.CallAfter(lambda: ResultDialog(gui.mainFrame, "Vision Assistant - Audio Transcript", res).ShowModal())
        except: wx.CallAfter(ui.message, "Error.")

    def script_solveCaptcha(self, gesture):
        mode = config.conf["VisionAssistant"]["captcha_mode"]
        if mode == 'fullscreen': d, w, h = self._capture_fullscreen()
        else: d, w, h = self._capture_navigator()
        
        is_gov = False
        try:
            if api.getForegroundObject() and "پنجره ملی خدمات دولت هوشمند" in api.getForegroundObject().name: 
                is_gov = True
        except: pass

        if d:
            ui.message("Solving...")
            threading.Thread(target=self._thread_cap, args=(d, is_gov), daemon=True).start()
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

    def script_checkUpdate(self, gesture):
        ui.message("Checking for updates...")
        self.updater.check_for_updates(silent=False)

    def _capture_navigator(self):
        try:
            obj = api.getNavigatorObject()
            if not obj or not obj.location: return None,0,0
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
        if t: 
            ui.message("Translating Clipboard...")
            threading.Thread(target=self._thread_translate, args=(t,), daemon=True).start()
        else:
            ui.message("Clipboard empty.")

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
        "kb:NVDA+shift+u": "checkUpdate",
    }