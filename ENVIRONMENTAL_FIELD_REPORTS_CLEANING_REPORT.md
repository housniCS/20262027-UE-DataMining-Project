# Rapport de Nettoyage des Données : `environmental_field_reports.csv`

**Fichier cible** : [`data/ecology/environmental_field_reports.csv`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/data/ecology/environmental_field_reports.csv)  
**Script automatisé** : [`mining_scripts/clean_environmental_field_reports.py`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/mining_scripts/clean_environmental_field_reports.py)  
**Date d'exécution** : 15 Septembre 2026  

---

## 1. Vue d'ensemble et métriques

| Métrique | Avant nettoyage | Après nettoyage | Différence / Action |
| :--- | :--- | :--- | :--- |
| **Nombre de lignes** | 30 | 30 | Intact (aucun doublon détecté) |
| **Nombre de colonnes** | 12 | 12 | Inchangé |
| **Valeurs nulles totales** | 1 (`author_name`) | 0 | Imputation explicite (`Uncredited`) |
| **Intégrité référentielle** | 100% valide | 100% valide | Vérifiée avec `bat_surveys`, `monitoring_sites` et `devices` |
| **Format des dates** | `YYYY-MM-DD` | `YYYY-MM-DD` | Standard ISO strict validé |
| **Normalisation des retours à la ligne** | Windows CRLF (`\r\n`) | LF standard (`\n`) | Harmonisation multi-plateforme |

---

## 2. Problèmes identifiés et corrections appliquées

### A. Absence de doublons
- **Constat** : Les 30 identifiants de documents (`EFR-510003` à `EFR-510130`) sont uniques.
- **Action** : Aucune ligne superflue à supprimer.

---

### B. Gestion de la valeur manquante dans `author_name`
- **Constat** : La ligne 23 (document `EFR-510012`) présentait une cellule vide (`NaN`) pour la colonne `author_name`.
  - Organisme émetteur : *Threshold Earth Observatory*
  - Type de document : *sensor_quality_report*
  - Titre : *Sensor Quality Review 49*
- **Analyse** : Les rapports de contrôle qualité de capteurs émis par cette organisation sont parfois institutionnels plutôt que signés nominativement par un chercheur individuel.
- **Correction** : Remplacement du `NaN` par la mention explicite standardisée **`"Uncredited"`**, garantissant 0 cellule vide tout en évitant d'inventer une fausse identité d'auteur.

---

### C. Validation de l'intégrité référentielle (Clés étrangères)
- **`site_code`** : Les 30 sites mentionnés existent tous dans [`monitoring_sites.csv`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/data/ecology/monitoring_sites.csv).
- **`related_survey_id`** : Les identifiants d'inventaires (ex. `BAT-0001814`) correspondent tous à des missions réelles et valides de [`bat_surveys.csv`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/data/ecology/bat_surveys.csv).
- **`related_device_reference`** : Les balises (ex. `DEV-KNTVXR-2`) existent toutes dans [`monitoring_device_operations.csv`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/data/ecology/monitoring_device_operations.csv).

---

### D. Standardisation du texte et des fins de ligne
- **Constat** : Le champ textuel `text` contenait des sauts de ligne avec encodage Windows `\r\n`.
- **Correction** : Normalisation en `\n` pour une portabilité optimale entre Linux, macOS et Windows lors de l'extraction NLP.

---

## 3. Schéma final des données

| Colonne | Type | Valeurs nulles | Description |
| :--- | :--- | :---: | :--- |
| `document_id` | `object` | 0 | Identifiant unique du rapport (ex: `EFR-510088`) |
| `site_code` | `object` | 0 | Code site de rattachement (ex: `KNT-KES`) |
| `document_date` | `object` (date ISO) | 0 | Date de publication (`YYYY-MM-DD`) |
| `document_type` | `object` | 0 | Type (`sensor_quality_report`, `ecological_incident_report`, etc.) |
| `author_name` | `object` | 0 | Auteur du rapport (`Uncredited` pour les rapports institutionnels) |
| `author_organization` | `object` | 0 | Organisation émettrice |
| `reporting_period` | `object` | 0 | Mois de référence (`YYYY-MM`) |
| `title` | `object` | 0 | Titre du rapport de terrain |
| `text` | `object` | 0 | Contenu textuel normalisé |
| `related_survey_id` | `object` | 0 | Référence à l'inventaire chauves-souris lié |
| `related_device_reference` | `object` | 0 | Référence au capteur lié |
| `publication_status` | `object` | 0 | Statut de diffusion (`restricted`, `public`, `internal`) |
