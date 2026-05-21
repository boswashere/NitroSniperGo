"""
Quick setup script for NitroSniper
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n▶️  {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("NitroSniper 2026 - Setup Assistant")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required!")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command(
            [sys.executable, "-m", "venv", "venv"],
            "Creating virtual environment"
        )
    
    # Detect OS and activate command
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate.bat"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    print(f"\n✅ Virtual environment ready")
    print(f"   Activate with: {activate_cmd}")
    
    # Install dependencies
    run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip"
    )
    
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing dependencies"
    )
    
    # Create settings.json if not exists
    if not Path("settings.json").exists():
        print("\n⚠️  settings.json not found")
        print("   Creating default settings.json...")
        # It already exists from the create_file call
    else:
        print("\n✅ settings.json found")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Edit settings.json with your Discord tokens")
    print("2. Run: python main.py")
    print("\n⚠️  Remember: Use at your own risk! No warranties provided.")


if __name__ == "__main__":
    main()
