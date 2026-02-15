"""
API Flask pour la gestion de fichiers.
Intègre le module FileManager de l'atelier 3.
"""
import os
from flask import Flask, jsonify, request
from file_manager import FileManager


def create_app():
    """Factory function pour créer l'application Flask."""
    app = Flask(__name__)
    
    # Instance globale du FileManager
    file_manager = FileManager()
    
    @app.route("/api/files", methods=["GET"])
    def list_files():
        """
        Liste les fichiers et répertoires d'un chemin donné.
        
        Query params:
            path: Chemin du répertoire à explorer
            
        Returns:
            JSON avec la liste des entrées et leur type
        """
        path = request.args.get("path", ".")
        
        # Vérifier que le chemin existe
        if not os.path.exists(path):
            return jsonify({"error": "Le chemin spécifié n'existe pas"}), 404
        
        if not os.path.isdir(path):
            return jsonify({"error": "Le chemin spécifié n'est pas un répertoire"}), 400
        
        try:
            entries = file_manager.list_entries(path)
            
            # Construire la réponse avec type pour chaque entrée
            result = []
            for entry in entries:
                entry_path = os.path.join(path, entry)
                entry_type = "directory" if os.path.isdir(entry_path) else "file"
                result.append({
                    "name": entry,
                    "type": entry_type
                })
            
            return jsonify({
                "path": path,
                "entries": result
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
