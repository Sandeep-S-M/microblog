# microblog (corey_scafer_Flask)

Quick setup and test instructions for Windows (cmd.exe)

Prerequisites
- Python 3.8+ (we used 3.13) installed and available as `python` or the `py` launcher.

Create and activate the virtual environment (from project root):

```bat
python -m venv venv
venv\Scripts\activate
```

Install pinned dependencies:

```bat
pip install -r requirements.txt
```

Run the unit tests:

```bat
venv\Scripts\python -m unittest tests.py -v
```

Notes
- On Windows prefer `python` or `py -3` instead of `python3`.
- If you see the Microsoft Store "Python was not found" message, either install Python from python.org and check "Add Python to PATH" or disable the store App Execution Aliases for `python.exe` / `python3.exe`.
- The `venv` folder is created in the project root. To deactivate the venv use `deactivate`.
