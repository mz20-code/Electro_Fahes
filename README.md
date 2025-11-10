# Electro_Fahes - Smart Solar Inverter Solutions

A professional AI-powered web application for solar inverter diagnostics and repair services in Lebanon.

## 🚀 Features

- **AI-Powered Diagnostics**: Upload inverter error screen images for instant AI analysis
- **Expert Technicians**: Connect with certified solar inverter specialists
- **Video Tutorials**: Access comprehensive learning resources
- **User Authentication**: Secure login and registration system
- **Email Verification**: Account verification system (demo auto-verifies)
- **Settings Page**: Update profile name and change language (English/Arabic)
- **Responsive Design**: Beautiful modern UI that works on all devices
- **3D Animated Backgrounds**: Unique floating shapes with smooth animations
- **Glassmorphism Design**: Modern frosted glass effect on cards
- **Beautiful Gradients**: Eye-catching color combinations throughout

## ✨ What's New

### Settings Page
- **Profile Management**: Update your full name
- **Language Selection**: Choose between English and Arabic
- **Account Status**: View verification status and member details
- **Beautiful UI**: Glassmorphism cards with 3D animated shapes

### Design Updates
- **3D Floating Shapes**: Animated geometric shapes in the background
- **Unique Color Gradients**: Custom gradient combinations on each page
- **Glassmorphism Effects**: Modern frosted glass design on all cards
- **Smooth Animations**: Floating, rotating, and morphing shape animations
- **Eye-Comfortable Colors**: Beautiful colors that are not harsh on the eyes

### Removed Dashboard Page
- Direct access to AI Advisor after login
- Streamlined navigation without dashboard clutter
- Settings page replaces profile management

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

## 🛠️ Installation & Setup

### 1. Clone or Download the Project

```bash
git clone https://github.com/yourusername/electro_fahes.git
cd electro_fahes
```

### 2. Create Project Structure

```
Electro_Fahes/
│
├── app.py                              # Main Flask application
├── requirements.txt                    # Python dependencies
├── README.md                          # This file
│
├── templates/                          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── ai_advisor.html
│   ├── technicians.html
│   ├── videos.html
│   └── error.html
│
├── static/                             # Static assets
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   └── logo.png                   # Add your logo here
│   └── uploads/                       # Created automatically
│
└── data/                              # Database (created automatically)
    └── electro_fahes.db
```

### 3. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create Required Directories

```bash
mkdir -p static/images static/uploads data
```

### 6. Add Logo Image

Place your logo image at `static/images/logo.png`. If you don't have one, you can:
- Create a simple placeholder logo
- Download a free logo from unsplash.com or similar
- Use any PNG/JPG image temporarily

### 7. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📖 Usage Guide

### First Time Setup

1. **Access the Application**: Open `http://localhost:5000` in your browser
2. **Create Account**: Click "Get Started Free" and fill in:
   - Full Name
   - Email Address
   - Password (minimum 6 characters)
3. **Login**: After registration, sign in with your credentials
4. **Email Verification**: For demo purposes, accounts are auto-verified

### Using the Dashboard

After logging in, you'll see:

- **Quick Stats**: View your activity summary
- **AI Diagnostics Card**: Access AI-powered inverter analysis
- **Technicians Card**: Find expert repair specialists
- **Videos Card**: Browse tutorial content

### AI Advisor

1. Navigate to **AI Advisor** from the dashboard
2. Enter your inverter model (e.g., "Sunny Boy 5.0")
3. Upload an image of the error screen
4. Click "Analyze Now"
5. View detailed diagnosis including:
   - Detected issue
   - Severity level
   - Recommended solution
   - Estimated repair cost

### Find Technicians

- Browse certified technicians
- View their specialties and experience
- Contact directly via phone or email

### Watch Tutorials

- Access video guides
- Learn troubleshooting techniques
- Maintenance best practices

## 🎨 Customization

### Colors

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --primary: #4F46E5;      /* Main brand color */
    --secondary: #06B6D4;    /* Secondary color */
    --accent: #F59E0B;       /* Accent color */
    /* ... */
}
```

### Logo & Branding

Replace `static/images/logo.png` with your company logo.

### Technicians Data

Edit the `init_db()` function in `app.py` to add/modify technician information.

## 🔐 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection (via Flask)
- Secure file upload handling
- SQL injection prevention

## 🚀 Production Deployment

### Using Gunicorn (Recommended)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

For production, set:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

### Database

The app uses SQLite for simplicity. For production, consider:
- PostgreSQL
- MySQL
- MongoDB

## 📱 Responsive Design

The application is fully responsive and works on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1440px+)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Database Errors

```bash
# Reset database
rm data/electro_fahes.db
python app.py  # Will recreate database
```

### Port Already in Use

```bash
# Use different port
python app.py --port 5001
```

### Missing Modules

```bash
pip install -r requirements.txt --upgrade
```

## 💡 Future Enhancements

- [ ] Real AI model integration
- [ ] Email sending functionality
- [ ] Advanced user profiles
- [ ] Service request tracking
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Mobile app version

## 📞 Support

For support, email: support@electro-fahes.com

## 🌟 Acknowledgments

- Flask Web Framework
- Inter Font by Rasmus Andersson
- Icons: Unicode Emoji

---

**Made in Lebanon**