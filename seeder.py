import pandas as pd
import numpy as np
import requests

BASE_URL = "http://127.0.0.1:8000"

def seed_database(excel_file_path):
    print("🚀 Veritabanı tohumlama (Seed) işlemi başlatılıyor...\n")
    
    categories_df = pd.read_excel(excel_file_path, sheet_name='Categories')
    products_df = pd.read_excel(excel_file_path, sheet_name='ProductClaims')

    # KRİTİK DÜZELTME: Tüm boş hücreleri (NaN) kesin olarak None'a çeviren zırh
    categories_df = categories_df.astype(object).where(pd.notnull(categories_df), None)
    products_df = products_df.astype(object).where(pd.notnull(products_df), None)

    print("1️⃣ Kategoriler veritabanına işleniyor...")
    category_id_map = {}

    for index, row in categories_df.iterrows():
        cat_payload = {
            "name": row['category_name'],
            "description": row['description']
        }
        
        response = requests.post(f"{BASE_URL}/category/", json=cat_payload)
        
        if response.status_code in [200, 201]:
            created_category = response.json()
            category_id_map[row['category_id']] = created_category['id']
            print(f"  ✅ Kategori eklendi: {row['category_name']}")
        else:
            print(f"  ❌ HATA (Kategori): {row['category_name']} -> {response.text}")

    print("\n2️⃣ Ürünler ve ilişkili risk/etkileşim verileri işleniyor...")
    
    # Türkçe Enum Çevirmeni
    evidence_map = {
        "Yüksek": "HIGH",
        "Orta": "MIDDLE",
        "Düşük": "LOW"
    }

    for index, row in products_df.iterrows():
        db_category_id = category_id_map.get(row['category_id'])
        
        if not db_category_id:
            continue

        # Gelen kanıt seviyesini temizle ve çevir (Boşsa veya Bekliyorsa None yap)
        raw_level = str(row['evidence_level']).strip() if row['evidence_level'] else None
        mapped_level = evidence_map.get(raw_level, None)

        # --- ÜRÜN (PRODUCT) PAKETİ ---
        product_payload = {
            "name": row['product_name_tr'],
            "usage_purpose": row['usage_purpose'],
            "evidence_level": mapped_level,
            "category_id": db_category_id
        }

        prod_response = requests.post(f"{BASE_URL}/product/", json=product_payload)
        
        if prod_response.status_code in [200, 201]:
            created_product = prod_response.json()
            db_product_id = created_product['id']
            print(f"  ✅ Ürün eklendi: {row['product_name_tr']}")

            # --- RİSK PAKETİ ---
            if row['risk_summary']:
                risk_payload = {
                    "description": row['risk_summary'],
                    "product_id": db_product_id
                }
                # Nehir /risk ucunu açtığında çalışması için buraya bir try-except koyduk
                try: requests.post(f"{BASE_URL}/risk/", json=risk_payload)
                except: pass

            # --- ETKİLEŞİM PAKETİ ---
            if row['interaction_summary']:
                interaction_payload = {
                    "description": row['interaction_summary'],
                    "product_id": db_product_id
                }
                # Nehir /interaction ucunu açtığında çalışması için try-except
                try: requests.post(f"{BASE_URL}/interaction/", json=interaction_payload)
                except: pass
        else:
             print(f"  ❌ HATA (Ürün): {row['product_name_tr']} -> {prod_response.text}")

    print("\n🎉 Tüm tohumlama işlemi tamamlandı!")

if __name__ == "__main__":
    seed_database("dataset.xlsx")