"""
check_pipeline.py
─────────────────────────────────────────────────────────────────────────────
Vérifie que tous les fichiers nécessaires existent et affiche leurs tailles.
Usage : python check_pipeline.py
─────────────────────────────────────────────────────────────────────────────
"""

import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = [
    ("data/BDD#7_Database_Albert_School_Sephora.csv", "CSV brut",            True),
    ("data/customer_features.csv",                    "Features complètes",  True),
    ("data/customer_features_train.csv",              "Features train",       True),
    ("data/transactions_test.csv",                    "Transactions test",    True),
    ("models/kmeans_model.pkl",                       "Modèle KMeans",        True),
    ("models/scaler.pkl",                             "Scaler",               True),
    ("outputs/data/migrations.csv",                   "Migrations",           True),
    ("outputs/data/personas_profiles.csv",            "Profils personas",     False),
    ("outputs/data/business_kpis.csv",                "KPIs business",        False),
    ("outputs/data/persona_cards.json",               "Cartes personas",      False),
]

OK, WARN, ERR = "✅", "⚠️ ", "❌"

def fmt_size(path):
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size/1024:.1f} KB"
    else:
        return f"{size/1024**2:.1f} MB"

def check_migrations_content(path):
    """Retourne le nombre de lignes (hors header)."""
    try:
        with open(path) as f:
            return sum(1 for _ in f) - 1
    except Exception:
        return -1

print("=" * 65)
print("  CHECK PIPELINE — Sephora Segmentation Dynamique | Groupe 5")
print("=" * 65)

all_ok = True
for rel_path, label, required in FILES:
    full_path = os.path.join(ROOT, rel_path)
    exists = os.path.exists(full_path)

    if exists:
        size = fmt_size(full_path)
        # Cas spécial : migrations.csv peut exister mais être vide
        if "migrations" in rel_path:
            n_rows = check_migrations_content(full_path)
            if n_rows == 0:
                icon = WARN
                note = f"⚠️  fichier vide ({size}) — re-run notebook 3"
                all_ok = False
            else:
                icon = OK
                note = f"{size} — {n_rows:,} migrations"
        else:
            icon = OK
            note = size
    else:
        icon = ERR if required else WARN
        note = "MANQUANT"
        if required:
            all_ok = False

    print(f"  {icon}  {label:<30} {note}")

print()

# Vérification IDs overlap
print("─" * 65)
print("  DIAGNOSTIC IDs clients (overlap features ↔ transactions)")
print("─" * 65)
try:
    import pandas as pd

    feat_path = os.path.join(ROOT, "data/customer_features_train.csv")
    txn_path  = os.path.join(ROOT, "data/transactions_test.csv")

    if os.path.exists(feat_path) and os.path.exists(txn_path):
        feat_ids = set(
            pd.read_csv(feat_path, dtype={"anonymized_card_code": str},
                        usecols=["anonymized_card_code"])["anonymized_card_code"].str.strip()
        )
        txn_ids = set(
            pd.read_csv(txn_path, dtype={"anonymized_card_code": str},
                        usecols=["anonymized_card_code"])["anonymized_card_code"].str.strip()
        )
        overlap = len(feat_ids & txn_ids)
        pct = overlap / len(txn_ids) * 100 if txn_ids else 0
        icon = OK if overlap > 0 else ERR
        print(f"  {icon}  Clients features : {len(feat_ids):,}")
        print(f"  {icon}  Clients test     : {len(txn_ids):,}")
        print(f"  {icon}  Overlap          : {overlap:,} ({pct:.1f}%)")
        if overlap == 0:
            print()
            print("  ❌ PROBLÈME : les IDs ne se correspondent pas.")
            print("     → Vérifier que customer_features_train.csv a été généré")
            print("       avec dtype={'anonymized_card_code': str} dans notebook 0.")
            all_ok = False
    else:
        print(f"  {WARN}  Fichiers manquants — skip diagnostic IDs")

except ImportError:
    print(f"  {WARN}  pandas non disponible — skip diagnostic IDs")

print()
print("=" * 65)
if all_ok:
    print("  ✅  Pipeline complet — prêt à lancer le dashboard")
    print("      streamlit run app/dashboard.py")
else:
    print("  ❌  Problèmes détectés — voir les erreurs ci-dessus")
    print()
    print("  Ordre d'exécution :")
    print("    1. notebook 0  → génère data/customer_features_train.csv")
    print("    2. notebook 2  → génère models/kmeans_model.pkl")
    print("    3. notebook 3  → génère outputs/data/migrations.csv")
print("=" * 65)

sys.exit(0 if all_ok else 1)
