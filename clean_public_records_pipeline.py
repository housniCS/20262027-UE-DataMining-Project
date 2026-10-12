"""
================================================================================
SCRIPT AUTOMATISÉ DE NETTOYAGE DES DONNÉES (MODIFICATION EN PLACE - IN-PLACE)
Projet : Regional Public Facilities, Personnel, and Institutional Directory
Objectif : Modifier et écraser directement les fichiers CSV d'origine (sur place)
           sans créer de fichiers ni de dossiers supplémentaires.
================================================================================
"""

import os
import re
import pandas as pd
import numpy as np

# Répertoire contenant les fichiers CSV à modifier directement sur place
# (Par défaut, le dossier courant '.' ou le dossier où se trouvent vos fichiers CSV)
DATA_DIR = "./data/public_records/"

def clean_whitespace(val):
    """
    Supprime les espaces en début/fin de chaîne et réduit les espaces multiples 
    internes à un seul espace. Préserve les valeurs NULL/NaN.
    """
    if pd.isna(val) or not isinstance(val, str):
        return val
    return re.sub(r'\s+', ' ', val).strip()

def parse_date_custom(val):
    """
    Normalise les dates vers le format ISO (YYYY-MM-DD), en gérant les mélanges 
    de formats (ISO, slashes YYYY/MM/DD ou DD/MM/YYYY, etc.).
    """
    if pd.isna(val) or val == '' or str(val).strip() == '':
        return np.nan
    val_str = str(val).strip()
    try:
        dt = pd.to_datetime(val_str, format='mixed', dayfirst=False)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        try:
            dt = pd.to_datetime(val_str, dayfirst=True)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return val_str

def parse_datetime_custom(val):
    """
    Normalise les horodatages vers le format ISO 8601 (YYYY-MM-DDTHH:MM:SS).
    """
    if pd.isna(val) or val == '' or str(val).strip() == '':
        return np.nan
    val_str = str(val).strip()
    try:
        dt = pd.to_datetime(val_str, format='mixed')
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return val_str

def parse_birth_year_range(val):
    """
    Parse les plages d'années de naissance (ex: '1920–1929') ou années simples 
    en deux bornes numériques (min, max).
    """
    if pd.isna(val):
        return np.nan, np.nan
    val_str = str(val).strip()
    if '–' in val_str or '-' in val_str:
        parts = re.split(r'[–-]', val_str)
        try:
            return int(parts[0]), int(parts[1])
        except Exception:
            return np.nan, np.nan
    else:
        try:
            yr = int(val_str)
            return yr, yr
        except Exception:
            return np.nan, np.nan

def extract_title(name):
    """
    Sépare les titres civiques/médicaux (Dr., Prof., etc.) du nom de famille.
    """
    if pd.isna(name):
        return np.nan, name
    match = re.match(r'^(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+(.*)$', name)
    if match:
        return match.group(1), match.group(2)
    return np.nan, name


