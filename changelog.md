## Changes for 3.0.2
*   **Batch OCR:** Added support for selecting and processing multiple images or PDF files simultaneously. The files are now processed in alphabetical order.
*   **Compatibility Fix:** Bundled the `markdown` library within the add-on to resolve startup errors (ModuleNotFoundError) on NVDA 2024.3+ and ensure stability across all versions.
*   **Code Safety:** Implemented a safer import mechanism to prevent conflicts with other add-ons or NVDA's internal libraries.
*   **Translation:** Fixed an issue where the "Custom:" prefix in the Refine menu was not translatable.