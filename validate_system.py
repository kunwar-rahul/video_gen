#!/usr/bin/env python3
"""
Complete System Validation - Checks all components
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*60}")
    print(f"Checking: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} (timed out)")
        return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False


def validate_project():
    """Validate the entire project setup"""
    print("\n" + "="*60)
    print("Video Generation System - Complete Validation")
    print("="*60)
    
    checks = []
    
    # 1. Python setup
    checks.append(run_command("python --version", "Python installed"))
    checks.append(run_command("pip --version", "Pip available"))
    
    # 2. Backend dependencies
    checks.append(run_command(
        "python -c \"import flask; import redis; import flask_socketio; print('Backend deps OK')\"",
        "Backend dependencies"
    ))
    
    # 3. Node.js setup
    checks.append(run_command("node --version", "Node.js installed"))
    checks.append(run_command("npm --version", "npm available"))
    
    # 4. Frontend setup
    ui_path = Path("ui/node_modules")
    if ui_path.exists():
        checks.append(True)
        print(f"✅ Frontend dependencies installed")
    else:
        print(f"⚠️  Frontend dependencies not installed (run: cd ui && npm install)")
        checks.append(False)
    
    # 5. Key files check
    required_files = [
        "app/api/main.py",
        "app/websocket/main.py",
        "local_dev.py",
        "run_all_services.py",
        "ui/package.json",
        "ui/src/App.tsx",
        "requirements.txt",
        "SETUP_AND_TESTING.md"
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
            checks.append(True)
        else:
            print(f"❌ {file} missing")
            checks.append(False)
    
    # 6. Environment files
    if Path(".env.local").exists() or Path(".env").exists():
        print(f"✅ Backend environment configured")
        checks.append(True)
    else:
        print(f"⚠️  Backend .env not found (run: cp .env.example .env)")
        checks.append(False)
    
    if Path("ui/.env.local").exists():
        print(f"✅ Frontend environment configured")
        checks.append(True)
    else:
        print(f"⚠️  Frontend .env.local not found (using defaults)")
        checks.append(True)  # Not critical
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n{'='*60}")
    print(f"Validation Summary: {passed}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("✅ All systems ready!")
        print("\nTo start the application:")
        print("  1. Terminal 1: python run_all_services.py")
        print("  2. Terminal 2: cd ui && npm run dev")
        print("  3. Terminal 3: python test_api_comprehensive.py")
        return True
    else:
        print("⚠️  Some checks failed. Review the output above.")
        print("\nFor detailed setup instructions, see: SETUP_AND_TESTING.md")
        return False


if __name__ == "__main__":
    success = validate_project()
    sys.exit(0 if success else 1)
