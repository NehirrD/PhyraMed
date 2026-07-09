import pandas as pd
import requests

BASE_URL = "http://127.0.0.1:8000"

def seed_database(excel_file_path):
    print("🚀 Veritabanı tohumlama (Seed) işlemi başlatılıyor...\n")
    
    categories_df = pd.read_excel(excel_file_path, sheet_name='Categories')
    products_df = pd.read_excel(excel_file_path, sheet_name='ProductClaims')
    sources_df = pd.read_excel(excel_file_path, sheet_name='Sources')

    categories_df = categories_df.astype(object).where(pd.notnull(categories_df), None)
    products_df = products_df.astype(object).where(pd.notnull(products_df), None)
    sources_df = sources_df.astype(object).where(pd.notnull(sources_df), None)

    print("1️⃣ Kategoriler veritabanına işleniyor...")
    category_id_map = {}

    for index, row in categories_df.iterrows():
        cat_payload = {
            "name": row['category_name'],
            "description": row['description']
        }
        
        response = requests.post(f"{BASE_URL}/category/", json=cat_payload)
        if response.status_code in [200, 201]:
            category_id_map[row['category_id']] = response.json()['id']
            print(f"  ✅ Kategori eklendi: {row['category_name']}")

    print("\n2️⃣ Ürünler ve riskler işleniyor...")

    claim_id_to_db_product_id_map = {} 
    
    evidence_map = {"Yüksek": "HIGH", "Orta": "MIDDLE", "Düşük": "LOW", "Bekliyor": "PENDING"}

    for index, row in products_df.iterrows():
        db_category_id = category_id_map.get(row['category_id'])
        if not db_category_id: continue

        raw_level = str(row['evidence_level']).strip() if row.get('evidence_level') else None
        
        product_payload = {
            "name": row['product_name_tr'],
            "usage_purpose": row['usage_purpose'],
            "evidence_level": evidence_map.get(raw_level, None),
            "evidence_summary": row['evidence_summary'], 
            "category_id": db_category_id
        }

        prod_res = requests.post(f"{BASE_URL}/product/", json=product_payload)
        
        if prod_res.status_code in [200, 201]:
            db_product_id = prod_res.json()['id']
            print(f"  ✅ Ürün: {row['product_name_tr']}")

        
            if row.get('claim_id'):
                claim_id_to_db_product_id_map[row['claim_id']] = db_product_id

            if row.get('risk_summary'):
                requests.post(f"{BASE_URL}/risk/", json={"description": row['risk_summary'], "severity": "Orta", "product_id": db_product_id})

            if row.get('interaction_summary'):
                requests.post(f"{BASE_URL}/interaction/", json={"description": row['interaction_summary'], "product_id": db_product_id})

    print("\n3️⃣ Bilimsel kaynaklar (Sources) veritabanına işleniyor...")
    for index, row in sources_df.iterrows():
    
        excel_claim_id = row.get('claim_id')
        
        
        db_product_id = claim_id_to_db_product_id_map.get(excel_claim_id)

        if db_product_id:
            source_payload = {
                "title": row.get('title') or "Bilimsel Kaynak",
                "type": row.get('source_type') or "Makale",
                "url": row.get('url') or "https://phyramed.com",
                "product_id": db_product_id
            }
            
            source_res = requests.post(f"{BASE_URL}/source/", json=source_payload)
            if source_res.status_code in [200, 201]:
                print(f"  ✅ Kaynak eklendi: {source_payload['title'][:30]}...")
            else:
                print(f"  ❌ Kaynak Hatası: {source_res.text}")
        else:
            print(f"  ⚠️ Pas Geçildi: {excel_claim_id} eşleşmedi.")

    print("\n🎉 Tüm tohumlama işlemi tamamlandı!")

if __name__ == "__main__":
    seed_database("dataset.xlsx")