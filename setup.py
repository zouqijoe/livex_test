#!/usr/bin/env python3
"""
Setup script for the Cal.com Chatbot
This script helps you configure the environment variables needed to run the chatbot.
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    print("🚀 Setting up Cal.com Chatbot")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get user input
    print("\n📝 Please provide the following information:")
    
    # OpenAI API Key (already provided in the challenge)
    openai_key = "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"
    
    # Cal.com API Key
    cal_api_key = input("🔑 Cal.com API Key (cal_live_...): ").strip()
    if not cal_api_key:
        print("❌ Cal.com API Key is required!")
        return
    
    # Cal.com Username
    cal_username = input("👤 Cal.com Username: ").strip()
    if not cal_username:
        print("❌ Cal.com Username is required!")
        return
    
    # Create .env file
    env_content = f"""# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# Cal.com Configuration
CAL_API_KEY={cal_api_key}
CAL_USERNAME={cal_username}

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python app.py")
        print("3. Open your browser to: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 