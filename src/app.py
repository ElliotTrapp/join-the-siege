import logging
from flask import Flask
from src.routes import api
from src.config import config
from src.parser import Parser
from src.classifier import Classifier

def create_app():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    app = Flask(__name__)

    app.config['MAX_CONTENT_LENGTH'] = config.MAX_DOC_BYTES

    app.register_blueprint(api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)