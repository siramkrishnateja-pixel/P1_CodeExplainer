import os

# Limit parallelism to save memory and avoid OpenBLAS allocation errors
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import gradio as gr
import requests
import os
from dotenv import load_dotenv

# Load environment variables (locally from .env, or from HF Space Secrets)
load_dotenv()

# Try both HF_API_KEY (manual) and HF_TOKEN (platform default)
raw_key = os.environ.get("HF_API_KEY") or os.environ.get("HF_TOKEN") or ""
HF_API_KEY = raw_key.strip().replace("Bearer ", "").strip("'").strip('"').strip()

MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct").strip()

def explain_code(code: str, level: str):
    if not code or not code.strip():
        return "⚠️ **Please enter some code first so I have something to explain!**"
    
    if not HF_API_KEY or HF_API_KEY == "YOUR_HUGGINGFACE_API_KEY":
        return "⚠️ **API Key Missing:** Please add your `HF_API_KEY` as a Secret in the Hugging Face Space Settings."
    
    # Send request to Hugging Face Serverless API (New Router API)
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # Prompt engineering dynamically based on Radio Selection
    if level == "Improve Code":
        prompt = f"Refactor and improve the following code. First, provide the fully improved code inside a markdown code block. Then, briefly explain the improvements you made.\n\nCODE:\n{code}\n\nIMPROVEMENTS:\n"
    else:
        tone_instruction = "Use zero or very little technical jargon. Provide a simple everyday analogy." if level in ["10 Year Old", "Beginner"] else "Use full technical terminology, analyze architectural decisions, and evaluate best practices."
        prompt = f"Explain this code for a {level} audience. {tone_instruction}\n\nCODE:\n{code}\n\nEXPLANATION:\n"
    
    try:
        response = requests.post(API_URL, headers=headers, json={
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600, 
            "temperature": 0.5
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"].strip()
            return f"### AI Explanation ({level} Level) 🧠\n\n{ai_text}"
        elif response.status_code == 401:
            # Debug info to help the user identify token issues without revealing the full secret
            key_preview = f"{HF_API_KEY[:4]}...{HF_API_KEY[-4:]}" if len(HF_API_KEY) > 10 else "N/A"
            key_len = len(HF_API_KEY)
            return (
                f"⚠️ **Authentication Error (401):** The Hugging Face token is invalid.\n\n"
                f"- **Token Preview**: `{key_preview}`\n"
                f"- **Token Length**: {key_len} chars\n"
                f"- **Action**: Ensure your Secret is named `HF_API_KEY` and contains just the token (no quotes, no 'Bearer')."
            )
        else:
            error_data = response.json() if response.headers.get("content-type") == "application/json" else {"error": response.text}
            error_msg = error_data.get("error", str(response.text))
            return f"⚠️ **API Error ({response.status_code}):** {error_msg}"
            
    except Exception as e:
        return f"⚠️ **Connection Error:** {str(e)}"

# Custom theme defining BOTH the crisp white mode and the rich dark blue mode
custom_theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate"
).set(
    # Light Mode Colors (Crisp White)
    body_background_fill="white",
    body_text_color="#0f172a",
    block_background_fill="*neutral_50",
    block_border_color="*neutral_200",
    
    # Dark Mode Colors (Deep Blue matching your earlier favorite aesthetic: #0b0f19)
    body_background_fill_dark="#0b0f19",
    body_text_color_dark="#f8fafc",
    block_background_fill_dark="rgba(18, 24, 38, 0.8)", # Glassmorphism-style panel
    block_border_color_dark="rgba(255, 255, 255, 0.08)",
    background_fill_primary_dark="#0b0f19",
    background_fill_secondary_dark="rgba(18, 24, 38, 0.8)",
)

# Custom Javascript to swap Gradio's dark/light class on the webpage body
toggle_js = """
function toggleTheme() {
    const isDark = document.body.classList.contains('dark');
    if (isDark) {
        document.body.classList.remove('dark');
    } else {
        document.body.classList.add('dark');
    }
}
"""

with gr.Blocks(theme=custom_theme, title="Code Explainer") as demo:
    with gr.Row(elem_classes="header-row"):
        gr.Markdown(
            """
            # 💻 AI Code Explainer
            Paste your complex code snippet below, and our AI will explain it in plain English.
            """
        )
        # Dedicated button for the user to manually control dark/light mode
        toggle_btn = gr.Button("🌓 Toggle Dark / Light Theme", size="sm", scale=0, min_width=250)
        
    with gr.Row():
        with gr.Column():
            code_input = gr.Code(label="Source Code", language="python", lines=12)
            
            # Simple Radio component for the user to choose Explanation Complexity
            level_radio = gr.Radio(
                choices=["10 Year Old", "Beginner", "Intermediate", "Professional", "Improve Code"],
                value="10 Year Old",
                label="Target Audience (Explanation Complexity)",
                interactive=True
            )
            
            explain_btn = gr.Button("✨ Explain Code", variant="primary")
        
        with gr.Column():
            output_display = gr.Markdown(label="Explanation", value="*Your explanation will appear here...*")
            
    # Connect the UI elements to the python logic
    explain_btn.click(
        fn=explain_code,
        inputs=[code_input, level_radio],
        outputs=[output_display]
    )
    
    # Wire up the theme toggle button to our Javascript function
    toggle_btn.click(
        fn=None,
        inputs=None,
        outputs=None,
        js=toggle_js
    )

if __name__ == "__main__":
    # On Hugging Face Spaces, SPACE_ID is set automatically by the platform
    is_spaces = os.environ.get("SPACE_ID") is not None

    demo.launch(
        server_name="0.0.0.0" if is_spaces else "127.0.0.1",
        server_port=7860,
        ssr_mode=False,
        share=not is_spaces  # share=True locally (public tunnel), False on HF Spaces (already public)
    )
