#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher implementations.

All watchers follow this structure:
1. Check for new items (emails, messages, files, etc.)
2. Create action files in the Needs_Action folder
3. Run continuously with configurable check interval
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        # Control flag for graceful shutdown
        self._running = False
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items (format depends on implementation)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file for an item.
        
        Args:
            item: Item to process (format depends on implementation)
            
        Returns:
            Path to the created action file
        """
        pass
    
    def process_item(self, item) -> Optional[Path]:
        """
        Process a single item and create an action file.
        
        Args:
            item: Item to process
            
        Returns:
            Path to created file, or None if skipped
        """
        try:
            filepath = self.create_action_file(item)
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and processes them.
        
        Call stop() to gracefully shut down.
        """
        self._running = True
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Watching: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        
        while self._running:
            try:
                items = self.check_for_updates()
                if items:
                    self.logger.info(f"Found {len(items)} new item(s)")
                    for item in items:
                        self.process_item(item)
                else:
                    self.logger.debug("No new items")
            except Exception as e:
                self.logger.error(f"Error checking for updates: {e}")
            
            # Sleep in small increments to allow responsive shutdown
            for _ in range(self.check_interval):
                if not self._running:
                    break
                time.sleep(1)
        
        self.logger.info(f"{self.__class__.__name__} stopped")
    
    def stop(self):
        """Signal the watcher to stop gracefully."""
        self._running = False
    
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running


class FileDropWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    
    When a file is dropped into the Inbox folder, it creates
    an action file in Needs_Action with metadata.
    
    This is the simplest watcher for Bronze tier - just drag
    and drop files into the Inbox folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 5):
        """
        Initialize the file drop watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 5 for responsive file drops)
        """
        super().__init__(vault_path, check_interval)
        self.inbox = self.vault_path / 'Inbox'
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by name + size + mtime
        self.processed_files: dict = {}
    
    def check_for_updates(self) -> list:
        """
        Check for new files in the Inbox folder.
        
        Returns:
            List of tuples: (file_path, stat_info)
        """
        new_files = []
        
        try:
            for file_path in self.inbox.iterdir():
                if file_path.is_file() and not file_path.name.endswith('.md'):
                    stat = file_path.stat()
                    file_key = f"{file_path.name}:{stat.st_size}:{stat.st_mtime}"
                    
                    if file_key not in self.processed_files:
                        self.processed_files[file_key] = True
                        new_files.append((file_path, stat))
        except Exception as e:
            self.logger.error(f"Error scanning inbox: {e}")
        
        return new_files
    
    def create_action_file(self, item) -> Path:
        """
        Create an action file for a dropped file.
        
        Args:
            item: Tuple of (file_path, stat_info)
            
        Returns:
            Path to the created action file
        """
        file_path, stat = item
        
        # Create unique action file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = file_path.name.replace(' ', '_').replace('.', '_')
        action_filename = f"FILE_DROP_{safe_name}_{timestamp}.md"
        action_path = self.needs_action / action_filename
        
        # Create action file content
        content = f"""---
type: file_drop
original_name: {file_path.name}
size: {stat.st_size}
created: {datetime.now().isoformat()}
status: pending
priority: normal
---

# File Drop for Processing

A new file has been dropped into the Inbox for processing.

## File Details

- **Original Name:** {file_path.name}
- **Size:** {self._format_size(stat.st_size)}
- **Location:** `{file_path}`
- **Dropped At:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Suggested Actions

- [ ] Review file contents
- [ ] Determine required action
- [ ] Process and move to Done
- [ ] Archive if no action needed

## Notes

_Add your analysis and action plan here_

---
*Created by FileSystemWatcher*
"""
        
        action_path.write_text(content, encoding='utf-8')
        return action_path
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    import sys
    
    # Default to current directory if no vault path provided
    vault = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Starting File Drop Watcher...")
    print(f"Vault: {Path(vault).resolve()}")
    print(f"Drop files into: {Path(vault).resolve() / 'Inbox'}")
    print("Press Ctrl+C to stop\n")
    
    watcher = FileDropWatcher(vault)
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        watcher.stop()
