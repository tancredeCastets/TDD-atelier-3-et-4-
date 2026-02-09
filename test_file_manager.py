"""
Tests unitaires pour le module FileManager.
Utilise des mocks pour simuler le système de fichiers et le tirage aléatoire.
"""
import unittest
from file_manager import FileManager


class MockFilesystem:
    """Mock pour simuler l'exploration du système de fichiers."""
    
    def __init__(self):
        self.directories = {}
        self.files = set()
        self.existing_paths = set()
        self.created_directories = []
    
    def setup_directory(self, path: str, entries: list):
        """Configure le contenu d'un répertoire."""
        self.directories[path] = entries
        self.existing_paths.add(path)
    
    def add_file(self, path: str):
        """Ajoute un fichier existant."""
        self.files.add(path)
        self.existing_paths.add(path)
    
    def add_directory(self, path: str):
        """Ajoute un répertoire existant."""
        self.existing_paths.add(path)
    
    def list_directory(self, path: str) -> list:
        """Liste les entrées d'un répertoire."""
        return self.directories.get(path, [])
    
    def exists(self, path: str) -> bool:
        """Vérifie si un chemin existe."""
        return path in self.existing_paths
    
    def is_directory(self, path: str) -> bool:
        """Vérifie si un chemin est un répertoire."""
        return path in self.existing_paths and path not in self.files
    
    def is_file(self, path: str) -> bool:
        """Vérifie si un chemin est un fichier."""
        return path in self.files
    
    def join_path(self, *paths) -> str:
        """Joint des chemins avec /."""
        return "/".join(paths)
    
    def create_directory(self, path: str) -> None:
        """Crée un répertoire."""
        self.created_directories.append(path)
        self.existing_paths.add(path)


class MockFileOperations:
    """Mock pour simuler les opérations sur fichiers."""
    
    def __init__(self):
        self.copied_files = []
        self.copied_directories = []
        self.moved_items = []
        self.deleted_files = []
        self.deleted_directories = []
    
    def copy_file(self, source: str, destination: str) -> None:
        """Simule la copie d'un fichier."""
        self.copied_files.append((source, destination))
    
    def copy_directory(self, source: str, destination: str) -> None:
        """Simule la copie d'un répertoire."""
        self.copied_directories.append((source, destination))
    
    def move(self, source: str, destination: str) -> None:
        """Simule le déplacement d'un fichier ou répertoire."""
        self.moved_items.append((source, destination))
    
    def delete_file(self, path: str) -> None:
        """Simule la suppression d'un fichier."""
        self.deleted_files.append(path)
    
    def delete_directory(self, path: str) -> None:
        """Simule la suppression d'un répertoire."""
        self.deleted_directories.append(path)


class MockRandomGenerator:
    """Mock pour simuler le tirage aléatoire."""
    
    def __init__(self, values=None):
        self.values = values or []
        self.call_index = 0
        self.calls = []
    
    def set_values(self, values: list):
        """Configure les valeurs à retourner."""
        self.values = values
        self.call_index = 0
    
    def choice(self, sequence):
        """Retourne une valeur prédéfinie."""
        self.calls.append(sequence)
        if self.call_index < len(self.values):
            value = self.values[self.call_index]
            self.call_index += 1
            return value
        return sequence[0] if sequence else None


