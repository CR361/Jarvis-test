import os
import logging
import re

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize Flask-Mail
mail = Mail()

# Initialize CSRF Protection
csrf = CSRFProtect()

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "crm-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Versie 1.1: Verhoog de maximale content lengte voor grote handtekeningen
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Configure the database
# Gebruik de DATABASE_URL omgevingsvariabele indien beschikbaar
database_url = os.environ.get("DATABASE_URL", "")

# Als DATABASE_URL niet beschikbaar is, bouw deze handmatig
if not database_url:
    dbuser = os.environ.get("PGUSER", "")
    dbpass = os.environ.get("PGPASSWORD", "")
    dbhost = os.environ.get("PGHOST", "")
    dbport = os.environ.get("PGPORT", "")
    dbname = os.environ.get("PGDATABASE", "")
    database_url = f"postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}"

# Configuratie parameters voor betrouwbaardere verbinding
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 60,  # Verbinding elke 60 seconden vernieuwen
    "pool_pre_ping": True,  # Connecties testen voor gebruik
    "connect_args": {
        "connect_timeout": 10,  # Verbinding timeout na 10 seconden
        "sslmode": "prefer"     # SSL mode, maar val terug op niet-SSL indien nodig
    }
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure Flask-Mail voor SendGrid
app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "apikey"
app.config["MAIL_PASSWORD"] = os.environ.get("SENDGRID_API_KEY")
app.config["MAIL_DEFAULT_SENDER"] = "noreply@jarvis-crm.com"
app.config["COMPANY_NAME"] = "Uw Bedrijf"

# Server URL voor url_for (_external=True) wordt automatisch gedetecteerd door Flask
# We geven de voorkeur aan HTTPS voor veiligheid
app.config["PREFERRED_URL_SCHEME"] = "https"

# Configure WTF CSRF protection
app.config["WTF_CSRF_ENABLED"] = True

# Custom Jinja2 filter for newlines to HTML
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    return s.replace('\n', '<br />')

# Initialize extensions with the app
db.init_app(app)
mail.init_app(app)
csrf.init_app(app)

# Import and register routes
with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all database tables
    db.create_all()
    
    # Register routes with the app
    routes.register_routes(app)
    
    # Register checklist routes
    from checklist_routes import register_checklist_routes
    register_checklist_routes(app)
    
    # Log database info
    app.logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.logger.info(f"Tables created: {db.metadata.tables.keys()}")

# Importeer en initialiseer de data restore functionaliteit (v1.1)
import restore_data
restore_data.init_app()

# Log app initialization
app.logger.info("CRM application initialized successfully")
