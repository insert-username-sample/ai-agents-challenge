# Workspace-Isolated Downloads Workflow

This workflow details how the agent dynamically isolates and coordinates browser downloads for individual projects.

## Execution Sequence

1. **Resolve Project Name:** Identify the name of the current workspace directory (e.g. `ai agents challenge`).
2. **Create Target Directory:** Ensure the folder `F:\mcp-data\<project-name>` exists:
   ```powershell
   New-Item -ItemType Directory -Force -Path "F:\mcp-data\<project-name>"
   ```
3. **Monitor Default Downloads:** When a download action is triggered in ChatGPT Web, Gemini Web, or NotebookLM Web, monitor `C:\Users\Admin\Downloads` for the newest file.
4. **Relocate Downloads:** Move the file to `F:\mcp-data\<project-name>` immediately upon download completion to preserve the workspace context.
