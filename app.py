import os

# Limit parallelism to save memory and avoid OpenBLAS allocation errors
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import gradio as gr
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

raw_key = os.environ.get("HF_API_KEY", "YOUR_HUGGINGFACE_API_KEY").strip()
HF_API_KEY = raw_key.replace("Bearer ", "").replace("'", "").replace('"', '')
MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct").strip()

def explain_code(code: str, level: str):
    if not code or not code.strip():
        return "⚠️ **Please enter some code first so I have something to explain!**"
    
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
        else:
            error_msg = response.json().get("error", str(response.text))
            return f"⚠️ **API Error:** {error_msg}"
            
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

with gr.Blocks(title="Code Explainer") as demo:
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
    # Check if running on Hugging Face Spaces specifically
    is_spaces = os.environ.get("SPACE_ID") is not None
    
    demo.launch(
        server_name="0.0.0.0" if is_spaces else "127.0.0.1",
        server_port=7865, # Keeping your custom port 7865
        theme=custom_theme,
        ssr_mode=False,
        share=not is_spaces  # Enable sharing only if NOT on HF Spaces
    )
