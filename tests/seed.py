import os
import sys

# Add backend directory to module search path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from database import SessionLocal, engine, Base
from models import MasterItem
import pandas as pd

Base.metadata.create_all(bind=engine)

def seed_master_items():
    db = SessionLocal()
    
    # Let's clean it first for testing
    db.query(MasterItem).delete()
    
    items = [
        MasterItem(barcode="4601234567890", article="ART-001", name="Смартфон Samsung Galaxy S23 Ultra 256GB Black", code_1c="0000000001"),
        MasterItem(barcode="4601234567891", article="ART-002", name="Ноутбук Apple MacBook Air 13 M2 8/256", code_1c="0000000002"),
        MasterItem(barcode="4601234567892", article="ART-003", name="Беспроводные наушники Sony WH-1000XM5", code_1c="0000000003"),
        MasterItem(barcode="4601234567893", article="ART-004", name="Игровая консоль Sony PlayStation 5", code_1c="0000000004"),
        MasterItem(barcode="4601234567894", article="ART-005", name="Умная колонка Яндекс Станция Макс (с Zigbee)", code_1c="0000000005"),
        MasterItem(barcode="1111111111111", article="ART-006", name="Телевизор LG OLED 55 C1", code_1c="0000000006")
    ]
    
    db.add_all(items)
    db.commit()
    db.close()
    print("Seeded 6 MasterItems into Nomenclature.")

def create_supplier_csv():
    # Mix of exact, fuzzy and unmatched data
    data = {
        "Штрихкод": ["4601234567890", "", "4601234567892", "", "", "9999999999999"],
        "Артикул": ["", "ART-002", "", "", "UNKNOWN-ART", ""],
        "Наименование": [
            "Samsung Galaxy S23 Ultra 256GB Black", # Match by barcode
            "Ноутбук Apple MacBook Air 13",         # Match by article
            "Наушники беспроводные Sony XM5",       # Match by barcode
            "Игровая приставка Sony PS5",           # Fuzzy match (should require manual if conf low, or auto match)
            "Яндекс Станция Макс умная колонка",    # Fuzzy match
            "Неизвестный товар которого нет в 1С"   # No match
        ],
        "Цена": [100000, 115000, 28000, 55000, 29000, 999]
    }
    
    df = pd.DataFrame(data)
    os.makedirs('tests', exist_ok=True)
    df.to_csv('tests/supplier_1.csv', index=False, sep=';')
    print("Created tests/supplier_1.csv")
    
if __name__ == "__main__":
    seed_master_items()
    create_supplier_csv()
