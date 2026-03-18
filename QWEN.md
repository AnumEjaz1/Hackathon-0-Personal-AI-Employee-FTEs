# Personal AI Employee (Digital FTE) Project

## Project Overview

This is a **hackathon project** for building a "Personal AI Employee" or "Digital FTE" (Full-Time Equivalent) - an autonomous AI agent that manages personal and business affairs 24/7. The project uses **Claude Code** as the reasoning engine and **Obsidian** (local Markdown) as the dashboard/memory system.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian Vault | Local Markdown dashboard and long-term memory |
| **Senses (Watchers)** | Python scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI |
| **Hands (MCP)** | Model Context Protocol servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Stop hook pattern for autonomous multi-step completion |

### Key Concepts

- **Watchers:** Lightweight Python scripts that run continuously, monitoring inputs and creating actionable `.md` files in `/Needs_Action` folder
- **Human-in-the-Loop (HITL):** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Ralph Wiggum Pattern:** A Stop hook that keeps Claude iterating until tasks are complete
- **Business Handover:** Autonomous weekly audits generating "Monday Morning CEO Briefing"

## Directory Structure

```
Hackathon-0-Personal-AI-Employee-FTEs/
├── .agents/
│   └── skills/
│       └── browsing-with-playwright/    # Browser automation skill
│           ├── SKILL.md                  # Skill documentation
│           ├── references/
│           │   └── playwright-tools.md   # MCP tool reference
│           └── scripts/
│               ├── mcp-client.py         # Universal MCP client (HTTP + stdio)
│               ├── start-server.sh       # Start Playwright MCP server
│               ├── stop-server.sh        # Stop Playwright MCP server
│               └── verify.py             # Server health check
├── .gitattributes                        # Git text normalization
├── skills-lock.json                      # Skill version tracking
└── Personal AI Employee Hackathon 0_...md  # Full architectural blueprint
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Sentinel scripts & orchestration |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers & automation |
| [Github Desktop](https://desktop.github.com/download/) | Latest | Version control |

### Hardware Requirements

- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage
- **For always-on:** Dedicated mini-PC or cloud VM

### Setup Checklist

```bash
# 1. Create Obsidian vault named "AI_Employee_Vault"
# Structure:
#   /Inbox          - Raw incoming items
#   /Needs_Action   - Items requiring AI processing
#   /Done           - Completed tasks
#   /Plans          - Generated plans
#   /Pending_Approval - Awaiting human approval
#   /Approved       - Approved actions ready to execute

# 2. Verify Claude Code
claude --version

# 3. Set up Python virtual environment (UV recommended)
# 4. Install Node.js dependencies for MCP servers
```

### Playwright MCP Skill Usage

```bash
# Start the Playwright MCP server
bash .agents/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .agents/skills/browsing-with-playwright/scripts/verify.py

# Stop the server (closes browser first)
bash .agents/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools from HTTP server
python scripts/mcp-client.py list -u http://localhost:8808

# Call a tool
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Emit tool schemas as markdown
python scripts/mcp-client.py emit -u http://localhost:8808
```

## Development Conventions

### Skill Structure

All agent skills follow the pattern in `.agents/skills/<skill-name>/`:
- `SKILL.md` - Skill documentation with usage examples
- `references/` - Tool documentation (auto-generated via `mcp-client.py emit`)
- `scripts/` - Helper scripts for server lifecycle and verification

### MCP Integration Pattern

1. **Start server** with `--shared-browser-context` flag for stateful sessions
2. **Verify** server is running before operations
3. **Use `browser_snapshot`** to get element refs before interaction
4. **Stop server** at end of browser tasks to free resources

### Human-in-the-Loop Workflow

For sensitive actions (payments, sending emails):

1. Claude creates approval request in `/Pending_Approval/<ACTION>_<ID>.md`
2. User reviews and moves file to `/Approved` or `/Rejected`
3. Orchestrator detects approved files and triggers MCP action
4. Result logged and task moved to `/Done`

### Watcher Pattern

All Watchers inherit from `BaseWatcher`:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        '''Main loop: check, create files, sleep'''
```

## Recommended MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `slack-mcp` | Send messages, read channels | Team communication |

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Dashboard.md, one Watcher, basic folder structure |
| **Silver** | 20-30 hrs | Multiple Watchers, Plan.md generation, one MCP server, HITL |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, weekly audit, Ralph Wiggum loop |
| **Platinum** | 60+ hrs | Cloud deployment, domain specialization, A2A upgrade |

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Complete architectural blueprint (1201 lines) |
| `skills-lock.json` | Tracks installed skill versions and sources |
| `.agents/skills/browsing-with-playwright/SKILL.md` | Browser automation skill documentation |
| `.agents/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client (HTTP + stdio transports) |

## Testing Practices

- **Verification scripts:** Each skill includes `verify.py` for health checks
- **Server lifecycle:** Start → Verify → Operate → Stop pattern
- **Graceful degradation:** Error recovery with logging

## Contribution Guidelines

1. All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
2. Skills must include verification scripts
3. Document server lifecycle (start/stop/verify)
4. Preserve secrets: `.env`, tokens, sessions never sync via Git

## Weekly Research Meeting

- **When:** Wednesdays at 10:00 PM PKT
- **Zoom:** [Meeting Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity Channel](https://www.youtube.com/@panaversity)
