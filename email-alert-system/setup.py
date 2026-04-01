#!/usr/bin/env python
"""Quick start setup script for Email Alert System"""

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("Email Alert System - Quick Start Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print("✓ Python version OK")
    print()
    
    # Install dependencies
    print("Installing dependencies...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    requirements_file = os.path.join(backend_dir, 'requirements.txt')
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Configure Email Settings:")
    print("   - Copy backend/.env.example to backend/.env")
    print("   - Update SMTP settings with your email credentials")
    print()
    print("2. Start Backend Server:")
    print("   - Run: python backend/run.py")
    print("   - API will be available at http://localhost:8000")
    print()
    print("3. Open Frontend:")
    print("   - Open frontend/index.html in your web browser")
    print("   - Or serve with: python -m http.server 8080")
    print()
    print("4. API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print()

if __name__ == "__main__":
    main()
