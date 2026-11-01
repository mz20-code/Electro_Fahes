"""Local WSGI launcher; no debug console or public bind by default."""
import os
from waitress import serve
from app import app,RELEASE,ROOT
if __name__=='__main__':
    print('TechVerse '+RELEASE+' | '+str(ROOT)+' | http://127.0.0.1:'+os.environ.get('PORT','5000'))
    serve(app,host=os.environ.get('HOST','127.0.0.1'),port=int(os.environ.get('PORT','5000')),threads=8)
