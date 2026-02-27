from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import engine, get_db
from models import MasterItem, SupplierItem, Base
from services.parser import parse_price_list
from services.matcher import match_supplier_items
from services.export import generate_1c_export_csv, generate_1c_export_xml

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nomenklatura Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/master-items/")
def get_master_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch the reference nomenclature."""
    return db.query(MasterItem).offset(skip).limit(limit).all()


@app.post("/api/upload/")
async def upload_supplier_price(
    supplier_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads a price list, parses it and saves unmatched items to DB."""
    contents = await file.read()
    
    try:
        records = parse_price_list(contents, file.filename, supplier_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    db_items = []
    for record in records:
        db_item = SupplierItem(
            supplier_name=supplier_name,
            name=record['name'],
            barcode=record['barcode'],
            article=record['article'],
            price=record['price']
        )
        db_items.append(db_item)
        
    db.add_all(db_items)
    db.commit()
    
    return {"message": f"Successfully parsed and saved {len(db_items)} items from {file.filename}"}


@app.post("/api/match/")
def run_matching(db: Session = Depends(get_db)):
    """Triggers the matching logic for all currently unmatched supplier items."""
    result = match_supplier_items(db)
    return {"message": "Matching run completed", **result}


@app.get("/api/results/")
def get_results(
    status: Optional[str] = None, # "matched", "unmatched"
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Returns the matching results."""
    query = db.query(SupplierItem)
    if status == "matched":
        query = query.filter(SupplierItem.is_matched == True)
    elif status == "unmatched":
        query = query.filter(SupplierItem.is_matched == False)
        
    # Join with MasterItem to return the matched item details
    items = query.offset(skip).limit(limit).all()
    
    # Format response
    response_items = []
    for item in items:
        resp = {
            "id": item.id,
            "supplier_name": item.supplier_name,
            "name": item.name,
            "barcode": item.barcode,
            "article": item.article,
            "price": item.price,
            "is_matched": item.is_matched,
            "match_confidence": item.match_confidence,
            "match_type": item.match_type
        }
        if item.is_matched and item.matched_master_id:
            master = db.query(MasterItem).filter(MasterItem.id == item.matched_master_id).first()
            if master:
                resp["master_item"] = {
                    "id": master.id,
                    "name": master.name,
                    "barcode": master.barcode,
                    "article": master.article,
                    "code_1c": master.code_1c
                }
        response_items.append(resp)
        
    return response_items

@app.post("/api/manual-match/{supplier_item_id}")
def manual_match(supplier_item_id: int, master_item_id: int, db: Session = Depends(get_db)):
    """API to handle manual matching reviews by user"""
    s_item = db.query(SupplierItem).filter(SupplierItem.id == supplier_item_id).first()
    if not s_item:
        raise HTTPException(status_code=404, detail="Supplier item not found")
        
    m_item = db.query(MasterItem).filter(MasterItem.id == master_item_id).first()
    if not m_item:
        raise HTTPException(status_code=404, detail="Master item not found")
        
    s_item.is_matched = True
    s_item.matched_master_id = m_item.id
    s_item.match_confidence = 100.0
    s_item.match_type = "manual"
    
    db.commit()
    return {"success": True}

@app.get("/api/search-master-items/")
def search_master_items(query: str, db: Session = Depends(get_db)):
    """Used in the frontend to search for master items during manual matching review."""
    items = db.query(MasterItem).filter(
        or_(
            MasterItem.name.ilike(f"%{query}%"),
            MasterItem.barcode.ilike(f"%{query}%"),
            MasterItem.article.ilike(f"%{query}%")
        )
    ).limit(50).all()
    return items

@app.get("/api/export/")
def export_matched_items(format: str = "csv", db: Session = Depends(get_db)):
    """Export all matched items for 1C import."""
    matched_items = get_results(status="matched", skip=0, limit=100000, db=db)
    
    if not matched_items:
        raise HTTPException(status_code=404, detail="No matched items to export")
        
    if format == "csv":
        csv_data = generate_1c_export_csv(matched_items)
        return Response(
            content=csv_data, 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=export_1c.csv"}
        )
    elif format == "xml":
        xml_data = generate_1c_export_xml(matched_items)
        return Response(
            content=xml_data, 
            media_type="application/xml", 
            headers={"Content-Disposition": "attachment; filename=export_1c.xml"}
        )
    else:
         raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'xml'")
