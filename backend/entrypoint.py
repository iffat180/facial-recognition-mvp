#!/usr/bin/env python3
"""
Entrypoint script for Railway deployment
Reads PORT from environment and starts uvicorn
"""
import os
import sys

def main():
    port = os.environ.get('PORT', '8000')
    print(f"Starting uvicorn on port {port}...")
    
    # Import and run uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(port),
        log_level="info"
    )

if __name__ == "__main__":
    main()
