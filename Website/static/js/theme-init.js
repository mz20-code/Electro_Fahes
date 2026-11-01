try { const theme = localStorage.getItem('techverse_theme'); if (theme === 'dark' || theme === 'light') document.documentElement.dataset.theme = theme; } catch (e) {}
