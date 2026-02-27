from database import SessionLocal
from services.parser import parse_price_list

with open('../tests/supplier_1.csv', 'rb') as f:
    data = f.read()
    records = parse_price_list(data, 'supplier_1.csv', 'Test Supplier')
    print(f'Successfully parsed {len(records)} records from CSV')
    for r in records:
        print(r)
