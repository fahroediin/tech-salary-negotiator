#!/usr/bin/env python3
"""
Tech Salary Negotiator Setup Script
Sets up the application with SQLAlchemy and SQLite
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ is required")
        return False
    logger.info(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"✅ Node.js {version} detected")
            return True
    except FileNotFoundError:
        pass

    logger.error("❌ Node.js is required but not installed")
    return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        logger.info("✅ .env file already exists")
        return True

    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        logger.info("✅ Created .env file from .env.example")
        logger.info("⚠️  Please edit .env file with your Gemini API key")
        return True
    else:
        logger.error("❌ .env.example file not found")
        return False

def install_python_deps():
    """Install Python dependencies"""
    logger.info("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True, capture_output=True)
        logger.info("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Python dependencies: {e}")
        return False

def install_node_deps():
    """Install Node.js dependencies"""
    logger.info("📦 Installing Node.js dependencies...")
    try:
        os.chdir('frontend')
        subprocess.run(['npm', 'install'], check=True, capture_output=True)
        os.chdir('..')
        logger.info("✅ Node.js dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ Frontend directory not found")
        return False

def init_database():
    """Initialize database"""
    logger.info("🗄️  Initializing database...")
    try:
        subprocess.run([sys.executable, 'init_db.py'], check=True, capture_output=True)
        logger.info("✅ Database initialized")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up Tech Salary Negotiator...")
    print()

    # Check prerequisites
    checks = [
        ("Python version", check_python_version),
        ("Node.js", check_node_version),
    ]

    for name, check_func in checks:
        if not check_func():
            return False

    # Setup steps
    steps = [
        ("Create .env file", create_env_file),
        ("Install Python dependencies", install_python_deps),
        ("Initialize database", init_database),
        ("Install Node.js dependencies", install_node_deps),
    ]

    for name, step_func in steps:
        logger.info(f"Running: {name}")
        if not step_func():
            logger.error(f"❌ Setup failed at: {name}")
            return False
        print()

    logger.info("✅ Setup complete!")
    print()
    logger.info("🎉 Next steps:")
    logger.info("1. Edit .env file with your Gemini API key")
    logger.info("2. Start backend: python main.py")
    logger.info("3. Start frontend: cd frontend && npm run dev")
    logger.info("4. Open http://localhost:3000 in your browser")
    print()
    logger.info("📚 For more information, see README.md")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)