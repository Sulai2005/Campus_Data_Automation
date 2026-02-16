# Python 3.12.4 Setup Guide for Arch Linux

## Current Situation

You have:
- ✅ Python 3.14.2 installed (system default)
- ❌ Python 3.12.4 not installed
- ❌ pip not working in venv

## Solution Options

### Option 1: Install Python 3.12 from AUR (Recommended)

This will install Python 3.12 alongside your existing Python 3.14.2.

```bash
# If you have yay (AUR helper):
yay -S python312

# Or if you have paru:
paru -S python312

# Or install manually from AUR:
git clone https://aur.archlinux.org/python312.git
cd python312
makepkg -si
```

After installation, you'll have `python3.12` command available.

### Option 2: Use pyenv (Version Manager)

Install pyenv to manage multiple Python versions:

```bash
# Install pyenv
yay -S pyenv

# Or manually:
curl https://pyenv.run | bash

# Add to ~/.bashrc or ~/.zshrc:
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc

# Install Python 3.12.4
pyenv install 3.12.4

# Set it for this project
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"
pyenv local 3.12.4
```

### Option 3: Use Current Python 3.14.2

The application will work with Python 3.14.2. Just need to fix the venv setup.

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"

# Remove old venv
rm -rf venv

# Create new venv with python3
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
python -m ensurepip --upgrade
python -m pip install --upgrade pip

# Install dependencies
cd backend
pip install -r requirements.txt

# Setup database
python -m utils.seed_data

# Run server
python -m uvicorn main:app --reload
```

## Quick Setup (Automated)

I've created a setup script that will handle everything:

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"

# Run the setup script
./setup_python312.sh
```

The script will:
1. Check for Python 3.12 (or use 3.14.2)
2. Create fresh virtual environment
3. Install pip properly
4. Install all dependencies
5. Setup database
6. Show you how to start the server

## Manual Setup (Step by Step)

If you want to do it manually:

### Step 1: Install Python 3.12 (choose one option above)

### Step 2: Create Virtual Environment

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"

# Remove old venv
rm -rf venv

# Create new venv with Python 3.12
python3.12 -m venv venv

# Or with current Python 3.14.2
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 4: Ensure pip is Available

```bash
# Upgrade pip
python -m ensurepip --upgrade
python -m pip install --upgrade pip

# Verify pip works
pip --version
```

### Step 5: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 6: Setup Database

```bash
# Remove old database
rm -f campus.db

# Create and seed new database
python -m utils.seed_data
```

### Step 7: Start Server

```bash
python -m uvicorn main:app --reload
```

### Step 8: Test

Open browser: http://127.0.0.1:8000
Login: student@campus.edu / student123

## Troubleshooting

### Issue: "pip: command not found" in venv

**Solution:**
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Issue: "No module named 'ensurepip'"

**Solution:**
```bash
# Install python-pip package
sudo pacman -S python-pip

# Then recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Issue: venv activation doesn't work

**Solution:**
```bash
# Make sure you're using bash or zsh
echo $SHELL

# Activate with full path
source /run/media/NoName/DATA/Projects/New\ folder/Campus_Data_Automation/venv/bin/activate

# Or use this format
. venv/bin/activate
```

### Issue: "ModuleNotFoundError" after installing

**Solution:**
```bash
# Make sure venv is activated
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install -r backend/requirements.txt
```

## Recommended Approach

**For Python 3.12.4 specifically:**
1. Install from AUR: `yay -S python312`
2. Run setup script: `./setup_python312.sh`

**For quick start with Python 3.14.2:**
1. Run setup script: `./setup_python312.sh`
2. Accept using Python 3.14.2 when prompted

## Why Python 3.12.4?

The application works with Python 3.8+, including 3.14.2. If you specifically need 3.12.4:
- For compatibility with specific libraries
- For production environment matching
- For testing purposes

Otherwise, Python 3.14.2 will work perfectly fine!

## Next Steps

After setup is complete:

```bash
# Start the server
cd backend
python -m uvicorn main:app --reload

# In another terminal, you can run tests
pytest tests/ -v
```

## Quick Commands Reference

```bash
# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Install package
pip install package_name

# Reinstall all dependencies
pip install -r backend/requirements.txt --force-reinstall
```

---

**Ready to start?** Run: `./setup_python312.sh`
