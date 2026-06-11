import os
import html
import json

TARGET_FILES = [
    "README.md",
    "agents/orchestrator.py",
    "agents/drafter.py",
    "agents/acceptor.py",
    "agents/strategist.py",
    "agents/case_base.py",
    "engine/mcts.py",
    "tools/sfe.py",
    "engine/aeds_sentinel.py",
    "requirements.txt"
]

def generate():
    file_data = {}
    for rel_path in TARGET_FILES:
        full_path = os.path.join("g:\\ai agents challenge", rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            file_data[rel_path] = content
        else:
            file_data[rel_path] = f"# Error: File {rel_path} not found in workspace."

    # Generate JSON serialized representation to dump in the HTML script
    files_json = json.dumps(file_data)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Clausely -- Interactive Code Explorer</title>
  
  <!-- Typography & Syntax Highlighting -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
  
  <style>
    :root {{
      --bg-dark: #070a13;
      --bg-card: rgba(13, 19, 33, 0.85);
      --bg-active: rgba(22, 33, 54, 0.9);
      --border-card: rgba(255, 255, 255, 0.08);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --color-primary: #38bdf8;
      --font-display: 'Outfit', sans-serif;
      --font-body: 'Inter', sans-serif;
      --code-bg: #0b0f19;
    }}

    [data-theme="light"] {{
      --bg-dark: #f8fafc;
      --bg-card: rgba(255, 255, 255, 0.9);
      --bg-active: rgba(241, 245, 249, 0.95);
      --border-card: rgba(15, 23, 42, 0.08);
      --text-main: #0f172a;
      --text-muted: #64748b;
      --color-primary: #0284c7;
      --code-bg: #f1f5f9;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-body);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    header {{
      height: 64px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 1.5rem;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-card);
      backdrop-filter: blur(12px);
      z-index: 10;
    }}

    .logo {{
      font-family: var(--font-display);
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--text-main);
      text-decoration: none;
    }}

    .logo span {{
      color: var(--color-primary);
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-family: var(--font-display);
      font-weight: 600;
      font-size: 0.85rem;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
      border: 1px solid var(--border-card);
      background: var(--bg-active);
      color: var(--text-main);
    }}

    .btn:hover {{
      background: var(--bg-card);
      border-color: var(--color-primary);
    }}

    /* Main split container */
    .workspace {{
      display: flex;
      flex-grow: 1;
      height: calc(100vh - 64px);
      overflow: hidden;
    }}

    /* Sidebar Navigation */
    .sidebar {{
      width: 280px;
      border-right: 1px solid var(--border-card);
      background: var(--bg-card);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      overflow-y: auto;
      padding: 1rem;
    }}

    .sidebar-title {{
      font-family: var(--font-display);
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 1rem;
      padding-left: 0.5rem;
    }}

    .file-tree {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}

    .file-item {{
      padding: 0.6rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.88rem;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--text-main);
    }}

    .file-item:hover {{
      background: var(--bg-active);
      color: var(--color-primary);
    }}

    .file-item.active {{
      background: var(--bg-active);
      color: var(--color-primary);
      border: 1px solid rgba(56, 189, 248, 0.2);
      font-weight: 600;
    }}

    /* Code Viewport */
    .code-viewport {{
      flex-grow: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      background: var(--code-bg);
    }}

    .code-header {{
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-card);
      padding: 0.75rem 1.5rem;
      font-family: monospace;
      font-size: 0.85rem;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .code-container {{
      flex-grow: 1;
      overflow: auto;
      padding: 1.5rem;
    }}

    pre {{
      margin: 0 !important;
      background: transparent !important;
      font-size: 0.88rem !important;
    }}

    code {{
      font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace !important;
    }}
  </style>
</head>
<body>
  
  <header>
    <a href="/" class="logo">clausely<span>.ai</span></a>
    <div class="header-controls">
      <a href="/" class="btn"><- Back</a>
      <button class="btn" id="theme-toggle-btn" onclick="toggleTheme()">Theme: Dark</button>
    </div>
  </header>

  <div class="workspace">
    <!-- Sidebar File Browser -->
    <div class="sidebar">
      <div class="sidebar-title">clausely-adk repository</div>
      <div class="file-tree" id="file-list">
        <!-- Javascript renders files here -->
      </div>
    </div>

    <!-- Code Viewport -->
    <div class="code-viewport">
      <div class="code-header">
        <span id="current-filename">README.md</span>
        <span style="font-size: 0.75rem; text-transform: uppercase;" id="code-lang">markdown</span>
      </div>
      <div class="code-container">
        <pre><code class="language-markdown" id="code-block">Loading repository data...</code></pre>
      </div>
    </div>
  </div>

  <!-- Syntax Highlighting Scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>

  <script>
    // Embedded Code database
    const filesDb = {files_json};

    // Load file list into sidebar
    const fileList = document.getElementById('file-list');
    
    function initFileTree() {{
      fileList.innerHTML = '';
      Object.keys(filesDb).forEach(path => {{
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerText = '[] ' + path;
        div.onclick = () => selectFile(path, div);
        fileList.appendChild(div);
      }});
      
      // Select first file by default (README.md)
      const firstItem = fileList.firstElementChild;
      if (firstItem) {{
        selectFile("README.md", firstItem);
      }}
    }}

    function selectFile(path, element) {{
      document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));
      element.classList.add('active');

      document.getElementById('current-filename').innerText = path;
      
      // Determine language for Prism
      let lang = 'python';
      if (path.endsWith('.md')) lang = 'markdown';
      else if (path.endsWith('.txt')) lang = 'text';
      
      document.getElementById('code-lang').innerText = lang;

      const codeBlock = document.getElementById('code-block');
      codeBlock.className = 'language-' + lang;
      
      // HTML escape content to prevent script injection
      const escapedContent = escapeHtml(filesDb[path]);
      codeBlock.innerHTML = escapedContent;

      // Re-run Prism highlighting
      Prism.highlightElement(codeBlock);
    }}

    function escapeHtml(text) {{
      return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }}

    // Theme Toggle Logic
    let currentTheme = 'dark';
    function toggleTheme() {{
      const body = document.body;
      const btn = document.getElementById('theme-toggle-btn');
      if (currentTheme === 'dark') {{
        body.setAttribute('data-theme', 'light');
        btn.innerText = 'Theme: Light';
        currentTheme = 'light';
      }} else {{
        body.removeAttribute('data-theme');
        btn.innerText = 'Theme: Dark';
        currentTheme = 'dark';
      }}
    }}

    // Initialize Page
    initFileTree();
  </script>
</body>
</html>
"""

    output_path = "g:\\ai agents challenge\\public\\code.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print("code.html generated successfully.")

if __name__ == "__main__":
    generate()
