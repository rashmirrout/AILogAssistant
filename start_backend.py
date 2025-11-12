"""
Simple script to start the backend server.
Run with: python start_backend.py
"""
import sys
import subprocess

def main():
    """Start the backend server."""
    try:
        # Check if running in virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("WARNING: Not running in a virtual environment!")
            print("It's recommended to create and activate a virtual environment first:")
            print("  python -m venv .venv")
            print("  .venv\\Scripts\\activate  (Windows)")
            print("  source .venv/bin/activate  (Linux/Mac)")
            print("  pip install -e .")
            print()
        
        # Import and run the backend
        from backend.main import main as backend_main
        backend_main()
        
    except ImportError as e:
        print(f"ERROR: Failed to import backend: {e}")
        print("\nPlease install dependencies first:")
        print("  pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
