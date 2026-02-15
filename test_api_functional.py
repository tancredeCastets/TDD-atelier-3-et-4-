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
    
    # ==================== ÉTAPE 2 - Sélection de fichiers ====================
    
    def test_select_file(self):
        """
        ATDD Test: L'API doit permettre de sélectionner un fichier.
        
        Given: Un répertoire exploré avec des fichiers
        When: Je fais une requête POST sur /api/selection avec un fichier
        Then: Le fichier est ajouté à la sélection
        """
        # D'abord explorer le répertoire
        self.client.get(f"/api/files?path={self.test_dir}")
        
        # Sélectionner un fichier
        response = self.client.post("/api/selection", json={
            "action": "select",
            "entry": "fichier1.txt"
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "fichier1.txt" in data["selection"]
    
    def test_select_multiple_files(self):
        """
        ATDD Test: L'API doit permettre de sélectionner plusieurs fichiers.
        
        Given: Un répertoire exploré
        When: Je sélectionne plusieurs fichiers
        Then: Tous les fichiers sont dans la sélection
        """
        self.client.get(f"/api/files?path={self.test_dir}")
        
        self.client.post("/api/selection", json={"action": "select", "entry": "fichier1.txt"})
        self.client.post("/api/selection", json={"action": "select", "entry": "fichier2.txt"})
        
        response = self.client.get("/api/selection")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "fichier1.txt" in data["selection"]
        assert "fichier2.txt" in data["selection"]
    
    def test_deselect_file(self):
        """
        ATDD Test: L'API doit permettre de désélectionner un fichier.
        
        Given: Un fichier sélectionné
        When: Je fais une requête POST pour désélectionner
        Then: Le fichier n'est plus dans la sélection
        """
        self.client.get(f"/api/files?path={self.test_dir}")
        self.client.post("/api/selection", json={"action": "select", "entry": "fichier1.txt"})
        
        response = self.client.post("/api/selection", json={
            "action": "deselect",
            "entry": "fichier1.txt"
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "fichier1.txt" not in data["selection"]
    
    def test_select_all(self):
        """
        ATDD Test: L'API doit permettre de sélectionner toutes les entrées.
        
        Given: Un répertoire exploré
        When: Je fais une requête POST pour tout sélectionner
        Then: Toutes les entrées sont sélectionnées
        """
        self.client.get(f"/api/files?path={self.test_dir}")
        
        response = self.client.post("/api/selection", json={"action": "select_all"})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["selection"]) == 5
    
    def test_deselect_all(self):
        """
        ATDD Test: L'API doit permettre de tout désélectionner.
        
        Given: Des fichiers sélectionnés
        When: Je fais une requête POST pour tout désélectionner
        Then: La sélection est vide
        """
        self.client.get(f"/api/files?path={self.test_dir}")
        self.client.post("/api/selection", json={"action": "select_all"})
        
        response = self.client.post("/api/selection", json={"action": "deselect_all"})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["selection"]) == 0
    
    def test_select_nonexistent_file_fails(self):
        """
        ATDD Test: La sélection d'un fichier inexistant doit échouer.
        
        Given: Un répertoire exploré
        When: J'essaie de sélectionner un fichier qui n'existe pas
        Then: Je reçois une erreur
        """
        self.client.get(f"/api/files?path={self.test_dir}")
        
        response = self.client.post("/api/selection", json={
            "action": "select",
            "entry": "fichier_inexistant.txt"
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_navigate_to_subdirectory(self):
        """
        ATDD Test: L'API doit permettre de naviguer dans un sous-répertoire.
        
        Given: Un répertoire avec des sous-répertoires
        When: Je liste les fichiers du sous-répertoire
        Then: Je vois le contenu du sous-répertoire
        """
        # Créer un fichier dans le sous-répertoire
        subdir_path = os.path.join(self.test_dir, "dossier1")
        open(os.path.join(subdir_path, "sous_fichier.txt"), "w").close()
        
        response = self.client.get(f"/api/files?path={subdir_path}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        entry_names = [e["name"] for e in data["entries"]]
        assert "sous_fichier.txt" in entry_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
