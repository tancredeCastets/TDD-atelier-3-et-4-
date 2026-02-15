"""
API Flask pour la gestion de fichiers.
Intègre le module FileManager de l'atelier 3.
"""
from flask import Flask


def create_app():
    """Factory function pour créer l'application Flask."""
    app = Flask(__name__)
    
    # TODO: Implémenter les routes
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
