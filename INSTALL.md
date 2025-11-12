# Installation Guide - AI Log Analytics Assistant

## Important: Python Version Compatibility

This project currently works best with **Python 3.10, 3.11, or 3.12** due to dependency constraints. Python 3.14 is too new and lacks prebuilt wheels for many dependencies.

## Recommended Installation Method

### Step 1: Check Python Version

```bash
python --version
```

**If you have Python 3.14**, you have two options:
1. Install Python 3.12 alongside (recommended)
2. Use pip with existing environment (see below)

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies

```bash
# Install the package in editable mode
pip install -e .

# For frontend support, also install:
pip install -e ".[frontend]"
```

### Step 4: Configure Environment

```bash
# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_key_here
```

### Step 5: Run the Application

**Terminal 1 - Backend:**
```bash
# Using the startup script
python start_backend.py

# OR using the command directly
ailog-backend
```

**Terminal 2 - Frontend:**
```bash
# Activate venv first if not already
.venv\Scripts\activate

# Run frontend
ailog-frontend
```

## Verification

1. Backend should start at: http://localhost:8000
2. Frontend should open at: http://localhost:8501
3. API docs available at: http://localhost:8000/docs

## Troubleshooting

### "No module named 'fastapi'"

You need to install dependencies:
```bash
pip install -e .
```

### "GEMINI_API_KEY not found"

1. Ensure `.env` file exists in project root
2. Add your API key: `GEMINI_API_KEY=your_actual_key`
3. Get an API key from: https://makersuite.google.com/app/apikey

### UV Installation Fails (Python 3.14)

UV cannot install on Python 3.14 due to missing prebuilt wheels. **Use pip method above instead.**

The error occurs because packages like `pillow`, `torch`, `pyarrow` don't have prebuilt wheels for Python 3.14 yet, and building from source requires:
- Visual Studio C++ Build Tools
- cmake
- zlib headers

**Solution**: Use Python 3.10-3.12 or use pip with your existing Python.

### Port Already in Use

If port 8000 or 8501 is in use:

**Backend (default 8000):**
Edit `backend/main.py` and change the port in the `main()` function.

**Frontend (default 8501):**
Streamlit will automatically try the next available port.

## Alternative: Using Conda/Mamba

If you prefer conda:

```bash
# Create environment with Python 3.12
conda create -n ailogassistant python=3.12
conda activate ailogassistant

# Install dependencies
pip install -e .
pip install -e ".[frontend]"
```

## Quick Test

Once installed, test with:

```bash
# In terminal 1
python start_backend.py

# In terminal 2 (after backend is running)
ailog-frontend
```

You should see:
- Backend: Uvicorn running on http://0.0.0.0:8000
- Frontend: Streamlit app opens in browser

## Next Steps

1. Create an issue workspace in the UI
2. Upload sample log file from `sample_logs/application.log`
3. Build knowledge base
4. Start querying your logs!

## Getting Help

- Check README.md for detailed usage guide
- API documentation: http://localhost:8000/docs
- Sample logs provided in `sample_logs/` directory
