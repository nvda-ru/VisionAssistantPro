# -*- coding: UTF-8 -*-
from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
    addon_name="VisionAssistant",
    # Add-on summary/title, usually the user visible name of the add-on
    # Translators: Summary/title for this add-on
    # to be shown on installation and add-on information found in add-on store
    addon_summary=_("Vision Assistant Pro"),
    # Add-on description
    # Translators: Long description to be shown for this add-on on add-on information from add-on store
    addon_description=_("""An advanced AI assistant for NVDA using Gemini models.
Features:
- Smart Translator (NVDA+Ctrl+Shift+T/Y)
- Smart Dictation (NVDA+Ctrl+Shift+S)
- Text Refiner (NVDA+Ctrl+Shift+R)
- Vision & Screen Analysis (NVDA+Ctrl+Shift+V/O)
- Document QA (NVDA+Ctrl+Shift+D)
- CAPTCHA Solver (NVDA+Ctrl+Shift+C)
- Audio Transcription (NVDA+Ctrl+Shift+A)
- File Selection & OCR (NVDA+Ctrl+Shift+F)
- Status Reporting (NVDA+Ctrl+Shift+I)"""),
    addon_version="2.8.0",
    # Brief changelog for this version
    # Translators: what's new content for the add-on version to be shown in the add-on store
    addon_changelog=_("""## Changes for 2.8
*   **Added Italian translation.**
*   **Status Reporting:** Added a new command (`NVDA+Control+Shift+I`) to announce the current status.
*   **HTML Export:** "Save Content" now saves as formatted HTML.
*   **Settings UI:** Improved layout with accessible grouping.
*   **New Models:** Added `gemini-flash-latest` and `gemini-flash-lite-latest`.
*   **Languages:** Added **Nepali**.
*   **Refine Menu Logic:** Fixed a bug where commands failed in non-English interfaces.
*   **Dictation:** Improved silence detection.
*   **Update Settings:** Auto-update check is now disabled by default.
*   **Code Cleanup.**"""),
    addon_author="Mahmood Hozhabri",
    addon_url="https://github.com/mahmoodhozhabri/VisionAssistantPro",
    addon_sourceURL="https://github.com/mahmoodhozhabri/VisionAssistantPro",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2019.3",
    addon_lastTestedNVDAVersion="2025.3.1",
    addon_updateChannel=None,
    addon_license="GPL-2.0",
    addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

pythonSources: list[str] = ["addon/globalPlugins/visionAssistant/*.py"]
i18nSources = pythonSources + ["buildVars.py"]
excludedFiles: list[str] = []

baseLanguage: str = "en"

markdownExtensions: list[str] = [
    "markdown.extensions.tables",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
    "markdown.extensions.extra",
]

brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}