"""
Module de sélection et manipulation de fichiers.
"""
import os
import shutil
import random
from typing import List, Optional, Set


class FileManager:
    """Classe pour énumérer, sélectionner et manipuler des fichiers et répertoires."""
    
    # Dictionnaires pour la génération de noms aléatoires
    NOUNS = [
        "soleil", "lune", "etoile", "montagne", "riviere",
        "foret", "ocean", "desert", "prairie", "colline",
        "nuage", "vent", "tempete", "aurore", "crepuscule",
        "jardin", "cascade", "vallee", "plaine", "horizon"
    ]
    
    ADJECTIVES = [
        "grand", "petit", "beau", "ancien", "nouveau",
        "rouge", "bleu", "vert", "dore", "argente",
        "rapide", "calme", "brillant", "sombre", "clair",
        "joyeux", "paisible", "mysterieux", "magique", "eternel"
    ]
    
    def __init__(self):
        """Initialise le FileManager."""
        self._current_directory: Optional[str] = None
        self._entries: List[str] = []
        self._selection: Set[str] = set()
    
    def list_entries(self, directory: str) -> List[str]:
        """
        Énumère les entrées (fichiers et répertoires) d'un répertoire donné.
        
        Args:
            directory: Chemin du répertoire à explorer
            
        Returns:
            Liste des noms d'entrées (fichiers et répertoires)
        """
        self._current_directory = directory
        self._entries = os.listdir(directory)
        self._selection.clear()
        return self._entries.copy()
    
    def get_entries(self) -> List[str]:
        """Retourne la liste des entrées du répertoire courant."""
        return self._entries.copy()
    
    def select(self, entry: str) -> bool:
        """
        Sélectionne une entrée.
        
        Args:
            entry: Nom de l'entrée à sélectionner
            
        Returns:
            True si l'entrée a été sélectionnée, False si elle n'existe pas
        """
        if entry in self._entries:
            self._selection.add(entry)
            return True
        return False
    
    def deselect(self, entry: str) -> bool:
        """
        Désélectionne une entrée.
        
        Args:
            entry: Nom de l'entrée à désélectionner
            
        Returns:
            True si l'entrée a été désélectionnée, False si elle n'était pas sélectionnée
        """
        if entry in self._selection:
            self._selection.remove(entry)
            return True
        return False
    
    def select_all(self) -> None:
        """Sélectionne toutes les entrées."""
        self._selection = set(self._entries)
    
    def deselect_all(self) -> None:
        """Désélectionne toutes les entrées."""
        self._selection.clear()
    
    def get_selection(self) -> List[str]:
        """Retourne la liste des entrées sélectionnées."""
        return list(self._selection)
    
    def _generate_random_name(self) -> str:
        """Génère un nom aléatoire en combinant un adjectif et un nom."""
        adjective = random.choice(self.ADJECTIVES)
        noun = random.choice(self.NOUNS)
        return f"{adjective}_{noun}"
    
    def _get_destination_path(self, destination: Optional[str] = None) -> str:
        """
        Détermine le chemin de destination.
        
        Args:
            destination: Chemin de destination optionnel
            
        Returns:
            Chemin de destination (fourni ou généré)
        """
        if destination:
            return destination
        
        random_name = self._generate_random_name()
        return os.path.join(self._current_directory, random_name)
    
    def copy_selection(self, destination: Optional[str] = None) -> str:
        """
        Copie les entrées sélectionnées vers la destination.
        
        Args:
            destination: Chemin de destination optionnel
            
        Returns:
            Chemin de destination utilisé
        """
        dest_path = self._get_destination_path(destination)
        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)
        
        for entry in self._selection:
            source = os.path.join(self._current_directory, entry)
            target = os.path.join(dest_path, entry)
            
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        
        return dest_path
    
    def move_selection(self, destination: Optional[str] = None) -> str:
        """
        Déplace les entrées sélectionnées vers la destination.
        
        Args:
            destination: Chemin de destination optionnel
            
        Returns:
            Chemin de destination utilisé
        """
        dest_path = self._get_destination_path(destination)
        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)
        
        for entry in self._selection:
            source = os.path.join(self._current_directory, entry)
            target = os.path.join(dest_path, entry)
            shutil.move(source, target)
        
        # Retirer les entrées déplacées de la liste et de la sélection
        for entry in list(self._selection):
            self._entries.remove(entry)
        self._selection.clear()
        
        return dest_path
    
    def delete_selection(self) -> None:
        """Supprime les entrées sélectionnées."""
        for entry in self._selection:
            path = os.path.join(self._current_directory, entry)
            
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        
        # Retirer les entrées supprimées de la liste
        for entry in list(self._selection):
            self._entries.remove(entry)
        self._selection.clear()
