# Learning Notes

After each step, write 3-5 lines IN MY OWN WORDS: what I did, why, and what I learned.
This is my interview prep sheet.

## Setup

**Tools I installed and why**
- Python 3.14: the language the project is written in. Installed through the Python install manager.
- VS Code: where I write, run and view code. Added the Python, Jupyter and Claude Code extensions.
- Git: tracks every version of my project so I can go back if something breaks,
  and uploads my code to GitHub where recruiters can see it.
- Claude Code: an AI coding assistant that works inside my project folder. It writes and
  runs code when I ask, but asks my permission first. I make the decisions and check its work.

**Virtual environment (.venv)**
- A private set of Python libraries just for this project, so different projects
  don't clash over library versions.
- Created with `python -m venv .venv`, activated with `.venv\Scripts\activate`.
- `(.venv)` at the start of the terminal line means it's active. Always check for it.

**Libraries and requirements.txt**
- Installed pandas (tables), numpy (math), yfinance (financial data), openpyxl (Excel),
  matplotlib (charts), jupyter (notebooks), pytest (testing calculations).
- `pip freeze > requirements.txt` records exact versions, so anyone can recreate my setup
  with `pip install -r requirements.txt`. This makes the project reproducible.

**Project structure**
- Separate folders for raw data, processed data, code (src), notebooks, tests, outputs
  and reports. Raw data is never edited, so I can always trace results back to the source.

**.gitignore**
- Tells Git what NOT to upload: .venv (large and recreatable), data/raw (downloaded data
  I don't own; my script can re-download it), and temporary Python/Jupyter files.

**CLAUDE.md**
- A briefing file Claude Code reads at the start of every session: project goal, my rules
  (explain everything, never invent data, ask before design decisions).

**Problems I hit and how I fixed them**
- `>>` in PowerShell: the command was incomplete (a pasted hidden character). Fixed by
  cancelling with Ctrl+C and typing the command manually.
- `git` not recognized: Git wasn't installed. Installed it with winget.
- "Running scripts is disabled": Windows blocks scripts by default. Fixed with
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, which allows local scripts.
- requirements.txt saved as UTF-16: PowerShell's default encoding. Re-saved as UTF-8 in VS Code
  so GitHub displays it properly.