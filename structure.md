# Project Structure & Frameworks

This document outlines the architecture and technologies used in the **AI Code Explainer** project.

## Core Frameworks

### 1. Python Backend (Gradio)
- **File**: [app.py](file:///d:/AI%20projects/P1_Code_Explainer_App/app.py)
- **Framework**: **Gradio**
- **Purpose**: Provides a local UI and a backend to interact with the Hugging Face Serverless API.
- **Key Features**:
  - Theme toggling (Dark/Light mode).
  - Code input and difficulty level selection.
  - Integration with `Qwen/Qwen2.5-Coder-32B-Instruct` via Hugging Face.

### 2. Web Frontend (HTML/JS/CSS)
- **Files**: [index.html](file:///d:/AI%20projects/P1_Code_Explainer_App/index.html), [script.js](file:///d:/AI%20projects/P1_Code_Explainer_App/script.js), [styles.css](file:///d:/AI%20projects/P1_Code_Explainer_App/styles.css)
- **Framework**: Vanilla JavaScript (no external JS frameworks like React/Vue).
- **Purpose**: A standalone, lightweight web version of the application that communicates directly with the Hugging Face API from the browser.
- **Key Features**:
  - Premium design with glassmorphism and animated backgrounds.
  - LocalStorage integration for API key persistence.
  - Staggered animations for "10 Year Old" explanation mode.

## Project Files Reference

| File | Role |
| :--- | :--- |
| `app.py` | Main entry point for the Gradio-based application. |
| `index.html` | Entry point for the static web version. |
| `script.js` | Frontend logic, API handling, and UI interactions. |
| `styles.css` | Custom styling, including dark mode support and animations. |
| `.env` | Stores environment variables like `HF_API_KEY`. |
| `requirements.txt` | Lists Python dependencies. |

## How to Run

1. **Gradio Version**: Run `python app.py` or use the provided `run_app.bat`.
2. **Web Version**: Open `index.html` directly in your browser (requires an API key entered in the UI).
