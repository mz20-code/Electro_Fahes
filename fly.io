# Electro_Fahes - Fly.io Deployment Guide

## Prerequisites

1. **Install Fly CLI**
   ```bash
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Sign up for Fly.io**
   ```bash
   fly auth signup
   # OR if you already have an account
   fly auth login
   ```

## Project Structure

Make sure your project has these files:
```
electro_fahes/
├── app.py
├── translations.py
├── requirements.txt
├── Dockerfile
├── fly.toml
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   └── logo.png
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── settings.html
│   ├── ai_advisor.html
│   ├── technicians.html
│   ├── videos.html
│   └── error.html
└── data/
```

## Deployment Steps

### 1. Create Fly App

```bash
# Navigate to your project directory
cd electro_fahes

# Launch the app (this will create fly.toml if it doesn't exist)
fly launch
```

When prompted:
- **App name**: Choose a unique name (e.g., `electro-fahes-yourname`)
- **Region**: Choose closest to Lebanon (e.g., `fra` for Frankfurt)
- **PostgreSQL**: No (we're using SQLite)
- **Redis**: No
- **Deploy now**: No (we'll configure first)

### 2. Create Volume for Database

```bash
# Create a persistent volume for the database
fly volumes create electro_data --region fra --size 1
```

### 3. Update fly.toml

Make sure your `fly.toml` looks like this:

```toml
app = "your-app-name"
primary_region = "fra"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512

[mounts]
  source = "electro_data"
  destination = "/app/data"
```

### 4. Deploy the Application

```bash
# Deploy to Fly.io
fly deploy

# This will:
# - Build your Docker image
# - Push it to Fly.io
# - Start your application
```

### 5. Check Deployment Status

```bash
# Check if app is running
fly status

# View logs
fly logs

# Open your app in browser
fly open
```

## Important Configuration Notes

### 1. Database Persistence
- The SQLite database is stored in `/app/data/` which is mounted to the persistent volume
- Data will persist across deployments and restarts

### 2. Keep App Running 24/7
The configuration ensures your app stays running:
- `auto_stop_machines = false` - Prevents automatic shutdown
- `min_machines_running = 1` - Keeps at least one instance running

### 3. HTTPS
- Fly.io automatically provides HTTPS
- `force_https = true` redirects all HTTP traffic to HTTPS

## Useful Commands

```bash
# View current app info
fly info

# SSH into your running app
fly ssh console

# Scale your app (add more instances)
fly scale count 2

# View resource usage
fly status

# Restart your app
fly apps restart

# View environment variables
fly secrets list

# Set environment variable (if needed)
fly secrets set SECRET_KEY=your-secret-key

# Destroy app (if you want to start over)
fly apps destroy your-app-name
```

## Monitoring & Maintenance

### View Logs
```bash
# Real-time logs
fly logs

# Last 200 lines
fly logs --lines 200
```

### Database Backup
```bash
# SSH into the machine
fly ssh console

# Create backup
cd /app/data
sqlite3 electro_fahes.db ".backup backup.db"

# Download the backup
fly sftp get /app/data/backup.db ./local-backup.db
```

### Update Application
```bash
# After making changes to your code
fly deploy

# Force rebuild
fly deploy --no-cache
```

## Troubleshooting

### App Not Starting
```bash
# Check logs for errors
fly logs

# Verify config
fly config validate

# Check app health
fly checks list
```

### Database Issues
```bash
# SSH into the machine
fly ssh console

# Check if database exists
ls -la /app/data/

# Verify database
sqlite3 /app/data/electro_fahes.db "SELECT * FROM users LIMIT 1;"
```

### Out of Memory
```bash
# Increase memory allocation
fly scale memory 1024
```

## Cost Estimation

Fly.io free tier includes:
- 3 shared-cpu-1x VMs with 256MB RAM each
- 3GB persistent volume storage
- 160GB outbound data transfer

Your configuration uses:
- 1 VM with 512MB RAM (may incur charges after free tier)
- 1GB persistent storage (within free tier)

Check current costs:
```bash
fly billing
```

## Custom Domain (Optional)

```bash
# Add your domain
fly certs create yourdomain.com

# Get DNS records to add
fly certs show yourdomain.com
```

Then add these DNS records to your domain:
- A record: `@` → Fly.io IP
- AAAA record: `@` → Fly.io IPv6

## Support

- Fly.io Docs: https://fly.io/docs
- Fly.io Community: https://community.fly.io
- Status Page: https://status.fly.io

## Your App URLs

After deployment:
- **Main URL**: `https://your-app-name.fly.dev`
- **Dashboard**: `https://fly.io/dashboard`
- **Monitoring**: `https://fly.io/apps/your-app-name`