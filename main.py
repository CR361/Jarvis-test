from app import app, db
import models
import restore_data
import os
import logging
import routes  # Importeer routes als module
from dotenv import load_dotenv

# Laad .env bestand als het bestaat
load_dotenv()

# Stel de juiste logging niveau in
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    with app.app_context():
        # Initialiseer de database tabellen
        logger.info("Maak database tabellen aan...")
        db.create_all()
        
        # Probeer data te herstellen van een backup
        logger.info("Controleren op backups...")
        restore_data.init_app()
        
    # Start de applicatie
    # Voor Replit, gebruik altijd poort 8080 als de expliciet ingestelde poort niet beschikbaar is
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starten van applicatie op poort {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)