# Frontend Installation Guide

The frontend requires `streamlit` which depends on `pyarrow`. Unfortunately, **pyarrow does not have prebuilt wheels for Python 3.14** and requires cmake to build from source.

## Option 1: Use Python 3.12 or 3.13 (Recommended)

The easiest solution is to use a compatible Python version for the frontend:

```bash
# Install Python 3.13 from python.org
# Then create a separate virtual environment for the frontend

# Create frontend-only virtual environment with Python 3.13
py -3.13 -m venv .venv-frontend
.venv-frontend\Scripts\activate

# Install frontend dependencies
pip install streamlit "altair<5" "protobuf<5"

# Run frontend (make sure backend is running on port 8000)
python -m frontend.app
```

## Option 2: Use Python 3.14 with Conda (Alternative)

Conda provides prebuilt pyarrow packages:

```bash
# Install Miniconda/Anaconda first
# Then create environment

conda create -n ailog-frontend python=3.14
conda activate ailog-frontend
conda install -c conda-forge pyarrow streamlit altair<5 protobuf<5

# Run frontend
python -m frontend.app
```

## Option 3: Install Build Tools for Python 3.14 (Advanced)

If you must use Python 3.14 with pip:

1. Install Visual Studio 2022 Build Tools
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"
   - Include CMake components

2. Install CMake
   - Download from: https://cmake.org/download/
   - Add to PATH during installation

3. Then retry:
```bash
pip install --user streamlit "altair<5" "protobuf<5"
```

## Current Status

✅ **Backend is working** - You can use the backend API independently with Python 3.14
- Backend runs on: http://localhost:8000
- API documentation: http://localhost:8000/docs
- No frontend dependencies needed

❌ **Frontend requires compatible Python version** - streamlit/pyarrow compatibility issue with Python 3.14

## Using the Backend Without Frontend

The backend provides a complete REST API. You can:

1. **Use curl or Postman** to interact with the API
2. **Build a custom UI** in any language/framework
3. **Use Python scripts** to call the API directly

Example using Python:
```python
import requests

# Create issue
response = requests.post("http://localhost:8000/create_issue", 
                        json={"issue_id": "test-001"})

# Upload logs
with open("app.log", "rb") as f:
    files = {"files": ("app.log", f, "text/plain")}
    requests.post("http://localhost:8000/upload_logs/test-001", files=files)

# Update knowledge base
requests.post("http://localhost:8000/update_kb",
             json={"issue_id": "test-001"})

# Query
response = requests.post("http://localhost:8000/query",
                        json={"issue_id": "test-001", "query": "What errors occurred?"})
print(response.json()["answer"])
```

## Summary

**For immediate use:** Backend works perfectly with Python 3.14
**For frontend:** Either downgrade Python to 3.12/3.13 or use Conda with Python 3.14
