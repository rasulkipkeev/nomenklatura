from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MasterItem(Base):
    __tablename__ = "master_items"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, index=True, nullable=True)
    article = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)
    # The actual ID or code in 1C to identify the item on export
    code_1c = Column(String, unique=True, index=True, nullable=False)

class SupplierItem(Base):
    __tablename__ = "supplier_items"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String, index=True)
    barcode = Column(String, index=True, nullable=True)
    article = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    
    # Matching status
    is_matched = Column(Boolean, default=False)
    matched_master_id = Column(Integer, ForeignKey("master_items.id"), nullable=True)
    match_confidence = Column(Float, nullable=True) # E.g., 100 for exact, 85 for fuzzy
    match_type = Column(String, nullable=True) # E.g., 'barcode', 'article', 'fuzzy', 'manual'