class TestFileManagerListEntries(unittest.TestCase):
    """Tests pour l'énumération des entrées."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_list_empty_directory(self):
        """Test: énumérer un répertoire vide."""
        self.mock_fs.setup_directory("/test", [])
        
        entries = self.manager.list_entries("/test")
        
        self.assertEqual(entries, [])
    
    def test_list_directory_with_files(self):
        """Test: énumérer un répertoire avec des fichiers."""
        self.mock_fs.setup_directory("/test", ["file1.txt", "file2.txt"])
        
        entries = self.manager.list_entries("/test")
        
        self.assertEqual(entries, ["file1.txt", "file2.txt"])
    
    def test_list_directory_with_subdirectories(self):
        """Test: énumérer un répertoire avec des sous-répertoires."""
        self.mock_fs.setup_directory("/test", ["dir1", "dir2"])
        
        entries = self.manager.list_entries("/test")
        
        self.assertEqual(entries, ["dir1", "dir2"])
    
    def test_list_directory_with_mixed_entries(self):
        """Test: énumérer un répertoire avec fichiers et sous-répertoires."""
        self.mock_fs.setup_directory("/test", ["file1.txt", "dir1", "file2.txt", "dir2"])
        
        entries = self.manager.list_entries("/test")
        
        self.assertEqual(entries, ["file1.txt", "dir1", "file2.txt", "dir2"])
    
    def test_list_entries_clears_previous_selection(self):
        """Test: lister un nouveau répertoire efface la sélection précédente."""
        self.mock_fs.setup_directory("/test1", ["file1.txt"])
        self.mock_fs.setup_directory("/test2", ["file2.txt"])
        
        self.manager.list_entries("/test1")
        self.manager.select("file1.txt")
        self.manager.list_entries("/test2")
        
        self.assertEqual(self.manager.get_selection(), [])
    
    def test_get_entries_returns_copy(self):
        """Test: get_entries retourne une copie de la liste."""
        self.mock_fs.setup_directory("/test", ["file1.txt"])
        self.manager.list_entries("/test")
        
        entries = self.manager.get_entries()
        entries.append("fake.txt")
        
        self.assertEqual(self.manager.get_entries(), ["file1.txt"])


class TestFileManagerSelection(unittest.TestCase):
    """Tests pour la gestion de la sélection."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
        self.mock_fs.setup_directory("/test", ["file1.txt", "file2.txt", "dir1"])
        self.manager.list_entries("/test")
    
    def test_select_single_entry(self):
        """Test: sélectionner une seule entrée."""
        result = self.manager.select("file1.txt")
        
        self.assertTrue(result)
        self.assertIn("file1.txt", self.manager.get_selection())
    
    def test_select_multiple_entries(self):
        """Test: sélectionner plusieurs entrées."""
        self.manager.select("file1.txt")
        self.manager.select("dir1")
        
        selection = self.manager.get_selection()
        self.assertIn("file1.txt", selection)
        self.assertIn("dir1", selection)
        self.assertEqual(len(selection), 2)
    
    def test_select_nonexistent_entry(self):
        """Test: sélectionner une entrée inexistante."""
        result = self.manager.select("nonexistent.txt")
        
        self.assertFalse(result)
        self.assertEqual(self.manager.get_selection(), [])
    
    def test_select_same_entry_twice(self):
        """Test: sélectionner deux fois la même entrée."""
        self.manager.select("file1.txt")
        self.manager.select("file1.txt")
        
        selection = self.manager.get_selection()
        self.assertEqual(len(selection), 1)
    
    def test_deselect_entry(self):
        """Test: désélectionner une entrée."""
        self.manager.select("file1.txt")
        result = self.manager.deselect("file1.txt")
        
        self.assertTrue(result)
        self.assertNotIn("file1.txt", self.manager.get_selection())
    
    def test_deselect_not_selected_entry(self):
        """Test: désélectionner une entrée non sélectionnée."""
        result = self.manager.deselect("file1.txt")
        
        self.assertFalse(result)
    
    def test_select_all(self):
        """Test: sélectionner toutes les entrées."""
        self.manager.select_all()
        
        selection = self.manager.get_selection()
        self.assertEqual(len(selection), 3)
        self.assertIn("file1.txt", selection)
        self.assertIn("file2.txt", selection)
        self.assertIn("dir1", selection)
    
    def test_deselect_all(self):
        """Test: désélectionner toutes les entrées."""
        self.manager.select_all()
        self.manager.deselect_all()
        
        self.assertEqual(self.manager.get_selection(), [])
    
    def test_select_all_on_empty_directory(self):
        """Test: sélectionner tout dans un répertoire vide."""
        self.mock_fs.setup_directory("/empty", [])
        self.manager.list_entries("/empty")
        
        self.manager.select_all()
        
        self.assertEqual(self.manager.get_selection(), [])


