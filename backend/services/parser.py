import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def parse_price_list(file_bytes: bytes, filename: str, supplier_name: str) -> list[dict]:
    """
    Parses an uploaded file (.xlsx, .csv, .xml) and returns a list of dictionaries.
    Expected dict structure (based on what we can extract):
    {
        "supplier_name": str,
        "name": str,
        "barcode": str | None,
        "article": str | None,
        "price": float | None
    }
    """
    extension = filename.split(".")[-1].lower()
    
    if extension == "csv":
        # Using a versatile separator attempt or default to comma/semicolon
        try:
            df = pd.read_csv(BytesIO(file_bytes), sep=';')
            if len(df.columns) < 2:
                df = pd.read_csv(BytesIO(file_bytes), sep=',')
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")
            
        return _df_to_records(df, supplier_name)
        
    elif extension in ["xls", "xlsx"]:
        try:
            df = pd.read_excel(BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Failed to parse Excel: {e}")
            
        return _df_to_records(df, supplier_name)
        
    elif extension == "xml":
        try:
            return _parse_xml(file_bytes, supplier_name)
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {e}")
            
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def _df_to_records(df: pd.DataFrame, supplier_name: str) -> list[dict]:
    """
    Tries to intelligently map dataframe columns to our expected fields.
    This is a basic implementation; in a real scenario, you'd likely want 
    a mapping configuration per supplier.
    """
    
    # Simple heuristics for column names (case-insensitive)
    col_mapping = {
        "name": ["наименование", "название", "товар", "name", "item", "номенклатура"],
        "barcode": ["штрихкод", "barcode", "штрих-код", "ean", "штрих код"],
        "article": ["артикул", "article", "код", "sku"],
        "price": ["цена", "price", "стоимость"]
    }

    # Find matching columns in the dataframe
    df_cols = [str(c).lower().strip() for c in df.columns]
    
    actual_mapping = {}
    for standard_col, possible_names in col_mapping.items():
        for i, df_col in enumerate(df_cols):
            if any(name in df_col for name in possible_names):
                actual_mapping[standard_col] = df.columns[i]
                break

    if "name" not in actual_mapping:
         # Fallback to the first string column if no clear name column is found
         for col in df.columns:
             if df[col].dtype == 'object':
                 actual_mapping["name"] = col
                 break
         
         if "name" not in actual_mapping:
            raise ValueError("Could not automatically determine the 'name' column in the file.")

    records = []
    # Replace NaNs with None
    df = df.where(pd.notnull(df), None)

    for _, row in df.iterrows():
        # Ensure name isn't completely empty
        raw_name = row.get(actual_mapping.get("name"))
        if not raw_name or pd.isna(raw_name) or str(raw_name).strip() == "":
            continue
            
        record = {
            "supplier_name": supplier_name,
            "name": str(raw_name).strip(),
            "barcode": str(row.get(actual_mapping.get("barcode", "none_existent"))).strip() if actual_mapping.get("barcode") and row.get(actual_mapping.get("barcode")) else None,
            "article": str(row.get(actual_mapping.get("article", "none_existent"))).strip() if actual_mapping.get("article") and row.get(actual_mapping.get("article")) else None,
            "price": None
        }
        
        # Handle barcodes that might have been parsed as floats (e.g. 4.60123e+12)
        if record["barcode"] and record["barcode"].endswith(".0"):
             record["barcode"] = record["barcode"][:-2]
             
        # Try to parse price reliably
        if actual_mapping.get("price"):
            raw_price = row.get(actual_mapping.get("price"))
            if raw_price:
                 try:
                     record["price"] = float(str(raw_price).replace(',', '.'))
                 except ValueError:
                     pass

        records.append(record)
        
    return records


def _parse_xml(file_bytes: bytes, supplier_name: str) -> list[dict]:
    """
    Very basic XML parser expecting a flat list of items.
    Like CommerceML, but simplified for generic fallback.
    """
    tree = ET.parse(BytesIO(file_bytes))
    root = tree.getroot()
    
    records = []
    
    # We'll just look for elements that might represent an item
    # This highly depends on the XML structure; assuming a generic format where 
    # items are repeated nodes like <Item> or <Товар>
    item_nodes = root.findall(".//Item") or root.findall(".//Товар")
    
    for node in item_nodes:
        name_node = node.find("Name") or node.find("Наименование") or node.find("Название")
        barcode_node = node.find("Barcode") or node.find("Штрихкод")
        article_node = node.find("Article") or node.find("Артикул")
        price_node = node.find("Price") or node.find("Цена")
        
        if name_node is not None and name_node.text:
            records.append({
                "supplier_name": supplier_name,
                "name": name_node.text.strip(),
                "barcode": barcode_node.text.strip() if barcode_node is not None and barcode_node.text else None,
                "article": article_node.text.strip() if article_node is not None and article_node.text else None,
                "price": float(price_node.text.replace(',', '.')) if price_node is not None and price_node.text else None
            })
            
    if not records:
        raise ValueError("Could not find required item nodes (<Товар> или <Item>) or their <Наименование> in XML.")
        
    return records
