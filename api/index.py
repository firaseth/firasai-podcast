# Vercel Serverless Entrypoint
import sys
import os

# Add root directory to Python path so Vercel can find main.py and other files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
