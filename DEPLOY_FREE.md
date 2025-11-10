# Deploy Electro_Fahes for FREE 24/7

## 🚀 Best Free Options for 24/7 Hosting

### Option 1: Render.com (RECOMMENDED) ⭐
**Best for: Flask apps, Easy setup, Free forever**

#### Step-by-Step Setup:

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub (recommended)

2. **Push Your Code to GitHub**
   ```bash
   # Initialize git in your project folder
   cd Electro_Fahes
   git init
   git add .
   git commit -m "Initial commit"
   
   # Create repository on GitHub
   # Go to github.com → New Repository → "Electro_Fahes"
   
   # Push to GitHub
   git remote add origin https://github.com/YOUR_USERNAME/Electro_Fahes.git
   git branch -M main
   git push -u origin main
   ```

3. **Create `render.yaml`** (add this file to your project):
   ```yaml
   services:
     - type: web
       name: electro-fahes
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app:app
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
         - key: SECRET_KEY
           generateValue: true
   ```

4. **Update `requirements.txt`**:
   ```txt
   Flask==3.0.0
   Werkzeug==3.0.1
   Pillow==10.1.0
   gunicorn==21.2.0
   ```

5. **Deploy on Render**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select "Electro_Fahes"
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

6. **Your Site is Live!**
   - URL: `https://electro-fahes.onrender.com`
   - Share this link with anyone!

**Pros:**
- ✅ Completely FREE forever
- ✅ 750 hours/month (enough for 24/7)
- ✅ Auto-deploys on git push
- ✅ Free SSL certificate
- ✅ Easy to use

**Cons:**
- ⚠️ Sleeps after 15 min inactivity (wakes in 30 seconds)
- ⚠️ Limited to 512MB RAM

---

### Option 2: PythonAnywhere (Alternative)

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Sign up (Free account)

2. **Upload Your Code**
   - Dashboard → Files → Upload files
   - Or use git: `git clone https://github.com/YOUR_USERNAME/Electro_Fahes.git`

3. **Setup Web App**
   - Web tab → Add new web app
   - Select Flask
   - Python version: 3.10
   - Path: `/home/yourusername/Electro_Fahes/app.py`

4. **Install Requirements**
   - Bash console:
   ```bash
   cd Electro_Fahes
   pip3 install --user -r requirements.txt
   ```

5. **Configure WSGI**
   - Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   ```python
   import sys
   path = '/home/yourusername/Electro_Fahes'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

6. **Reload Web App**
   - Green button "Reload"
   - Visit: `https://yourusername.pythonanywhere.com`

**Pros:**
- ✅ Always on (no sleep)
- ✅ Easy file management
- ✅ Good documentation

**Cons:**
- ⚠️ Need to reload manually after changes
- ⚠️ Limited to 100MB disk space

---

### Option 3: Railway.app

1. **Create Account**
   - https://railway.app
   - Sign up with GitHub

2. **Deploy**
   - New Project → Deploy from GitHub
   - Select your repository
   - Railway auto-detects Flask app
   - Click Deploy

**Pros:**
- ✅ Very fast deployment
- ✅ Auto SSL
- ✅ Good performance

**Cons:**
- ⚠️ Free tier: $5 credit/month (usually enough)
- ⚠️ May need payment method for verification

---

## 📝 Required Files for Deployment

### 1. Create `.gitignore`:
```
__pycache__/
*.pyc
*.db
*.sqlite
data/*.db
static/uploads/*
!static/uploads/.gitkeep
venv/
.env
.DS_Store
```

### 2. Create `Procfile` (for some platforms):
```
web: gunicorn app:app
```

### 3. Create `runtime.txt` (optional):
```
python-3.11.0
```

### 4. Update `app.py` for Production:

Change the last lines:
```python
if __name__ == '__main__':
    init_db()
    # For production, remove debug=True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## 🔒 Important Security Steps

1. **Set Secret Key as Environment Variable**

In `app.py`:
```python
import os
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
```

On Render:
- Settings → Environment → Add `SECRET_KEY` → Generate

2. **Disable Debug Mode**
```python
app.run(debug=False)  # Never use debug=True in production
```

3. **Use Environment Variables for Sensitive Data**

---

## 🌐 Custom Domain (Optional - Still Free!)

### With Render:
1. Buy domain from Namecheap/GoDaddy (~$1/year for .xyz)
2. Render Settings → Custom Domain
3. Add DNS records as shown

### Free Domain Options:
- Freenom.com (free .tk, .ml domains)
- Use Render's free subdomain: `yourapp.onrender.com`

---

## 📊 Keep Your Site Active (Prevent Sleep)

### Method 1: UptimeRobot (FREE)
1. Go to https://uptimerobot.com
2. Sign up free
3. Add New Monitor
4. Type: HTTP(S)
5. URL: Your site URL
6. Monitoring Interval: 5 minutes
7. UptimeRobot pings your site every 5 min → keeps it awake!

### Method 2: Cron-Job.org
1. Go to https://cron-job.org
2. Sign up free
3. Create new cron job
4. URL: Your site URL
5. Schedule: Every 5 minutes

---

## 📱 Progressive Web App (Bonus)

Add this to make your site installable on phones:

Create `static/manifest.json`:
```json
{
  "name": "Electro_Fahes",
  "short_name": "E_Fahes",
  "description": "AI Solar Inverter Diagnostics",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0E1A",
  "theme_color": "#00D9FF",
  "icons": [
    {
      "src": "/static/images/logo.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Add to `base.html` `<head>`:
```html
<link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
<meta name="theme-color" content="#00D9FF">
<meta name="apple-mobile-web-app-capable" content="yes">
```

---

## 🚀 Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` updated with gunicorn
- [ ] `.gitignore` created
- [ ] `render.yaml` created (for Render)
- [ ] Database in data/ folder (will be created on first run)
- [ ] Logo in static/images/
- [ ] Secret key in environment variables
- [ ] Debug mode OFF
- [ ] Deployed and tested
- [ ] UptimeRobot monitoring set up

---

## 🎉 You're Live!

Your site is now:
- ✅ Accessible worldwide
- ✅ Running 24/7
- ✅ HTTPS secured
- ✅ FREE forever

**Share your link:**
`https://electro-fahes.onrender.com`

Or whatever custom domain you choose!

---

## 🆘 Troubleshooting

### Site not loading?
- Check Render logs: Dashboard → Logs
- Ensure all files are committed to GitHub
- Verify requirements.txt has all packages

### Database issues?
- SQLite works on Render
- Database resets on each deploy (free tier)
- Consider upgrading or using external DB

### Upload folder issues?
- Create empty file: `static/uploads/.gitkeep`
- Uploads are temporary on free hosting
- Consider using Cloudinary for permanent storage

### Getting "Application Error"?
- Check if gunicorn is in requirements.txt
- Verify app.py has `app` variable
- Check Python version compatibility

---

## 💰 Upgrade Options (If Needed Later)

**If you need more:**
- Render: $7/month for always-on
- Heroku: $7/month
- DigitalOcean: $6/month
- AWS/GCP: Pay as you go

**But for now, FREE hosting is perfect!** 🎉