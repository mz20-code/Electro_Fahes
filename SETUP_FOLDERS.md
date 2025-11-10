# Setting Up Required Folders

## 📁 Create These Folders

Before deploying, create these empty folders with .gitkeep files:

### Windows (Command Prompt):
```cmd
mkdir data
mkdir static\uploads
type nul > data\.gitkeep
type nul > static\uploads\.gitkeep
```

### Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Path data -Force
New-Item -ItemType Directory -Path static\uploads -Force
New-Item -ItemType File -Path data\.gitkeep -Force
New-Item -ItemType File -Path static\uploads\.gitkeep -Force
```

### Mac/Linux:
```bash
mkdir -p data
mkdir -p static/uploads
touch data/.gitkeep
touch static/uploads/.gitkeep
```

### Or Manually:
1. Create folder `data/`
2. Create folder `static/uploads/`
3. Create empty file `data/.gitkeep`
4. Create empty file `static/uploads/.gitkeep`

## Why .gitkeep?

Git doesn't track empty folders. The .gitkeep file (empty file) allows git to track the folder structure without tracking the actual database files or uploads.

## Folder Structure:
```
Electro_Fahes/
├── data/
│   └── .gitkeep (empty file)
├── static/
│   ├── uploads/
│   │   └── .gitkeep (empty file)
│   ├── images/
│   │   └── logo.png (your logo)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   └── (all HTML files)
├── app.py
├── requirements.txt
├── render.yaml
└── .gitignore
```

## After Creating:
```bash
git add .
git commit -m "Added folder structure"
git push
```

Done! ✅