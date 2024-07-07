from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['REPORT_FOLDER'] = 'reports/'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

    from .routes import main
    app.register_blueprint(main)

    return app
