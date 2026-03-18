#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee system.

The Orchestrator:
1. Manages watcher processes (FileDrop, Gmail, WhatsApp, etc.)
2. Monitors Needs_Action folder for items to process
3. Triggers Qwen Code to analyze and create plans
4. Updates Dashboard.md with current status
5. Handles approved actions and moves completed items to Done

Usage:
    python orchestrator.py /path/to/vault
    python orchestrator.py  # Uses current directory
"""

import os
import sys
import time
import logging
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import FileDropWatcher, BaseWatcher

# Configure logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


@dataclass
class WatcherConfig:
    """Configuration for a watcher instance."""
    name: str
    class_name: str
    check_interval: int
    enabled: bool = True


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates watchers, processes action items, and maintains the dashboard.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        self.logger = logging.getLogger("Orchestrator")
        
        # Core folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.needs_action, self.done, self.plans, 
                       self.pending_approval, self.approved, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Watchers registry
        self.watchers: Dict[str, BaseWatcher] = {}
        self.watcher_configs = [
            WatcherConfig("file_drop", "FileDropWatcher", check_interval=5),
            # Add more watchers here as they are implemented:
            # WatcherConfig("gmail", "GmailWatcher", check_interval=120),
            # WatcherConfig("whatsapp", "WhatsAppWatcher", check_interval=30),
        ]
        
        # Control flags
        self._running = False
        self.process_interval = 10  # Check for items to process every 10 seconds
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'actions_created': 0,
            'approvals_pending': 0,
            'approvals_completed': 0,
            'start_time': None
        }
        
        self.logger.info(f"Orchestrator initialized for: {self.vault_path}")
    
    def register_watcher(self, watcher: BaseWatcher):
        """Register a watcher instance."""
        self.watchers[watcher.__class__.__name__] = watcher
        self.logger.info(f"Registered watcher: {watcher.__class__.__name__}")
    
    def start_watchers(self):
        """Start all registered watchers in background threads."""
        import threading
        
        for name, watcher in self.watchers.items():
            thread = threading.Thread(target=watcher.run, daemon=True)
            thread.start()
            self.logger.info(f"Started watcher thread: {name}")
    
    def stop_watchers(self):
        """Stop all watchers gracefully."""
        for name, watcher in self.watchers.items():
            watcher.stop()
            self.logger.info(f"Stopped watcher: {name}")
    
    def process_needs_action(self):
        """
        Process items in the Needs_Action folder.
        
        For Bronze tier: Just count and log items.
        For Silver/Gold: Trigger Qwen Code to analyze and create plans.
        """
        try:
            action_files = list(self.needs_action.glob('*.md'))
            
            if not action_files:
                return
            
            self.logger.info(f"Found {len(action_files)} item(s) in Needs_Action")
            
            for action_file in action_files:
                self._process_single_item(action_file)
                
        except Exception as e:
            self.logger.error(f"Error processing Needs_Action: {e}")
    
    def _process_single_item(self, action_file: Path):
        """
        Process a single action item.
        
        Bronze tier: Log the item and update dashboard.
        Silver/Gold: Call Qwen Code to analyze and create plan.
        """
        try:
            content = action_file.read_text(encoding='utf-8')
            
            # Extract metadata from frontmatter
            metadata = self._parse_frontmatter(content)
            
            self.logger.info(f"Processing: {action_file.name}")
            self.logger.info(f"  Type: {metadata.get('type', 'unknown')}")
            self.logger.info(f"  Status: {metadata.get('status', 'unknown')}")
            
            # For Bronze tier: Just update stats and dashboard
            self.stats['items_processed'] += 1
            
            # TODO: Silver/Gold - Call Qwen Code here
            # Example:
            # plan = self._invoke_qwen(action_file)
            # if plan:
            #     self._create_plan(action_file, plan)
            
        except Exception as e:
            self.logger.error(f"Error processing {action_file.name}: {e}")
    
    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown content."""
        metadata = {}
        lines = content.split('\n')
        
        if not lines[0].strip() == '---':
            return metadata
        
        for line in lines[1:]:
            if line.strip() == '---':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def process_approved(self):
        """
        Process items in the Approved folder.
        
        Execute the approved actions via MCP servers.
        """
        try:
            approved_files = list(self.approved.glob('*.md'))
            
            if not approved_files:
                return
            
            self.logger.info(f"Found {len(approved_files)} approved action(s)")
            
            for approved_file in approved_files:
                self._execute_approved_action(approved_file)
                
        except Exception as e:
            self.logger.error(f"Error processing approved actions: {e}")
    
    def _execute_approved_action(self, approved_file: Path):
        """Execute a single approved action."""
        try:
            content = approved_file.read_text(encoding='utf-8')
            metadata = self._parse_frontmatter(content)
            
            action_type = metadata.get('action', 'unknown')
            self.logger.info(f"Executing approved action: {action_type}")
            
            # TODO: Silver/Gold - Execute via MCP server
            # For now, just log and move to Done
            
            # Move to Done folder
            dest = self.done / approved_file.name
            approved_file.rename(dest)
            
            self.stats['approvals_completed'] += 1
            self.logger.info(f"Action completed: {dest.name}")
            
        except Exception as e:
            self.logger.error(f"Error executing {approved_file.name}: {e}")
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        try:
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            pending_approval_count = len(list(self.pending_approval.glob('*.md')))
            approved_count = len(list(self.approved.glob('*.md')))
            done_today = self._count_done_today()
            
            # Calculate uptime
            uptime = ""
            if self.stats['start_time']:
                delta = datetime.now() - self.stats['start_time']
                uptime = str(delta).split('.')[0]  # Remove microseconds
            
            content = f"""---
last_updated: {datetime.now().isoformat()}
status: active
---

# 🎯 AI Employee Dashboard

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

---

## 📊 Quick Status

| Metric | Value | Status |
|--------|-------|--------|
| **Pending Actions** | {needs_action_count} | {"⚠️ Action needed" if needs_action_count > 0 else "✅ Clear"} |
| **Pending Approvals** | {pending_approval_count} | {"⚠️ Review needed" if pending_approval_count > 0 else "✅ Clear"} |
| **Approved (Ready)** | {approved_count} | {"⏳ Processing" if approved_count > 0 else "✅ Clear"} |
| **Completed Today** | {done_today} | - |

---

## 📥 Inbox Status

- **Unprocessed Items:** {needs_action_count}
- **Last Check:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## ⏳ Needs Action

{self._list_folder_items(self.needs_action) or "_No items requiring attention_"}

---

## 🕒 Pending Approval

{self._list_folder_items(self.pending_approval) or "_No items awaiting your approval_"}

---

## ✅ Recent Activity

| Timestamp | Action | Status |
|-----------|--------|--------|
| {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Orchestrator running | Active |
| - | Items processed | {self.stats['items_processed']} |

---

## 📈 Session Statistics

| Metric | Value |
|--------|-------|
| **Uptime** | {uptime or "N/A"} |
| **Items Processed** | {self.stats['items_processed']} |
| **Actions Created** | {self.stats['actions_created']} |
| **Approvals Completed** | {self.stats['approvals_completed']} |

---

## 🤖 System Status

| Component | Status | Last Heartbeat |
|-----------|--------|----------------|
| Orchestrator | ✅ Running | {datetime.now().strftime("%H:%M:%S")} |
| Watchers | {"✅ Running" if self.watchers else "⏸️ Not started"} | - |

---

## 📝 Quick Links

- [[Company_Handbook]] - Rules of Engagement
- [[Business_Goals]] - Objectives and Targets
- [/Needs_Action](file://./Needs_Action) - Items requiring processing
- [/Pending_Approval](file://./Pending_Approval) - Awaiting your decision
- [/Done](file://./Done) - Completed tasks archive

---

*Auto-updated by Orchestrator v0.1 (Bronze Tier)*
"""
            
            self.dashboard.write_text(content, encoding='utf-8')
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
    
    def _list_folder_items(self, folder: Path, limit: int = 5) -> str:
        """Generate markdown list of recent items in a folder."""
        try:
            items = sorted(folder.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
            if not items:
                return ""
            
            lines = []
            for item in items:
                mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%m-%d %H:%M")
                lines.append(f"- [{mtime}] `{item.name}`")
            
            return "\n".join(lines)
        except Exception:
            return ""
    
    def _count_done_today(self) -> int:
        """Count items moved to Done today."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            count = 0
            for item in self.done.glob('*.md'):
                mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d")
                if mtime == today:
                    count += 1
            return count
        except Exception:
            return 0
    
    def log_event(self, event_type: str, details: dict):
        """Log an event to the logs folder."""
        try:
            log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "actor": "orchestrator",
                "details": details
            }
            
            # Append to daily log
            if log_file.exists():
                import json
                logs = json.loads(log_file.read_text())
                logs.append(log_entry)
                log_file.write_text(json.dumps(logs, indent=2))
            else:
                import json
                log_file.write_text(json.dumps([log_entry], indent=2))
                
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
    
    def run(self):
        """Main run loop for the orchestrator."""
        self._running = True
        self.stats['start_time'] = datetime.now()
        
        self.logger.info("=" * 60)
        self.logger.info("AI Employee Orchestrator v0.1 (Bronze Tier)")
        self.logger.info("=" * 60)
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Process interval: {self.process_interval}s")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("=" * 60)
        
        # Start watchers
        self._initialize_watchers()
        self.start_watchers()
        
        # Main loop
        last_dashboard_update = 0
        dashboard_update_interval = 30  # Update dashboard every 30 seconds
        
        try:
            while self._running:
                # Process action items
                self.process_needs_action()
                
                # Process approved actions
                self.process_approved()
                
                # Update dashboard periodically
                now = time.time()
                if now - last_dashboard_update > dashboard_update_interval:
                    self.update_dashboard()
                    last_dashboard_update = now
                
                time.sleep(self.process_interval)
                
        except KeyboardInterrupt:
            self.logger.info("\nReceived shutdown signal")
        finally:
            self.shutdown()
    
    def _initialize_watchers(self):
        """Initialize and register all configured watchers."""
        for config in self.watcher_configs:
            if not config.enabled:
                continue
            
            try:
                if config.class_name == "FileDropWatcher":
                    watcher = FileDropWatcher(
                        str(self.vault_path),
                        check_interval=config.check_interval
                    )
                    self.register_watcher(watcher)
                # Add more watcher types here as implemented
            except Exception as e:
                self.logger.error(f"Failed to initialize {config.name}: {e}")
    
    def shutdown(self):
        """Graceful shutdown of all components."""
        self.logger.info("Shutting down...")
        self._running = False
        
        # Stop watchers
        self.stop_watchers()
        
        # Final dashboard update
        self.update_dashboard()
        
        # Log shutdown
        self.log_event("shutdown", {
            "uptime": str(datetime.now() - self.stats['start_time']),
            "items_processed": self.stats['items_processed'],
            "approvals_completed": self.stats['approvals_completed']
        })
        
        self.logger.info("Shutdown complete")


def main():
    """Entry point for the orchestrator."""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else ".qwen"
    
    # Validate vault path
    vault = Path(vault_path).resolve()
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    # Check for required files
    dashboard = vault / "Dashboard.md"
    handbook = vault / "Company_Handbook.md"
    
    if not dashboard.exists():
        print(f"Warning: Dashboard.md not found in {vault}")
    if not handbook.exists():
        print(f"Warning: Company_Handbook.md not found in {vault}")
    
    # Create and run orchestrator
    orchestrator = Orchestrator(vault_path)
    orchestrator.run()


if __name__ == "__main__":
    main()
