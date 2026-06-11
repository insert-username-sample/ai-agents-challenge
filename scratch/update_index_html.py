import re
from pathlib import Path

def main():
    filepath = Path("g:/ai agents challenge/demo_video/index.html")
    content = filepath.read_text(encoding="utf-8")
    
    # 1. Update Font Import
    content = content.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">',
        '<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">'
    )
    
    # 2. Update Font Families
    content = content.replace("'Outfit', sans-serif", "'Comfortaa', cursive")
    content = content.replace("'Outfit'", "'Comfortaa'")
    
    # 3. Update Logo Styling
    logo_style_old = """      .logo {
        font-family: 'Comfortaa', cursive;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #f8fafc;
      }
      .logo span {
        color: #06b6d4;
      }"""
      
    logo_style_new = """      .logo-container {
        display: flex;
        align-items: center;
        gap: 16px;
      }
      .logo-img {
        width: 54px;
        height: 54px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.35);
        object-fit: contain;
      }
      .logo-text {
        font-family: 'Comfortaa', cursive;
        font-size: 2.5rem;
        font-weight: 700;
        color: #f8fafc;
      }
      .logo-text span {
        color: #06b6d4;
      }"""
    
    content = content.replace(logo_style_old, logo_style_new)
    
    # 4. Update Header Branding HTML
    header_old = """      <!-- Header Branding -->
      <div class="video-header">
        <div class="logo">clausely<span>.ai</span></div>
        <div class="badge">GOOGLE AGENTS CHALLENGE 2026</div>
      </div>"""
      
    header_new = """      <!-- Header Branding -->
      <div class="video-header">
        <div class="logo-container">
          <img src="assets/clausely_logo.png" class="logo-img" alt="Clausely Logo">
          <div class="logo-text">clausely<span>.ai</span></div>
        </div>
        <div class="badge">GOOGLE AGENTS CHALLENGE 2026</div>
      </div>"""
      
    content = content.replace(header_old, header_new)
    
    # 5. Replace Slide 1 Right Panel (no screenshots)
    panel_old = """          <div class="right-panel">
            <div class="error-wrapper" id="err-card1" style="opacity: 0;">
              <img src="assets/gemini_3.5_flash_error_1.png" class="error-img" alt="Gemini Error">
            </div>
            <div class="stamp" id="stamp1" style="opacity: 0;">REJECTED</div>
          </div>"""
          
    panel_new = """          <div class="right-panel">
            <div class="glass-card error-details-card" id="err-card1" style="opacity: 0; border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 40px rgba(239, 68, 68, 0.2); width: 100%; max-width: 750px;">
              <div class="card-header" style="color: #ef4444; border-bottom-color: rgba(239, 68, 68, 0.15);">
                <span>🚨 Neural Shortcut Failure (LLM Hallucination)</span>
              </div>
              <div class="code-block" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.1); background: #0c080e; font-size: 1.25rem; line-height: 1.6; padding: 25px;">
                <span style="color: #64748b;">Input Intent:</span> "Draft Nagpur Writ Petition for Vidya Khobrekar"<br>
                <span style="color: #ef4444;">LLM Output:</span> "...the Petitioner herein, Smt. Vidya, is the daughter..."<br><br>
                <span style="color: #f8fafc; font-weight: 700;">>>> FACT AUDIT ERROR [Verifier Agent]:</span><br>
                Bombay High Court Nagpur Bench WP 4769/2021 records confirm Smt. Vidya Khobrekar is the mother of the applicant (son), not daughter. Filing invalidated.
              </div>
            </div>
            <div class="stamp" id="stamp1" style="opacity: 0; z-index: 20;">REJECTED</div>
          </div>"""
          
    content = content.replace(panel_old, panel_new)
    
    filepath.write_text(content, encoding="utf-8")
    print("Successfully updated index.html branding, typography, and removed screenshots!")

if __name__ == "__main__":
    main()
