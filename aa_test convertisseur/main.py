import json

# --- Configuration ---
input_file = "input.json"   # ton fichier source
output_file = "output.json" # fichier de sortie

# --- Lecture du JSON ---
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Transformation ---
new_items = []
for item in data.get("relationships_following", []):
    title = item.get("title", "")
    string_data = item.get("string_list_data", [])
    
    for s in string_data:
        href = s.get("href", "")
        timestamp = s.get("timestamp", 0)
        
        new_item = {
            "title": title,
            "media_list_data": [],
            "string_list_data": [
                {
                    "href": href,
                    "value": title,  # on ajoute la valeur du titre ici
                    "timestamp": timestamp
                }
            ]
        }
        new_items.append(new_item)

# --- Sauvegarde du résultat ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)

print(f"Transformation terminée. {len(new_items)} éléments écrits dans {output_file}.")
