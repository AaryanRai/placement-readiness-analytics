# GitHub Repository Setup Guide

## Steps to Push Project to GitHub

### 1. Create a New GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Repository name: `placement-readiness-analytics` (or your preferred name)
5. Description: "University Placement Readiness Analytics Dashboard - ML-based system for tracking student job market readiness"
6. Set visibility: **Public** or **Private** (your choice)
7. **DO NOT** initialize with README, .gitignore, or license (we already have these)
8. Click "Create repository"

### 2. Push Existing Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename main branch if needed (GitHub uses 'main' by default)
git branch -M main

# Push all code to GitHub
git push -u origin main
```

### 3. Alternative: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### 4. Verify Push

After pushing, refresh your GitHub repository page. You should see all your project files.

## Important Notes

### Files NOT Pushed to GitHub (via .gitignore):
- `.env` - Contains database credentials (keep private!)
- `models/*.pkl` - Trained ML models (large files)
- `__pycache__/` - Python bytecode
- `.venv/` - Virtual environment
- `.DS_Store` - macOS system files

### Files Pushed to GitHub:
- All source code (`src/`)
- Configuration files (`config/`)
- Data files (`data/`)
- Documentation (`README.md`, `PRD.md`, etc.)
- Scripts (`setup.sh`, `run.sh`)
- `requirements.txt`
- `.gitignore`
- `models/.gitkeep` (preserves models directory structure)

## Next Steps After Pushing

1. **Add Repository Description**: Update the GitHub repo description
2. **Add Topics/Tags**: Add tags like `machine-learning`, `streamlit`, `postgresql`, `education`, `analytics`
3. **Create Releases**: Tag important versions (e.g., `v1.0.0`)
4. **Add License**: Consider adding a LICENSE file
5. **Update README**: Ensure README has clear setup instructions

## Repository Structure Overview

```
placement-readiness-analytics/
├── README.md                 # Project overview
├── PRD.md                    # Product requirements
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
├── run.sh                    # Run script
├── config/                   # Configuration
├── data/                     # Data files
├── src/                      # Source code
│   ├── database/            # Database layer
│   ├── data_generation/     # Data generation
│   ├── core/                # Core algorithms
│   ├── ml_models/           # ML models
│   └── dashboard/           # Streamlit dashboard
├── models/                   # ML models (gitkeep only)
└── tests/                    # Test files
```

## Security Reminder

⚠️ **Never commit `.env` file to GitHub!** It contains sensitive database credentials.

If you accidentally committed it:
1. Remove it from git: `git rm --cached .env`
2. Add to .gitignore (already done)
3. Commit: `git commit -m "Remove .env from tracking"`
4. Push: `git push`
5. **Change your database password** if the repo is public!

