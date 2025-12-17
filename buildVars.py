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
    addon_version="3.0.2",
    # Brief changelog for this version
    # Translators: what's new content for the add-on version to be shown in the add-on store
    addon_changelog=_("""## Changes for 3.0.2
*   **Batch OCR:** Added support for selecting and processing multiple images or PDF files simultaneously. The files are now processed in alphabetical order.
*   **Compatibility Fix:** Bundled the `markdown` library within the add-on to resolve startup errors (ModuleNotFoundError) on NVDA 2024.3+ and ensure stability across all versions.
*   **Code Safety:** Implemented a safer import mechanism to prevent conflicts with other add-ons or NVDA's internal libraries.
*   **Translation:** Fixed an issue where the "Custom:" prefix in the Refine menu was not translatable."""),
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