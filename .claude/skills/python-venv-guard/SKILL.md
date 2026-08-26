---
name: python-venv-guard
description: MANDATORY — use before running ANY Python command (pip, pytest, python, mypy, ruff, etc.) in any project with a .venv directory. Trigger on "run tests," "install package," "pip install," "pytest," "mypy," "ruff," or any Python execution — even if the user doesn't mention venvs. Ensures all Python work runs inside the correct virtual environment, never at the system level.
---

# Python Venv Guard

Every Python project has its own `.venv`. All Python commands MUST run inside the project's venv — NEVER at the system Python level.

## Pre-flight check (MANDATORY before ANY Python command)

Before running ANY Python command, run this check:

```bash
# Detect venv
VENV_PYTHON=""
if [ -f ".venv/bin/python" ]; then
  VENV_PYTHON=".venv/bin/python"
elif [ -f "backend/.venv/bin/python" ]; then
  VENV_PYTHON="backend/.venv/bin/python"
elif [ -f "apps/backend/.venv/bin/python" ]; then
  VENV_PYTHON="apps/backend/.venv/bin/python"
fi

if [ -z "$VENV_PYTHON" ]; then
  echo "ERROR: No .venv found. Create one first: python3 -m venv .venv"
  exit 1
fi

# Verify venv is active
CURRENT_PYTHON=$(which python3 2>/dev/null)
if [[ "$CURRENT_PYTHON" != *".venv"* ]]; then
  echo "WARNING: venv not active. Current python: $CURRENT_PYTHON"
  echo "Activating venv..."
  source "$(dirname "$VENV_PYTHON")/activate"
fi
```

## Hard rules (NEVER violate)

1. **Never run `pip install` at the system level** — always use `.venv/bin/pip install` or activate first
2. **Never run `pytest`, `mypy`, `ruff` at the system level** — always use venv binaries
3. **Never run bare `python` or `python3`** when a `.venv` exists — use `.venv/bin/python`
4. **System Python is OFF-LIMITS** — it's for system tools only, not project work
5. **When creating a new Python project**, always create a venv first:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Verification (run after ANY Python command)

```bash
# Verify the command used the venv
which python3  # Must show .venv/bin/python3
which pip3     # Must show .venv/bin/pip3
```

If `which python3` or `which pip3` does NOT show `.venv/bin/`, STOP and fix immediately.

## Project venv locations

| Project | Venv path | Python version |
|---|---|---|
| synca_conf_back | `.venv/` | 3.12 |
| Eureka-Group/apps/backend | `apps/backend/.venv/` | 3.12 |
| jenby/backend | `backend/.venv/` | 3.12 |

## Detecting the venv

If unsure which venv to use:

```bash
find . -name "pyvenv.cfg" -path "*/.venv/*" 2>/dev/null
```

## Quick activation reference

```bash
# synca_conf_back:
source .venv/bin/activate

# Eureka-Group backend:
source apps/backend/.venv/bin/activate

# jenby backend:
source backend/.venv/bin/activate
```

Or use venv binaries directly (no activation needed):

```bash
.venv/bin/pip install <package>
.venv/bin/pytest
.venv/bin/mypy .
.venv/bin/ruff check .
```
