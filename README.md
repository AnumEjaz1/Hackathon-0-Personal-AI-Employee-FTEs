# AI Employee - Bronze Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A personal AI employee that proactively manages your tasks using **Qwen Code** as the reasoning engine and the **`.qwen`** folder as the local dashboard. This is the **Bronze Tier** implementation - the foundation for autonomous task management.

## 📋 Bronze Tier Deliverables

✅ **Completed:**
- [x] `.qwen` folder with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System monitoring)
- [x] Qwen Code integration for reading/writing to the vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] Orchestrator for managing watchers and processing items

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EXTERNAL TRIGGERS                     │
│         (File drops into .qwen/Inbox folder)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │   FileDropWatcher (monitors Inbox folder)       │    │
│  └─────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  .QWEN FOLDER (Local)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ /Inbox        → Drop files here                   │  │
│  │ /Needs_Action → Items to process                  │  │
│  │ /Done         → Completed tasks                   │  │
│  │ /Plans        → AI-generated plans                │  │
│  │ /Pending_Approval → Awaiting human decision       │  │
│  │ /Approved     → Ready to execute                  │  │
│  │ /Logs         → Audit trail                       │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ Dashboard.md         → Real-time status           │  │
│  │ Company_Handbook.md  → Rules of engagement        │  │
│  │ Business_Goals.md    → Objectives & metrics       │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  REASONING LAYER                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │   Orchestrator (manages watchers, triggers AI)  │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │   Qwen Code (analyze, plan, write reports)      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Hackathon-0-Personal-AI-Employee-FTEs/
├── .qwen/                      # Main vault folder
│   ├── Inbox/                  # Drop files here for processing
│   ├── Needs_Action/           # Items awaiting processing
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # AI-generated plans
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Approved actions ready to execute
│   ├── Rejected/               # Rejected actions
│   ├── Logs/                   # Audit logs
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   └── Business_Goals.md       # Objectives and metrics
├── src/
│   ├── base_watcher.py         # Base class for all watchers
│   └── orchestrator.py         # Main orchestration process
├── requirements.txt            # Python dependencies
├── verify_bronze.py            # Bronze tier verification script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Qwen Code](https://github.com/anthropics/qwen-code) | Active subscription | Reasoning engine |

### Installation

1. **Clone or download this repository**

2. **Verify Python version**
   ```bash
   python --version  # Should be 3.13 or higher
   ```

3. **Install dependencies (optional for Bronze Tier)**
   ```bash
   pip install -r requirements.txt
   ```
   Note: Bronze Tier has no external dependencies.

### Running the AI Employee

1. **Start the Orchestrator**
   ```bash
   # From the project root directory
   python src/orchestrator.py .qwen
   ```

2. **Drop a file into the Inbox**
   - Any file dropped into `.qwen/Inbox/` will be automatically detected
   - An action file will be created in `Needs_Action/`
   - The Dashboard will update in real-time

3. **Process items with Qwen Code**
   ```bash
   # In a new terminal, navigate to the .qwen folder
   cd .qwen
   
   # Invoke Qwen Code to process pending items
   qwen "Check the Needs_Action folder and process any pending items. Create plans for each item."
   ```

4. **Monitor the Dashboard**
   - Open `Dashboard.md` in any text editor or Markdown viewer
   - Watch it update as items are processed

### Stopping

Press `Ctrl+C` in the orchestrator terminal to gracefully shut down.

## 📖 Usage Guide

### How It Works

1. **File Drop** → Drag any file into the `.qwen/Inbox/` folder
2. **Auto-Detection** → FileDropWatcher detects the new file every 5 seconds
3. **Action File Created** → A markdown file with metadata is created in `Needs_Action/`
4. **AI Processing** → Qwen Code reads the action file and creates a plan
5. **Human Approval** → For sensitive actions, move files to `Pending_Approval/`
6. **Execution** → Once approved, actions are executed and moved to `Done/`

### Folder Workflow

```
Inbox/ → (Watcher detects) → Needs_Action/ → (Qwen processes) → Plans/
                                                      ↓
                                              Pending_Approval/
                                                      ↓ (Human approves)
                                                 Approved/ → (Execute) → Done/
```

### Dashboard

The `Dashboard.md` file is auto-updated every 30 seconds with:
- Number of pending actions
- Pending approvals requiring your attention
- Session statistics (uptime, items processed)
- Recent activity log

## 🔧 Configuration

### Watcher Intervals

Edit `src/orchestrator.py` to adjust check intervals:

```python
WatcherConfig("file_drop", "FileDropWatcher", check_interval=5),  # Check every 5 seconds
```

### Adding New Watchers

1. Create a new watcher class in `src/` extending `BaseWatcher`
2. Implement `check_for_updates()` and `create_action_file()`
3. Register in `orchestrator.py`:
   ```python
   WatcherConfig("gmail", "GmailWatcher", check_interval=120),
   ```

## 📊 Bronze Tier Features

| Feature | Status | Description |
|---------|--------|-------------|
| File Drop Watcher | ✅ | Monitors Inbox for new files |
| Action File Creation | ✅ | Creates markdown action files |
| Dashboard Updates | ✅ | Real-time status tracking |
| Folder Structure | ✅ | Complete vault organization |
| Company Handbook | ✅ | Rules of engagement defined |
| Qwen Code Integration | ⚠️ | Manual invocation (upgrade to Silver for auto) |
| Approval Workflow | ⚠️ | Manual file movement (upgrade to Silver for auto) |
| MCP Servers | ❌ | Silver tier feature |
| Gmail/WhatsApp Watchers | ❌ | Silver tier feature |

⚠️ = Partial (requires manual steps)  
❌ = Not included (higher tier feature)

## 🎯 Next Steps (Silver Tier)

To upgrade to Silver Tier, add:
1. **Gmail Watcher** - Monitor Gmail for important emails
2. **WhatsApp Watcher** - Monitor WhatsApp for urgent messages
3. **MCP Server** - Enable automated email sending
4. **Auto-Approval Workflow** - Automated file movement between folders
5. **Scheduled Tasks** - Cron/Task Scheduler integration

## 🐛 Troubleshooting

### Orchestrator won't start
- Ensure Python 3.13+ is installed
- Check that `.qwen/` folder exists
- Verify no other process is locking the vault files

### Files not being detected
- Ensure files are dropped into `Inbox/` (not `Needs_Action/`)
- Check orchestrator logs for errors
- Verify file permissions allow reading

### Dashboard not updating
- Orchestrator updates every 30 seconds
- Refresh your text editor
- Check orchestrator is still running

## 📝 License

This project is part of the Personal AI Employee Hackathon 0.

## 📞 Support

- **Weekly Research Meeting:** Wednesdays at 10:00 PM PKT
- **Zoom:** [Meeting Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity Channel](https://www.youtube.com/@panaversity)

---

*Built with ❤️ for the AI Employee Hackathon 0*
