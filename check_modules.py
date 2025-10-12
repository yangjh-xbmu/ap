import json
from pathlib import Path

file_path = Path("workspace") / "concept_map.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

topic_data = data.get("topics", {}).get("测试主题", {})
concepts = topic_data.get("concepts", {})

for concept_id, concept_data in concepts.items():
    module_id = concept_data.get("module_id", "N/A")
    print(f"Concept: {concept_id}, Module ID: {module_id}")
