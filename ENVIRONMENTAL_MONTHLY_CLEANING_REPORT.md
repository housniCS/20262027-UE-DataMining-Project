# Rapport de Nettoyage des Données : `environmental_monthly.csv`

**Fichier cible** : [`data/ecology/environmental_monthly.csv`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/data/ecology/environmental_monthly.csv)  
**Script automatisé** : [`mining_scripts/clean_environmental_monthly.py`](file:///c:/Users/hi/code/data_mining/20262027-UE-DataMining-Project/mining_scripts/clean_environmental_monthly.py)  
**Date d'exécution** : 15 Septembre 2026  

---

## 1. Vue d'ensemble et métriques

| Métrique | Avant nettoyage | Après nettoyage | Différence / Action |
| :--- | :--- | :--- | :--- |
| **Nombre de lignes** | 4 994 | 4 992 | -2 doublons stricts supprimés |
| **Nombre de colonnes** | 11 | 11 | Inchangé |
| **Doublons exacts** | 2 | 0 | Nettoyés |
| **Valeurs manquantes (`vegetation_cover_pct`)** | 10 | 0 | Imputées par interpolation temporelle intra-site |
| **Valeurs manquantes (`pesticide_index`)** | 15 | 0 | Imputées par interpolation temporelle intra-site |
| **Valeurs manquantes (`weather_exception_code`)** | 4 790 (`NaN`) | 0 | Standardisées en catégorie `'NONE'` |
| **Typage numérique strict** | Variables polluées en `object` | `float64` strict | Unités (`C`, `mm`) et virgules nettoyées |

---

## 2. Problèmes identifiés et corrections appliquées

### A. Dédoublonnage strict
- **Constat** : 2 lignes étaient dupliquées à la fin du fichier pour le site `AVL-NMQ` aux mois `2023-10-01` et `2023-11-01`.
- **Correction** : Suppression des 2 doublons redondants, ramenant le dataset à 4 992 observations mensuelles uniques (exactement 78 mois par site sur les 64 sites).

---

### B. Harmonisation de la casse (`land_use_category`)
- **Constat** : Présence de valeurs avec casses hétérogènes (`Karst_Habitat`, `DEGRADED_LAND`, etc.).
- **Correction** : Conversion uniforme en minuscules (`strip().lower()`) pour obtenir des catégories homogènes :
  - `mixed_forest`, `coastal_habitat`, `durian_orchard`, `karst_habitat`, `research_site`, `mixed_agriculture`, `protected_forest`, `degraded_land`.

---

### C. Nettoyage des colonnes physiques polluées par du texte et des virgules
- **Constat** :
  - `mean_temperature_c` : présence du suffixe `" C"` (ex. `"25.86 C"`) et de séparateurs décimaux à virgule (ex. `"23,81"`).
  - `rainfall_mm` : présence du suffixe `" mm"` (ex. `"251.3 mm"`) et de virgules décimales (ex. `"201,4"`).
  - `mean_humidity_pct` : présence de virgules décimales (ex. `"74,8"`).
- **Correction** :
  - Suppression automatique des suffixes `" C"` et `" mm"`.
  - Remplacement de toutes les virgules par des points.
  - Typage strict en `float64` arrondi à 2 décimales.

---

### D. Imputation des séries chronologiques (`vegetation_cover_pct` et `pesticide_index`)
- **Constat** : 
  - 10 valeurs manquantes dans `vegetation_cover_pct`.
  - 15 valeurs manquantes dans `pesticide_index`.
- **Méthode adoptée** :
  - Comme chaque site dispose d'une série temporelle mensuelle continue de 2019 à 2025, une moyenne globale aurait masqué les spécificités locales et saisonnières.
  - L'imputation a été réalisée par **interpolation linéaire temporelle au sein de chaque site chronologiquement ordonné**, complétée par propagation avant/arrière (`bfill`/`ffill`) pour les éventuelles bornes.
  - Résultat : Continuité environnementale respectée sans rupture artificielle.

---

### E. Standardisation de `weather_exception_code`
- **Constat** : 4 790 valeurs étaient à `NaN` car la majorité des mois ne subissent pas d'aléa climatique extrême. Les seules anomalies répertoriées étaient `HEAVY_RAIN` (112) et `DRY_SPELL` (92).
- **Correction** : Remplacement des `NaN` par la modalité explicite `'NONE'`, ce qui élimine les cellules nulles tout en préservant le sens métier (aucun événement météo exceptionnel).

---

## 3. Schéma final des données

| Colonne | Type initial | Type final | Nulls restants | Description |
| :--- | :--- | :--- | :---: | :--- |
| `site_code` | `object` | `object` | 0 | Code identifiant le site (64 sites) |
| `reporting_month` | `object` | `object` (ISO) | 0 | Premier jour du mois de relevé (`YYYY-MM-DD`) |
| `mean_temperature_c` | `object` (pollué) | `float64` | 0 | Température moyenne mensuelle (°C) |
| `rainfall_mm` | `object` (pollué) | `float64` | 0 | Précipitations cumulées du mois (mm) |
| `mean_humidity_pct` | `object` (pollué) | `float64` | 0 | Humidité moyenne relative (%) |
| `vegetation_cover_pct` | `float64` (10 nuls) | `float64` | 0 | Couverture végétale moyenne (%) |
| `habitat_disturbance_index`| `float64` | `float64` | 0 | Indice de perturbation de l'habitat (0-100) |
| `pesticide_index` | `float64` (15 nuls) | `float64` | 0 | Indice d'exposition aux pesticides (0-100) |
| `land_use_category` | `object` (casses mixtes) | `object` | 0 | Type d'occupation du sol standardisé |
| `weather_exception_code` | `object` (4 790 nuls) | `object` | 0 | Code d'aléa météo (`NONE`, `HEAVY_RAIN`, `DRY_SPELL`) |
| `data_completeness_pct` | `float64` | `float64` | 0 | Taux d'exhaustivité des capteurs du site (%) |
