"""
Tests fonctionnels ATDD pour l'API de gestion de fichiers.
Ces tests utilisent un répertoire de test prédéfini (mock) pour être déterministes.
"""
import pytest
import json
import os
import tempfile
import shutil


class TestFileManagerAPI:
    """Tests fonctionnels pour l'API de gestion de fichiers."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Prépare un répertoire de test avec une structure prédéfinie."""
        # Créer un répertoire temporaire avec une structure connue
        self.test_dir = tempfile.mkdtemp()
        
        # Créer des fichiers de test
        open(os.path.join(self.test_dir, "fichier1.txt"), "w").close()
        open(os.path.join(self.test_dir, "fichier2.txt"), "w").close()
        open(os.path.join(self.test_dir, "document.pdf"), "w").close()
        
        # Créer des sous-répertoires
        os.makedirs(os.path.join(self.test_dir, "dossier1"))
        os.makedirs(os.path.join(self.test_dir, "dossier2"))
        
        # Importer l'application Flask
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        
        yield
        
        # Nettoyer après le test
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    # ==================== ÉTAPE 1 - Liste des fichiers ====================
    
    def test_list_files_returns_entries(self):
        """
        ATDD Test: L'API doit retourner la liste des fichiers d'un répertoire.
        
        Given: Un répertoire contenant des fichiers et dossiers
        When: Je fais une requête GET sur /api/files avec le chemin du répertoire
        Then: Je reçois la liste des entrées du répertoire
        """
        response = self.client.get(f"/api/files?path={self.test_dir}")
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "entries" in data
        
        entries = data["entries"]
        assert len(entries) == 5  # 3 fichiers + 2 dossiers
        
        # Vérifier que nos fichiers sont présents
        entry_names = [e["name"] for e in entries]
        assert "fichier1.txt" in entry_names
        assert "fichier2.txt" in entry_names
        assert "document.pdf" in entry_names
        assert "dossier1" in entry_names
        assert "dossier2" in entry_names
    
    def test_list_files_returns_entry_types(self):
        """
        ATDD Test: L'API doit indiquer le type de chaque entrée (fichier ou dossier).
        
        Given: Un répertoire contenant des fichiers et dossiers
        When: Je fais une requête GET sur /api/files
        Then: Chaque entrée a un type "file" ou "directory"
        """
        response = self.client.get(f"/api/files?path={self.test_dir}")
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        entries = data["entries"]
        
        # Trouver les entrées par nom et vérifier leur type
        for entry in entries:
            if entry["name"] in ["fichier1.txt", "fichier2.txt", "document.pdf"]:
                assert entry["type"] == "file"
            elif entry["name"] in ["dossier1", "dossier2"]:
                assert entry["type"] == "directory"
    
    def test_list_files_invalid_path_returns_error(self):
        """
        ATDD Test: L'API doit retourner une erreur pour un chemin invalide.
        
        Given: Un chemin de répertoire qui n'existe pas
        When: Je fais une requête GET sur /api/files avec ce chemin
        Then: Je reçois une erreur 404
        """
        response = self.client.get("/api/files?path=/chemin/inexistant")
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
