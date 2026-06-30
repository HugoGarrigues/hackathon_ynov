# TechCorp Chat - Deployment

This path follows the PDF brief: production-ready chat access to Phi-3.5-Financial through a web interface.

## 1. Start Ollama

Install Ollama from https://ollama.com/download, then start the local service.

On Windows, the official PowerShell install command is:

```powershell
irm https://ollama.com/install.ps1 | iex
```

If `ollama` is not found in the current terminal after installation, open a new PowerShell window or call the executable directly:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

Check the API:

```powershell
python scripts/check_ollama.py --url http://localhost:11434
```

If the script says Ollama is unreachable, open Ollama or run:

```powershell
ollama serve
```

## 2. Create the TechCorp model

The provided Modelfile wraps a Phi 3.5 base model with the TechCorp financial assistant system prompt.

```powershell
ollama pull phi3.5
ollama create techcorp-phi3-financial -f ollama_server/Modelfile
python scripts/check_ollama.py --model techcorp-phi3-financial
```

If `phi3.5` is not available on the machine, use a lightweight fallback for the demo:

```powershell
ollama pull qwen2.5:3b
```

Then select `qwen2.5:3b` in the app sidebar.

## 3. Run the web interface

Create a virtual environment and install the app dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r app/requirements.txt
```

Launch:

```powershell
python -m streamlit run app/streamlit_app.py
```

Open the local URL shown by Streamlit, usually http://localhost:8501.

## Runtime configuration

The app reads these optional environment variables:

```powershell
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_MODEL="techcorp-phi3-financial"
python -m streamlit run app/streamlit_app.py
```

## Demo checklist

- Ollama responds on `http://localhost:11434/api/tags`.
- A Phi-compatible model is available.
- The app status is `Connecte`.
- A finance question returns a streamed answer.
- The known compromised trigger is blocked by the interface.
