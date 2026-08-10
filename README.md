# Mahoraga — local web app

Mahoraga is a locally run adaptive chess opponent. The browser UI, API, SQLite database, and Stockfish process all run on your PC.

## Windows setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/windows/ and select **Add Python to PATH**.
2. Download the Windows Stockfish executable from https://stockfishchess.org/download/ and extract it. If you leave it in `Downloads` (e.g. `Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe`) Mahoraga finds it automatically; otherwise set `STOCKFISH_PATH` to its full path.
3. In PowerShell:

```powershell
cd <repo>\backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` once, then activate again.

Open http://127.0.0.1:8000 in a browser. You play White. Click a white piece, then click its destination square. Use the New game button to reset the board.

## Tests and validation

With the virtual environment active:

```powershell
pytest
py -m tests.offline_harness.run_validation
```

The validation command checks whether the Phase 1 loss signatures cluster the labeled tactical fixtures as designed. The app creates `backend\mahoraga.db` automatically on first start; delete only that file if you intentionally want to reset local player history.
