"""
Module de sélection et manipulation de fichiers.
"""
import os
import shutil
import random
from typing import List, Optional, Set


class DefaultFilesystem:
    """Implémentation par défaut pour l'exploration du système de fichiers."""
    
    def list_directory(self, path: str) -> List[str]:
        """Liste les entrées d'un répertoire."""
        return os.listdir(path)
    
    def exists(self, path: str) -> bool:
        """Vérifie si un chemin existe."""
        return os.path.exists(path)
    
    def is_directory(self, path: str) -> bool:
        """Vérifie si un chemin est un répertoire."""
        return os.path.isdir(path)
    
    def join_path(self, *paths) -> str:
        """Joint des chemins."""
        return os.path.join(*paths)
    
    def create_directory(self, path: str) -> None:
        """Crée un répertoire."""
        os.makedirs(path, exist_ok=True)


class DefaultFileOperations:
    """Implémentation par défaut pour les opérations sur fichiers."""
    
    def copy_file(self, source: str, destination: str) -> None:
        """Copie un fichier."""
        shutil.copy2(source, destination)
    
    def copy_directory(self, source: str, destination: str) -> None:
        """Copie un répertoire."""
        shutil.copytree(source, destination)
    
    def move(self, source: str, destination: str) -> None:
        """Déplace un fichier ou répertoire."""
        shutil.move(source, destination)
    
    def delete_file(self, path: str) -> None:
        """Supprime un fichier."""
        os.remove(path)
    
    def delete_directory(self, path: str) -> None:
        """Supprime un répertoire."""
        shutil.rmtree(path)


class DefaultRandomGenerator:
    """Implémentation par défaut pour le tirage aléatoire."""
    
    def choice(self, sequence):
        """Choisit un élément aléatoire dans une séquence."""
        return random.choice(sequence)


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
    
    def __init__(self, filesystem=None, file_operations=None, random_generator=None):
        """
        Initialise le FileManager avec des dépendances injectables.
        
        Args:
            filesystem: Interface pour l'exploration du système de fichiers (simulation possible)
            file_operations: Interface pour les opérations sur fichiers (simulation possible)
            random_generator: Interface pour le tirage aléatoire (simulation possible)
        """
        self._filesystem = filesystem or DefaultFilesystem()
        self._file_operations = file_operations or DefaultFileOperations()
        self._random = random_generator or DefaultRandomGenerator()
        
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
        self._entries = self._filesystem.list_directory(directory)
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
        adjective = self._random.choice(self.ADJECTIVES)
        noun = self._random.choice(self.NOUNS)
        return f"{adjective}_{noun}"
    
    def _generate_unique_name(self) -> str:
        """
        Génère un nom de répertoire unique.
        Retente jusqu'à 10 fois si le nom existe déjà.
        Après 10 tentatives, ajoute un numéro au dernier nom tiré.
        """
        max_retries = 10
        last_name = None
        
        for _ in range(max_retries):
            name = self._generate_random_name()
            last_name = name
            path = self._filesystem.join_path(self._current_directory, name)
            if not self._filesystem.exists(path):
                return name
        
        # Après 10 tentatives, numéroter le dernier nom
        counter = 1
        while True:
            numbered_name = f"{last_name}_{counter}"
            path = self._filesystem.join_path(self._current_directory, numbered_name)
            if not self._filesystem.exists(path):
                return numbered_name
            counter += 1
    
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
        
        random_name = self._generate_unique_name()
        return self._filesystem.join_path(self._current_directory, random_name)
    
    def copy_selection(self, destination: Optional[str] = None) -> str:
        """
        Copie les entrées sélectionnées vers la destination.
        
        Args:
            destination: Chemin de destination optionnel
            
        Returns:
            Chemin de destination utilisé
        """
        dest_path = self._get_destination_path(destination)
        
        if not self._filesystem.exists(dest_path):
            self._filesystem.create_directory(dest_path)
        
        for entry in self._selection:
            source = self._filesystem.join_path(self._current_directory, entry)
            target = self._filesystem.join_path(dest_path, entry)
            
            if self._filesystem.is_directory(source):
                self._file_operations.copy_directory(source, target)
            else:
                self._file_operations.copy_file(source, target)
        
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
        
        if not self._filesystem.exists(dest_path):
            self._filesystem.create_directory(dest_path)
        
        for entry in self._selection:
            source = self._filesystem.join_path(self._current_directory, entry)
            target = self._filesystem.join_path(dest_path, entry)
            self._file_operations.move(source, target)
        
        # Retirer les entrées déplacées de la liste et de la sélection
        for entry in list(self._selection):
            self._entries.remove(entry)
        self._selection.clear()
        
        return dest_path
    
    def delete_selection(self) -> None:
        """Supprime les entrées sélectionnées."""
        for entry in self._selection:
            path = self._filesystem.join_path(self._current_directory, entry)
            
            if self._filesystem.is_directory(path):
                self._file_operations.delete_directory(path)
            else:
                self._file_operations.delete_file(path)
        
        # Retirer les entrées supprimées de la liste
        for entry in list(self._selection):
            self._entries.remove(entry)
        self._selection.clear()
