#!/usr/bin/env python3
"""
Startup script for Typhoon Summarizer API service
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from apis.typhoon_summarizer_api import app

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("TYPHOON_API_PORT", 8000))
    host = os.environ.get("TYPHOON_API_HOST", "0.0.0.0")
    
    print(f"Starting Typhoon Summarizer API on {host}:{port}")
    print("Model will be loaded on first request...")
    
    # Run the FastAPI app
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