def run_pipeline(data_dir=DATA_DIR):
    print(f">>> Démarrage du nettoyage en place sur les fichiers dans '{data_dir}'...")

    # 1. INSTITUTIONAL_MEMOS.CSV
    path_memos = os.path.join(data_dir, "institutional_memos.csv")
    if os.path.exists(path_memos):
        df_memos = pd.read_csv(path_memos)
        for col in df_memos.select_dtypes(include=['object']).columns:
            df_memos[col] = df_memos[col].apply(clean_whitespace)
        df_memos['document_date'] = df_memos['document_date'].apply(parse_date_custom)
        df_memos['has_purchase_order'] = df_memos['related_purchase_order'].notna()
        df_memos['has_shipment'] = df_memos['related_shipment_number'].notna()
        df_memos['has_case'] = df_memos['related_case_number'].notna()
        df_memos.to_csv(path_memos, index=False)
        print(" -> institutional_memos.csv modifié en place.")

    # 2. LICENSED_FACILITIES.CSV
    path_fac = os.path.join(data_dir, "licensed_facilities.csv")
    if os.path.exists(path_fac):
        df_fac = pd.read_csv(path_fac)
        for col in df_fac.select_dtypes(include=['object']).columns:
            df_fac[col] = df_fac[col].apply(clean_whitespace)
        df_fac['license_start'] = df_fac['license_start'].apply(parse_date_custom)
        df_fac['declared_services'] = df_fac['declared_services'].apply(
            lambda x: "; ".join([s.strip() for s in x.split(";")]) if pd.notna(x) else x
        )
        df_fac.to_csv(path_fac, index=False)
        print(" -> licensed_facilities.csv modifié en place.")

    # 3. LICENSED_PROFESSIONALS.CSV
    path_prof = os.path.join(data_dir, "licensed_professionals.csv")
    if os.path.exists(path_prof):
        df_prof = pd.read_csv(path_prof)
        if 'license_expiry_date' in df_prof.columns and df_prof['license_expiry_date'].isna().all():
            df_prof.drop(columns=['license_expiry_date'], inplace=True)
        for col in df_prof.select_dtypes(include=['object']).columns:
            df_prof[col] = df_prof[col].apply(clean_whitespace)
        df_prof['license_issue_date'] = df_prof['license_issue_date'].apply(parse_date_custom)
        df_prof['title'], df_prof['professional_name_clean'] = zip(*df_prof['professional_name'].apply(extract_title))
        df_prof['primary_facility_license_filled'] = df_prof['primary_facility_license'].fillna('NON_RATTACHE')
        df_prof.to_csv(path_prof, index=False)
        print(" -> licensed_professionals.csv modifié en place.")

    # 4. OFFICER_FILINGS.CSV
    path_off = os.path.join(data_dir, "officer_filings.csv")
    if os.path.exists(path_off):
        df_off = pd.read_csv(path_off)
        df_off.drop_duplicates(inplace=True)
        for col in df_off.select_dtypes(include=['object']).columns:
            df_off[col] = df_off[col].apply(clean_whitespace)
        for date_col in ['appointment_date', 'cessation_date', 'filing_date']:
            df_off[date_col] = df_off[date_col].apply(parse_date_custom)
        df_off['birth_year_min'], df_off['birth_year_max'] = zip(*df_off['birth_year_or_age_band'].apply(parse_birth_year_range))
        df_off['is_active_officer'] = df_off['cessation_date'].isna()
        df_off.to_csv(path_off, index=False)
        print(" -> officer_filings.csv modifié en place.")

    # 5. PUBLIC_AND_INVESTIGATIVE_DOCUMENTS.CSV
    path_docs = os.path.join(data_dir, "public_and_investigative_documents.csv")
    if os.path.exists(path_docs):
        df_docs = pd.read_csv(path_docs)
        for col in df_docs.select_dtypes(include=['object']).columns:
            df_docs[col] = df_docs[col].apply(clean_whitespace)
        df_docs['document_date'] = df_docs['document_date'].apply(parse_date_custom)
        df_docs['author_name'] = df_docs['author_name'].fillna('Inconnu')
        df_docs.to_csv(path_docs, index=False)
        print(" -> public_and_investigative_documents.csv modifié en place.")

    # 6. PUBLIC_APPOINTMENTS.CSV
    path_app = os.path.join(data_dir, "public_appointments.csv")
    if os.path.exists(path_app):
        df_app = pd.read_csv(path_app)
        for col in df_app.select_dtypes(include=['object']).columns:
            df_app[col] = df_app[col].apply(clean_whitespace)
        df_app['appointment_start'] = df_app['appointment_start'].apply(parse_date_custom)
        df_app['appointment_end'] = df_app['appointment_end'].apply(parse_date_custom)
        df_app['recorded_birth_year'] = df_app['recorded_birth_year'].astype('Int64')
        df_app['is_active_appointment'] = df_app['appointment_end'].isna()
        df_app.to_csv(path_app, index=False)
        print(" -> public_appointments.csv modifié en place.")

    # 7, 8, 9. REGISTERED_ENTITIES, REGULATORY_CASE_EVENTS, SITE_ACCESS_CASE_EVENTS
    path_reg = os.path.join(data_dir, "registered_entities.csv")
    path_case = os.path.join(data_dir, "regulatory_case_events.csv")
    path_site = os.path.join(data_dir, "site_access_case_events.csv")

    if os.path.exists(path_reg) and os.path.exists(path_case) and os.path.exists(path_site):
        df_reg = pd.read_csv(path_reg)
        if 'parent_registration_number' in df_reg.columns and df_reg['parent_registration_number'].isna().all():
            df_reg.drop(columns=['parent_registration_number'], inplace=True)
        for col in df_reg.select_dtypes(include=['object']).columns:
            df_reg[col] = df_reg[col].apply(clean_whitespace)
        df_reg['registration_date'] = df_reg['registration_date'].apply(parse_date_custom)
        df_reg['last_filing_date'] = df_reg['last_filing_date'].apply(parse_date_custom)
        df_reg['is_dummy_record'] = False

        df_case = pd.read_csv(path_case)
        df_case.drop_duplicates(inplace=True)
        for col in df_case.select_dtypes(include=['object']).columns:
            df_case[col] = df_case[col].apply(clean_whitespace)
        df_case['event_time'] = df_case['event_time'].apply(parse_datetime_custom)
        df_case['is_registered_entity'] = df_case['subject_registration_number'].notna()
        df_case['subject_registration_number_filled'] = df_case['subject_registration_number'].fillna('NON_IMMATRICULE')

        df_site = pd.read_csv(path_site)
        df_site.drop_duplicates(inplace=True)
        for col in df_site.select_dtypes(include=['object']).columns:
            df_site[col] = df_site[col].apply(clean_whitespace)
        df_site['event_time'] = df_site['event_time'].apply(parse_datetime_custom)
        df_site['is_registered_entity'] = df_site['requesting_registration_number'].notna()
        df_site['requesting_registration_number_filled'] = df_site['requesting_registration_number'].fillna('NON_IMMATRICULE')

        # Intégrité référentielle
        existing_regs = set(df_reg['registration_number'].dropna())
        orphan_case_regs = set(df_case['subject_registration_number'].dropna()) - existing_regs
        orphan_site_regs = set(df_site['requesting_registration_number'].dropna()) - existing_regs
        all_orphans = sorted(list(orphan_case_regs.union(orphan_site_regs)))

        dummy_rows = []
        for orphan_id in all_orphans:
            dummy_rows.append({
                'registration_number': orphan_id,
                'legal_name': f'Entité non immatriculée ({orphan_id})',
                'registered_entity_type': 'Inconnu',
                'registration_date': np.nan,
                'current_status': 'non_enregistre',
                'registered_address': 'Inconnu',
                'jurisdiction': 'Inconnu',
                'declared_activity': 'Inconnu',
                'last_filing_date': np.nan,
                'is_dummy_record': True
            })

        df_reg_extended = pd.concat([df_reg, pd.DataFrame(dummy_rows)], ignore_index=True)

        # Ecrasement en place des fichiers
        df_reg_extended.to_csv(path_reg, index=False)
        df_case.to_csv(path_case, index=False)
        df_site.to_csv(path_site, index=False)
        print(" -> registered_entities.csv, regulatory_case_events.csv et site_access_case_events.csv modifiés en place.")

    print(">>> Tous les fichiers ont été modifiés directement sur place avec succès !")

if __name__ == '__main__':
    run_pipeline()
