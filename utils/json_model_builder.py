# utils/json_model_builder.py

def build_semantic_model(parsed_structure):
    semantic_model = []

    for cls in parsed_structure.get("classes", []):
        class_entry = {
            "entity_type": "class",
            "name": cls["name"],
            "base_classes": cls["base_classes"],
            "line_number": cls["lineno"],
            "methods": [],
        }

        for method in cls["methods"]:
            class_entry["methods"].append({
                "name": method["name"],
                "parameters": method["params"],
                "line_number": method["lineno"]
            })

        semantic_model.append(class_entry)

    for func in parsed_structure.get("functions", []):
        semantic_model.append({
            "entity_type": "function",
            "name": func["name"],
            "parameters": func["params"],
            "line_number": func["lineno"]
        })

    return semantic_model