class TestFileManagerCopy(unittest.TestCase):
    """Tests pour la copie de fichiers."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_copy_single_file_to_destination(self):
        """Test: copier un fichier vers une destination spécifiée."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection("/dest")
        
        self.assertEqual(result, "/dest")
        self.assertIn(("/source/file1.txt", "/dest/file1.txt"), self.mock_ops.copied_files)
    
    def test_copy_directory_to_destination(self):
        """Test: copier un répertoire vers une destination spécifiée."""
        self.mock_fs.setup_directory("/source", ["dir1"])
        self.mock_fs.add_directory("/source/dir1")
        self.manager.list_entries("/source")
        self.manager.select("dir1")
        
        result = self.manager.copy_selection("/dest")
        
        self.assertEqual(result, "/dest")
        self.assertIn(("/source/dir1", "/dest/dir1"), self.mock_ops.copied_directories)
    
    def test_copy_multiple_items(self):
        """Test: copier plusieurs éléments."""
        self.mock_fs.setup_directory("/source", ["file1.txt", "dir1"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_fs.add_directory("/source/dir1")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        self.manager.select("dir1")
        
        self.manager.copy_selection("/dest")
        
        self.assertEqual(len(self.mock_ops.copied_files), 1)
        self.assertEqual(len(self.mock_ops.copied_directories), 1)
    
    def test_copy_creates_destination_if_not_exists(self):
        """Test: la copie crée le répertoire de destination s'il n'existe pas."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.copy_selection("/new_dest")
        
        self.assertIn("/new_dest", self.mock_fs.created_directories)
    
    def test_copy_does_not_create_existing_destination(self):
        """Test: la copie ne recrée pas un répertoire existant."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_fs.add_directory("/dest")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.copy_selection("/dest")
        
        self.assertNotIn("/dest", self.mock_fs.created_directories)
    
    def test_copy_with_random_destination(self):
        """Test: copie avec génération aléatoire du nom de destination."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_random.set_values(["beau", "soleil"])
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection()
        
        self.assertEqual(result, "/source/beau_soleil")
    
    def test_copy_keeps_selection(self):
        """Test: la copie conserve la sélection."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.copy_selection("/dest")
        
        self.assertIn("file1.txt", self.manager.get_selection())
    
    def test_copy_empty_selection(self):
        """Test: copier une sélection vide."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.manager.list_entries("/source")
        
        result = self.manager.copy_selection("/dest")
        
        self.assertEqual(result, "/dest")
        self.assertEqual(self.mock_ops.copied_files, [])


class TestFileManagerMove(unittest.TestCase):
    """Tests pour le déplacement de fichiers."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_move_single_file_to_destination(self):
        """Test: déplacer un fichier vers une destination spécifiée."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.move_selection("/dest")
        
        self.assertEqual(result, "/dest")
        self.assertIn(("/source/file1.txt", "/dest/file1.txt"), self.mock_ops.moved_items)
    
    def test_move_removes_from_entries(self):
        """Test: le déplacement retire les entrées de la liste."""
        self.mock_fs.setup_directory("/source", ["file1.txt", "file2.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.move_selection("/dest")
        
        self.assertNotIn("file1.txt", self.manager.get_entries())
        self.assertIn("file2.txt", self.manager.get_entries())
    
    def test_move_clears_selection(self):
        """Test: le déplacement vide la sélection."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.move_selection("/dest")
        
        self.assertEqual(self.manager.get_selection(), [])
    
    def test_move_with_random_destination(self):
        """Test: déplacement avec génération aléatoire du nom de destination."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_random.set_values(["grand", "montagne"])
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.move_selection()
        
        self.assertEqual(result, "/source/grand_montagne")
    
    def test_move_creates_destination_if_not_exists(self):
        """Test: le déplacement crée le répertoire de destination s'il n'existe pas."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.move_selection("/new_dest")
        
        self.assertIn("/new_dest", self.mock_fs.created_directories)
    
    def test_move_multiple_files(self):
        """Test: déplacer plusieurs fichiers."""
        self.mock_fs.setup_directory("/source", ["file1.txt", "file2.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_fs.add_file("/source/file2.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        self.manager.select("file2.txt")
        
        self.manager.move_selection("/dest")
        
        self.assertEqual(len(self.mock_ops.moved_items), 2)
        self.assertEqual(self.manager.get_entries(), [])


class TestFileManagerDelete(unittest.TestCase):
    """Tests pour la suppression de fichiers."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_delete_single_file(self):
        """Test: supprimer un fichier."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.delete_selection()
        
        self.assertIn("/source/file1.txt", self.mock_ops.deleted_files)
    
    def test_delete_directory(self):
        """Test: supprimer un répertoire."""
        self.mock_fs.setup_directory("/source", ["dir1"])
        self.mock_fs.add_directory("/source/dir1")
        self.manager.list_entries("/source")
        self.manager.select("dir1")
        
        self.manager.delete_selection()
        
        self.assertIn("/source/dir1", self.mock_ops.deleted_directories)
    
    def test_delete_removes_from_entries(self):
        """Test: la suppression retire les entrées de la liste."""
        self.mock_fs.setup_directory("/source", ["file1.txt", "file2.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.delete_selection()
        
        self.assertNotIn("file1.txt", self.manager.get_entries())
        self.assertIn("file2.txt", self.manager.get_entries())
    
    def test_delete_clears_selection(self):
        """Test: la suppression vide la sélection."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        self.manager.delete_selection()
        
        self.assertEqual(self.manager.get_selection(), [])
    
    def test_delete_multiple_items(self):
        """Test: supprimer plusieurs éléments."""
        self.mock_fs.setup_directory("/source", ["file1.txt", "dir1"])
        self.mock_fs.add_file("/source/file1.txt")
        self.mock_fs.add_directory("/source/dir1")
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        self.manager.select("dir1")
        
        self.manager.delete_selection()
        
        self.assertEqual(len(self.mock_ops.deleted_files), 1)
        self.assertEqual(len(self.mock_ops.deleted_directories), 1)
    
    def test_delete_empty_selection(self):
        """Test: supprimer une sélection vide."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.manager.list_entries("/source")
        
        self.manager.delete_selection()
        
        self.assertEqual(self.mock_ops.deleted_files, [])
        self.assertEqual(self.mock_ops.deleted_directories, [])


class TestFileManagerRandomNameGeneration(unittest.TestCase):
    """Tests pour la génération de noms aléatoires."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_random_name_format(self):
        """Test: le nom généré a le bon format (adjectif_nom)."""
        self.mock_random.set_values(["mysterieux", "foret"])
        
        name = self.manager._generate_random_name()
        
        self.assertEqual(name, "mysterieux_foret")
    
    def test_random_name_uses_dictionaries(self):
        """Test: la génération utilise les dictionnaires d'adjectifs et de noms."""
        self.mock_random.set_values(["brillant", "cascade"])
        
        self.manager._generate_random_name()
        
        self.assertEqual(len(self.mock_random.calls), 2)
        self.assertEqual(self.mock_random.calls[0], FileManager.ADJECTIVES)
        self.assertEqual(self.mock_random.calls[1], FileManager.NOUNS)
    
    def test_dictionaries_have_twenty_entries(self):
        """Test: les dictionnaires contiennent 20 entrées chacun."""
        self.assertEqual(len(FileManager.NOUNS), 20)
        self.assertEqual(len(FileManager.ADJECTIVES), 20)
    
    def test_dictionaries_have_no_special_characters(self):
        """Test: les dictionnaires ne contiennent pas de caractères spéciaux."""
        import re
        pattern = re.compile(r'^[a-zA-Z]+$')
        
        for noun in FileManager.NOUNS:
            self.assertTrue(pattern.match(noun), f"'{noun}' contient des caractères spéciaux")
        
        for adj in FileManager.ADJECTIVES:
            self.assertTrue(pattern.match(adj), f"'{adj}' contient des caractères spéciaux")


class TestFileManagerRandomRetry(unittest.TestCase):
    """Tests pour la répétition du tirage aléatoire si le répertoire existe."""
    
    def setUp(self):
        self.mock_fs = MockFilesystem()
        self.mock_ops = MockFileOperations()
        self.mock_random = MockRandomGenerator()
        self.manager = FileManager(
            filesystem=self.mock_fs,
            file_operations=self.mock_ops,
            random_generator=self.mock_random
        )
    
    def test_retry_if_directory_exists(self):
        """Test: retente le tirage si le répertoire existe déjà."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        # Le premier nom généré existe déjà
        self.mock_fs.add_directory("/source/beau_soleil")
        # Configurer les tirages: premier échoue, deuxième réussit
        self.mock_random.set_values(["beau", "soleil", "grand", "montagne"])
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection()
        
        self.assertEqual(result, "/source/grand_montagne")
    
    def test_retry_up_to_10_times(self):
        """Test: retente jusqu'à 10 fois maximum."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        # Les 9 premiers noms existent
        for i in range(9):
            self.mock_fs.add_directory(f"/source/nom{i}_test{i}")
        # Configurer 9 tirages qui échouent puis 1 qui réussit (10ème tentative)
        values = []
        for i in range(9):
            values.extend([f"nom{i}", f"test{i}"])
        values.extend(["libre", "chemin"])
        self.mock_random.set_values(values)
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection()
        
        self.assertEqual(result, "/source/libre_chemin")
    
    def test_add_number_after_10_retries(self):
        """Test: ajoute un numéro après 10 tentatives échouées."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        # Les 10 noms tirés existent tous
        for i in range(10):
            self.mock_fs.add_directory(f"/source/nom{i}_test{i}")
        # Configurer 10 tirages qui échouent tous
        values = []
        for i in range(10):
            values.extend([f"nom{i}", f"test{i}"])
        self.mock_random.set_values(values)
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection()
        
        # Le dernier nom tiré (nom9_test9) doit être numéroté
        self.assertEqual(result, "/source/nom9_test9_1")
    
    def test_increment_number_until_unique(self):
        """Test: incrémente le numéro jusqu'à trouver un nom unique."""
        self.mock_fs.setup_directory("/source", ["file1.txt"])
        self.mock_fs.add_file("/source/file1.txt")
        # Les 10 noms existent + versions numérotées
        for i in range(10):
            self.mock_fs.add_directory(f"/source/nom{i}_test{i}")
        self.mock_fs.add_directory("/source/nom9_test9_1")
        self.mock_fs.add_directory("/source/nom9_test9_2")
        # Configurer 10 tirages
        values = []
        for i in range(10):
            values.extend([f"nom{i}", f"test{i}"])
        self.mock_random.set_values(values)
        self.manager.list_entries("/source")
        self.manager.select("file1.txt")
        
        result = self.manager.copy_selection()
        
        self.assertEqual(result, "/source/nom9_test9_3")


if __name__ == "__main__":
    unittest.main()
