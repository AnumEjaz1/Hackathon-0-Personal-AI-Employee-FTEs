#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bronze Tier Verification Script

Run this to verify all Bronze Tier deliverables are complete.
"""

import sys
from pathlib import Path


def check(condition, message):
    """Print check result and return status."""
    if condition:
        print(f"  ✅ {message}")
        return True
    else:
        print(f"  ❌ {message}")
        return False


def main():
    print("=" * 60)
    print("AI Employee - Bronze Tier Verification")
    print("=" * 60)
    
    vault_path = Path("AI_Employee_Vault").resolve()
    src_path = Path("src").resolve()
    root_path = vault_path.parent
    
    all_passed = True
    
    # Check 1: Vault folder structure
    print("\n📁 Vault Folder Structure:")
    required_folders = [
        "Inbox", "Needs_Action", "Done", "Plans",
        "Pending_Approval", "Approved", "Rejected", "Logs"
    ]
    for folder in required_folders:
        all_passed &= check(
            (vault_path / folder).exists(),
            f"{folder}/ folder exists"
        )
    
    # Check 2: Required markdown files
    print("\n📄 Required Markdown Files:")
    required_files = {
        "Dashboard.md": "Real-time status dashboard",
        "Company_Handbook.md": "Rules of engagement",
        "Business_Goals.md": "Objectives and metrics"
    }
    for filename, description in required_files.items():
        filepath = vault_path / filename
        all_passed &= check(
            filepath.exists() and filepath.stat().st_size > 0,
            f"{filename} ({description})"
        )
    
    # Check 3: Python source files
    print("\n🐍 Python Source Files:")
    source_files = {
        "base_watcher.py": "Base watcher class with FileDropWatcher",
        "orchestrator.py": "Main orchestration process"
    }
    for filename, description in source_files.items():
        filepath = src_path / filename
        all_passed &= check(
            filepath.exists() and filepath.stat().st_size > 0,
            f"{filename} ({description})"
        )
    
    # Check 4: Configuration files
    print("\n⚙️ Configuration Files:")
    all_passed &= check(
        (root_path / "requirements.txt").exists(),
        "requirements.txt exists"
    )
    all_passed &= check(
        (root_path / "README.md").exists(),
        "README.md with setup instructions"
    )
    
    # Check 5: Python syntax validation
    print("\n🔍 Syntax Validation:")
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "py_compile",
         str(src_path / "base_watcher.py"),
         str(src_path / "orchestrator.py")],
        capture_output=True,
        text=True
    )
    all_passed &= check(
        result.returncode == 0,
        "Python syntax valid (no compilation errors)"
    )
    
    # Check 6: Import test
    print("\n📦 Import Test:")
    try:
        sys.path.insert(0, str(src_path))
        from base_watcher import BaseWatcher, FileDropWatcher
        from orchestrator import Orchestrator
        all_passed &= check(True, "All modules import successfully")
    except ImportError as e:
        all_passed &= check(False, f"Import failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Bronze Tier Complete!")
        print("\nNext steps:")
        print("  1. Open AI_Employee_Vault in Obsidian")
        print("  2. Run: python src/orchestrator.py AI_Employee_Vault")
        print("  3. Drop a file into AI_Employee_Vault/Inbox/")
        print("  4. Watch the Dashboard update in real-time")
    else:
        print("⚠️ SOME CHECKS FAILED - Review errors above")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
