from sqlalchemy.orm import Session
from thefuzz import fuzz, process
from models import MasterItem, SupplierItem

# Configurable threshold for fuzzy matching
FUZZY_MATCH_THRESHOLD = 80

def match_supplier_items(db: Session):
    """
    Attempts to match all currently unmatched SupplierItems against MasterItems.
    Priority:
    1. Exact Barcode Match
    2. Exact Article Match
    3. Fuzzy Name Match
    """
    unmatched_items = db.query(SupplierItem).filter(SupplierItem.is_matched == False).all()
    if not unmatched_items:
        return {"matched": 0, "remaining": 0}

    # Pre-load master items into memory for faster searching
    # In a very large DB, we'd need a different strategy (chunking or DB-level full-text search)
    # But for a standard nomenclature size (e.g., < 100k items), this is fine.
    master_items = db.query(MasterItem).all()
    
    # Create lookup dicts for O(1) exact matches
    barcode_lookup = {item.barcode: item for item in master_items if item.barcode}
    article_lookup = {item.article: item for item in master_items if item.article}
    
    # List of tuples for fuzzy search: (name, MasterItem)
    # thefuzz `process.extractOne` needs a dict or list of choices
    name_choices = {item.id: item.name for item in master_items}
    
    matched_count = 0
    
    for s_item in unmatched_items:
        # 1. Barcode Match
        if s_item.barcode and s_item.barcode in barcode_lookup:
            m_item = barcode_lookup[s_item.barcode]
            s_item.is_matched = True
            s_item.matched_master_id = m_item.id
            s_item.match_confidence = 100.0
            s_item.match_type = "barcode"
            matched_count += 1
            continue

        # 2. Article Match
        if s_item.article and s_item.article in article_lookup:
            m_item = article_lookup[s_item.article]
            s_item.is_matched = True
            s_item.matched_master_id = m_item.id
            s_item.match_confidence = 100.0
            s_item.match_type = "article"
            matched_count += 1
            continue
            
        # 3. Fuzzy Name Match using Token Set Ratio (good for "Brand X Product Y" vs "Product Y Brand X")
        if s_item.name and name_choices:
            # extractOne returns a tuple: (match_string, score, choice_key[id])
            best_match = process.extractOne(
                s_item.name, 
                name_choices, 
                scorer=fuzz.token_set_ratio,
                score_cutoff=FUZZY_MATCH_THRESHOLD
            )
            
            if best_match:
                match_string, score, master_id = best_match
                s_item.is_matched = True
                s_item.matched_master_id = master_id
                s_item.match_confidence = float(score)
                s_item.match_type = "fuzzy"
                matched_count += 1
                
    # Commit changes to database
    db.commit()
    
    remaining = len(unmatched_items) - matched_count
    return {
        "matched": matched_count,
        "remaining": remaining
    }
