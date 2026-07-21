# Create virtual environment
python -m venv .venv

# Activate virtual environment (Git Bash)
source .venv/Scripts/activate

# Install requirements from file
pip install -r requirements.txt

# Save currently installed packages to requirements (optional)
pip freeze > requirements.txt

# Deactivate
deactivate



Note for VS Code: When you open VS Code after creating .venv, it will usually ask if you want to select it as the workspace interpreter. Select Yes, or open the Command Palette (Ctrl+Shift+P) $\rightarrow$ Python: Select Interpreter and pick the .venv path.