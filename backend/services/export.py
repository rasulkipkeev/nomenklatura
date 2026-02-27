import csv
from io import StringIO
from typing import List
import xml.etree.ElementTree as ET

def generate_1c_export_csv(matched_items: List[dict]) -> str:
    """
    Generates a CSV string containing the matched items formatted for 1C import.
    Expected to include the 1C Code of the Master Item, Supplier Code/Name, and Price.
    """
    output = StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Headers suitable for a typical 1C upload document
    writer.writerow([
        "Код1С",          # Master Item code
        "Номенклатура",   # Master Item name
        "Поставщик",      # Supplier Name
        "АртикулПоставщика",
        "Штрихкод",
        "Цена"
    ])
    
    for item in matched_items:
        master = item.get("master_item", {})
        writer.writerow([
            master.get("code_1c", ""),
            master.get("name", ""),
            item.get("supplier_name", ""),
            item.get("article", ""),
            item.get("barcode", ""),
            item.get("price", "")
        ])
        
    return output.getvalue()

def generate_1c_export_xml(matched_items: List[dict]) -> str:
    """
    Generates an XML string (CommerceML-like) for 1C import.
    """
    root = ET.Element("КоммерческаяИнформация", ВерсияСхемы="2.03", ДатаФормирования="")
    docs = ET.SubElement(root, "Документ")
    
    # Header metadata could go here (e.g., date, supplier, etc)
    
    items_node = ET.SubElement(docs, "Товары")
    
    for item in matched_items:
        master = item.get("master_item", {})
        
        item_node = ET.SubElement(items_node, "Товар")
        ET.SubElement(item_node, "Ид").text = master.get("code_1c", "")
        ET.SubElement(item_node, "Наименование").text = master.get("name", "")
        ET.SubElement(item_node, "Поставщик").text = item.get("supplier_name", "")
        ET.SubElement(item_node, "АртикулПоставщика").text = item.get("article", "")
        ET.SubElement(item_node, "Штрихкод").text = item.get("barcode", "")
        ET.SubElement(item_node, "ЦенаЗаЕдиницу").text = str(item.get("price", ""))
        
    # Pretty print hack (in Python 3.9+ use ET.indent, for older manual spacing)
    if hasattr(ET, 'indent'):
        ET.indent(root, space="  ", level=0)
        
    return ET.tostring(root, encoding='unicode', xml_declaration=True)
