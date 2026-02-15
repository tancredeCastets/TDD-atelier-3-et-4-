# API de Gestion de Fichiers - Atelier ATDD

API Flask pour la manipulation de fichiers, développée en suivant l'approche ATDD (Acceptance Test Driven Development).

## Installation

```bash
pip install -r requirements.txt
```

## Lancement de l'API

```bash
python app.py
```

L'API sera disponible sur `http://localhost:5000`.

## Endpoints de l'API

### 1. Liste des fichiers

**GET** `/api/files?path=<chemin>`

Liste les fichiers et répertoires d'un chemin donné.

**Réponse:**
```json
{
  "path": "/chemin/vers/repertoire",
  "entries": [
    {"name": "fichier.txt", "type": "file"},
    {"name": "dossier", "type": "directory"}
  ]
}
```

### 2. Gestion de la sélection

**GET** `/api/selection`

Récupère la sélection actuelle.

**POST** `/api/selection`

Modifie la sélection.

**Actions disponibles:**
- `select`: Sélectionne une entrée
- `deselect`: Désélectionne une entrée
- `select_all`: Sélectionne toutes les entrées
- `deselect_all`: Désélectionne toutes les entrées

**Exemple:**
```json
{
  "action": "select",
  "entry": "fichier.txt"
}
```

### 3. Suppression de fichiers

**DELETE** `/api/files/delete`

Supprime les fichiers et répertoires sélectionnés.

**Réponse:**
```json
{
  "success": true,
  "deleted_count": 2,
  "errors": []
}
```

## Tests

Exécuter les tests fonctionnels ATDD :

```bash
pytest test_api_functional.py -v
```

Exécuter tous les tests :

```bash
pytest -v
```

## Historique des commits ATDD

1. **RED**: Premier test ATDD - Liste des fichiers
2. **GREEN**: Implémentation endpoint `/api/files`
3. **RED**: Tests ATDD pour exploration et sélection
4. **GREEN**: Implémentation endpoint `/api/selection`
5. **RED**: Tests ATDD pour opération de suppression
6. **GREEN**: Implémentation endpoint DELETE `/api/files/delete`
7. **REFACTOR**: Finalisation et documentation
