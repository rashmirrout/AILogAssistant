"""
Simple script to start the Streamlit frontend.
This should be run with Python 3.13 (or another version with streamlit installed).
"""

import sys
import subprocess

def main():
    """Start the Streamlit frontend."""
    
    print("Starting AILog Assistant Frontend...")
    print("Make sure the backend is running on http://localhost:8000")
    print()
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable,
            "-m", "streamlit",
            "run",
            "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\nFrontend stopped.")
    except FileNotFoundError:
        print("ERROR: Streamlit not found!")
        print()
        print("Please install streamlit first:")
        print(f"  {sys.executable} -m pip install streamlit \"altair<5\" \"protobuf<5\"")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
