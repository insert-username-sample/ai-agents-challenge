<RULE[mcp_downloads]>
# Global Rule: Workspace-Isolated Downloads Setup

For every workspace or project context (whether new, old, or separate from the current one), the agent MUST dynamically isolate all downloads to a project-specific folder under `F:\mcp-data\<project-name>`.

1. **Auto-creation**: At the start of any workflow, the agent must check if `F:\mcp-data\<project-name>` (where `<project-name>` is the name of the workspace directory, e.g. "ai agents challenge") exists, and create it if not.
2. **Download Isolation**: All files, outputs, audio overviews, and images downloaded or generated via browser MCP servers (like ChatGPT, Gemini, NotebookLM) must be systematically moved from the default downloads directory (e.g. C:\Users\Admin\Downloads) to `F:\mcp-data\<project-name>`.
3. **Workflow Integration**: The agent must maintain a dedicated workflow `mcp-workspace-downloads.md` under the workspace's workflows directory that details this file monitoring and isolation behavior.
</RULE[mcp_downloads]>
