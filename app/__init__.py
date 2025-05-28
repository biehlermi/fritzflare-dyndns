import logging
import sys
from flask import Flask

# Configure logging to output to the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

# Importiere die Routen, damit sie bei App-Start registriert werden
from app import routes