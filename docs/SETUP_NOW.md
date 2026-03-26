# 🚀 QUICK SETUP - Read This First!

## Your Situation

- ✅ You're on Arch Linux
- ✅ You have Python 3.14.2 installed
- ❌ You don't have `python-pip` installed (that's why pip doesn't work)
- ❌ Your venv doesn't have pip
- 🎯 You want Python 3.12.4

## Two Options for You

### Option 1: Quick Fix (Use Python 3.14.2) ⚡ FASTEST

This will work perfectly! The app supports Python 3.8+, so 3.14.2 is fine.

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"
./quick_fix.sh
```

**What it does:**
1. Installs `python-pip` system package (asks for sudo password)
2. Creates fresh virtual environment
3. Installs all dependencies
4. Sets up database
5. Ready to run!

**Time: ~2-3 minutes**

### Option 2: Install Python 3.12.4 🎯 YOUR PREFERENCE

If you specifically need Python 3.12.4:

#### Step 1: Install Python 3.12

```bash
# Using yay (AUR helper)
yay -S python312

# Or using paru
paru -S python312
```

#### Step 2: Run setup script

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"
./setup_python312.sh
```

**Time: ~5-10 minutes** (depending on AUR build time)

## What's the Problem?

Your venv was created but doesn't have pip because:
1. System doesn't have `python-pip` package installed
2. When you create venv without pip, it can't install packages

## The Fix

Install `python-pip` system package:

```bash
sudo pacman -S python-pip
```

Then recreate your venv.

## Step-by-Step Manual Fix (If Scripts Don't Work)

```bash
# 1. Install python-pip
sudo pacman -S python-pip

# 2. Go to project
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation"

# 3. Remove old venv
rm -rf venv

# 4. Create new venv
python3 -m venv venv

# 5. Activate venv
source venv/bin/activate

# 6. Upgrade pip
python -m pip install --upgrade pip

# 7. Install dependencies
cd backend
pip install -r requirements.txt

# 8. Setup database
rm -f campus.db
python -m utils.seed_data

# 9. Start server
python -m uvicorn main:app --reload
```

## After Setup

### Start the Server

```bash
cd "/run/media/NoName/DATA/Projects/New folder/Campus_Data_Automation/backend"
source ../venv/bin/activate
python -m uvicorn main:app --reload
```

### Open Browser

http://127.0.0.1:8000

### Login

- **Student**: `student@campus.edu` / `student123`
- **Admin**: `admin@campus.edu` / `admin123`

## Recommended: Use Quick Fix

Unless you absolutely need Python 3.12.4, just run:

```bash
./quick_fix.sh
```

It will:
- ✅ Install python-pip
- ✅ Create proper venv
- ✅ Install all dependencies
- ✅ Setup database
- ✅ Get you running in 2-3 minutes

## Need Python 3.12.4?

See **PYTHON_SETUP_ARCH.md** for detailed instructions on installing Python 3.12.4 via AUR or pyenv.

---

**TL;DR:** Run `./quick_fix.sh` and you'll be up and running! 🚀
