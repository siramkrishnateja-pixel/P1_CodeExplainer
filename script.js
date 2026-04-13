document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const explainBtn = document.getElementById('explainBtn');
    const codeInput = document.getElementById('codeInput');
    const outputContent = document.getElementById('outputContent');
    const loaderContainer = document.getElementById('loaderContainer');
    const statusBadge = document.getElementById('statusBadge');
    
    const themeToggleBtn = document.getElementById('themeToggle');
    const themeIcon = themeToggleBtn.querySelector('.theme-icon');
    const themeText = themeToggleBtn.querySelector('.theme-text');
    
    // Level Selection Logic
    const levelSelector = document.getElementById('levelSelector');
    const pills = levelSelector.querySelectorAll('.pill');
    let currentLevel = "10 Year Old"; // Default
    
    const apiKeyInput = document.getElementById('apiKeyInput');
    
    // Load previously saved API key from localStorage
    if (localStorage.getItem('hf_api_key')) {
        apiKeyInput.value = localStorage.getItem('hf_api_key');
    }
    // Save to localStorage when changed
    apiKeyInput.addEventListener('input', (e) => {
        localStorage.setItem('hf_api_key', e.target.value.trim());
    });

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentLevel = pill.dataset.level;
            
            // Adjust button text slightly to match the explanation vibe
            const btnText = explainBtn.querySelector('.btn-text');
            if (currentLevel === "Professional") {
                btnText.textContent = 'Generate Deep Analysis';
            } else if (currentLevel === "Improve Code") {
                btnText.textContent = 'Optimize & Refactor';
            } else if (currentLevel === "Intermediate") {
                btnText.textContent = 'Explain Architecture';
            } else if (currentLevel === "Beginner") {
                btnText.textContent = 'Explain Basics';
            } else {
                btnText.textContent = 'Explain in Simple Words';
            }
        });
    });

    // Theme Toggling Logic
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        
        const isDark = document.body.classList.contains('dark-mode');
        if (isDark) {
            themeIcon.textContent = '☀️';
            themeText.textContent = 'Light Mode';
        } else {
            themeIcon.textContent = '🌙';
            themeText.textContent = 'Dark Mode';
        }
    });

    // Explain Button Logic
    explainBtn.addEventListener('click', async () => {
        const code = codeInput.value.trim();
        
        // Validation
        if (!code) {
            outputContent.innerHTML = `
                <div style="color: #ef4444; text-align: center; padding: 2rem;">
                    <p>Please enter some code first so I have something to explain!</p>
                </div>
            `;
            return;
        }

        // 1. UI changes to loading state
        const originalBtnText = explainBtn.querySelector('.btn-text').textContent;
        explainBtn.disabled = true;
        explainBtn.querySelector('.btn-text').textContent = 'Analyzing Code...';
        outputContent.style.display = 'none';
        loaderContainer.style.display = 'flex';
        statusBadge.textContent = 'Processing';
        statusBadge.style.color = '#f59e0b';
        statusBadge.style.background = 'rgba(245, 158, 11, 0.1)';
        statusBadge.style.borderColor = 'rgba(245, 158, 11, 0.2)';

        // 2. Real Hugging Face API Call
        let HF_API_KEY = apiKeyInput.value.trim();
        // Automatically clean up accidental "Bearer" prefixes or quotes
        HF_API_KEY = HF_API_KEY.replace(/^Bearer\s+/i, '').replace(/['"]/g, '').trim();
        
        if (!HF_API_KEY) {
            explainBtn.disabled = false;
            explainBtn.querySelector('.btn-text').textContent = originalBtnText;
            loaderContainer.style.display = 'none';
            outputContent.style.display = 'block';
            
            statusBadge.textContent = 'Key Required';
            statusBadge.style.color = '#ef4444';
            statusBadge.style.background = 'transparent';
            statusBadge.style.borderColor = 'transparent';
            
            outputContent.innerHTML = `
                <div style="color: #ef4444; font-size: 1.1rem; text-align: center; padding: 2rem;">
                    <p><strong>⚠️ Missing API Key!</strong></p>
                    <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 10px;">Please paste your Hugging Face token in the input box on the right side of the options bar to continue. Your key is safely saved in your local browser storage!</p>
                </div>
            `;
            return;
        }

        const MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct";

        try {
            let prompt = "";
            if (currentLevel === "Improve Code") {
                prompt = `Refactor and improve the following code. First, provide the fully improved code inside a markdown code block. Then, briefly explain the improvements you made.\n\nCODE:\n${code}\n\nIMPROVEMENTS:\n`;
            } else {
                const toneInstruction = (currentLevel === "10 Year Old" || currentLevel === "Beginner") 
                    ? "Use zero or very little technical jargon. Provide a simple everyday analogy." 
                    : "Use full technical terminology, analyze architectural decisions, and evaluate best practices.";
                    
                prompt = `Explain this code for a ${currentLevel} audience. ${toneInstruction}\n\nCODE:\n${code}\n\nEXPLANATION:\n`;
            }

            const response = await fetch(`https://router.huggingface.co/v1/chat/completions`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${HF_API_KEY}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    model: MODEL_ID,
                    messages: [{ role: "user", content: prompt }],
                    max_tokens: 600, 
                    temperature: 0.5
                }),
            });

            // Restore UI
            explainBtn.disabled = false;
            explainBtn.querySelector('.btn-text').textContent = originalBtnText;
            loaderContainer.style.display = 'none';
            outputContent.style.display = 'block';

            if (!response.ok) {
                const errorData = await response.json();
                statusBadge.textContent = 'Error';
                statusBadge.style.color = '#ef4444';
                outputContent.innerHTML = `<p style="color: #ef4444;">API Error: ${errorData.error || response.statusText}</p>`;
                return;
            }

            const result = await response.json();
            statusBadge.textContent = 'Completed';
            statusBadge.style.color = '#10b981';
            statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
            statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.2)';

            // Clean up and display generated text
            let aiText = "Could not parse explanation.";
            if (result.choices && result.choices.length > 0) {
                aiText = result.choices[0].message.content.trim();
            }
            
            let finalHtml = "";

            if (currentLevel === "10 Year Old") {
                // Feature 1: Short staggered animations when "10 Year Old" is selected!
                const paragraphs = aiText.split('\n\n').filter(p => p.trim() !== '');
                
                const animatedHtml = paragraphs.map((p, index) => {
                    const delay = index * 400; // 400ms stagger between paragraphs
                    const formattedLine = p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    return `<div class="animated-item" style="animation-delay: ${delay}ms">${formattedLine}</div>`;
                }).join('');

                finalHtml = `
                    <div class="kids-mode-container">
                        <div class="kids-star" style="top: 10%; right: 10%;">🚀</div>
                        <div class="kids-star" style="bottom: 20%; left: 5%; animation-delay: -1s;">🌟</div>
                        <div class="kids-star" style="top: 40%; right: 5%; animation-delay: -2s; font-size: 1.5rem;">🎈</div>
                        <div class="kids-star" style="bottom: 5%; right: 30%; animation-delay: -1.5s; font-size: 2rem;">✨</div>
                        <div style="position: relative; z-index: 10;">${animatedHtml}</div>
                    </div>
                `;
            } else {
                // Feature 2: Standard Markdown parser for the other modes
                const formattedText = aiText
                    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.05); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: monospace; border: 1px solid rgba(0,0,0,0.1); margin: 1rem 0;"><code>$1</code></pre>')
                    .replace(/```([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.05); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: monospace; border: 1px solid rgba(0,0,0,0.1); margin: 1rem 0;"><code>$1</code></pre>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n\n/g, '</p><p>');

                finalHtml = `<div style="font-size: 1.05rem; line-height: 1.8;"><p>${formattedText}</p></div>`;
            }

            outputContent.innerHTML = finalHtml;

        } catch (error) {
            console.error("HF API Connection Error:", error);
            explainBtn.disabled = false;
            explainBtn.querySelector('.btn-text').textContent = 'Explain in Simple Words';
            loaderContainer.style.display = 'none';
            outputContent.style.display = 'block';
            
            statusBadge.textContent = 'Connection Error';
            statusBadge.style.color = '#ef4444';
            outputContent.innerHTML = `
                <p style="color: #ef4444; font-weight: bold;">Failed to connect to Hugging Face API.</p>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid #ef4444;">
                    <p style="font-size: 0.9rem; color: #ef4444; margin: 0; font-family: monospace;"><strong>Error Details:</strong> ${error.message}</p>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 8px;"><strong>Tip:</strong> If you opened this HTML file directly (you see "file:///" in your address bar), your browser likely blocked it for security (CORS). Try running 'python app.py' in your terminal instead!</p>
                </div>
            `;
        }
    });
});
