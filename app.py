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
    
    @app.route("/api/selection", methods=["GET"])
    def get_selection():
        """
        Récupère la sélection actuelle.
        
        Returns:
            JSON avec la liste des fichiers sélectionnés
        """
        return jsonify({
            "selection": file_manager.get_selection()
        })
    
    @app.route("/api/selection", methods=["POST"])
    def modify_selection():
        """
        Modifie la sélection de fichiers.
        
        Body JSON:
            action: "select", "deselect", "select_all", "deselect_all"
            entry: Nom de l'entrée (pour select/deselect)
            
        Returns:
            JSON avec le résultat et la sélection actuelle
        """
        data = request.get_json()
        
        if not data or "action" not in data:
            return jsonify({"error": "Action non spécifiée"}), 400
        
        action = data["action"]
        
        if action == "select":
            entry = data.get("entry")
            if not entry:
                return jsonify({"error": "Entrée non spécifiée"}), 400
            
            success = file_manager.select(entry)
            if not success:
                return jsonify({"error": f"L'entrée '{entry}' n'existe pas dans le répertoire courant"}), 400
            
            return jsonify({
                "success": True,
                "selection": file_manager.get_selection()
            })
        
        elif action == "deselect":
            entry = data.get("entry")
            if not entry:
                return jsonify({"error": "Entrée non spécifiée"}), 400
            
            file_manager.deselect(entry)
            return jsonify({
                "success": True,
                "selection": file_manager.get_selection()
            })
        
        elif action == "select_all":
            file_manager.select_all()
            return jsonify({
                "success": True,
                "selection": file_manager.get_selection()
            })
        
        elif action == "deselect_all":
            file_manager.deselect_all()
            return jsonify({
                "success": True,
                "selection": file_manager.get_selection()
            })
        
        else:
            return jsonify({"error": f"Action inconnue: {action}"}), 400
    
    @app.route("/api/files/delete", methods=["DELETE"])
    def delete_files():
        """
        Supprime les fichiers et répertoires sélectionnés.
        
        Returns:
            JSON avec le résultat de la suppression
        """
        selection = file_manager.get_selection()
        
        if not selection:
            return jsonify({
                "success": True,
                "deleted_count": 0,
                "message": "Aucun fichier sélectionné"
            })
        
        errors = file_manager.delete_selection()
        deleted_count = len(selection) - len(errors)
        
        return jsonify({
            "success": len(errors) == 0,
            "deleted_count": deleted_count,
            "errors": errors
        })
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
