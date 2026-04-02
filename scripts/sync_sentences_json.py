
import pandas as pd
import json
import os

def main():
    excel_path = 'data/강의별 단어_예문.xlsx'
    json_path = 'data/sentences.json'
    
    if not os.path.exists(excel_path):
        return

    # 1. Load existing JSON
    existing_data = []
    existing_sentences = set()
    next_id = 1
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            for item in existing_data:
                existing_sentences.add(item.get('sentenceKr', '').strip())
                try:
                    next_id = max(next_id, int(item.get('id', 0)) + 1)
                except:
                    pass

    # 2. Extract from Excel
    xl = pd.ExcelFile(excel_path)
    new_items = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet)
        for _, row in df.iterrows():
            level = str(row.get('단계', sheet))
            category = str(row.get('분류', '일반'))
            topic = str(row.get('주제', ''))
            
            for col in ['예문1', '예문2', '예문3']:
                sentence = str(row.get(col, '')).strip()
                if sentence and sentence != 'nan' and sentence not in existing_sentences:
                    new_items.append({
                        "id": next_id,
                        "level": level,
                        "sentenceKr": sentence,
                        "sentenceEn": "",
                        "difficulty": "보통",
                        "tags": [category, topic],
                        "category": category,
                        "tips": f"{topic} 관련 표현입니다."
                    })
                    existing_sentences.add(sentence)
                    next_id += 1

    # 3. Save merged data
    merged = existing_data + new_items
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Added {len(new_items)} new items to {json_path}. Total: {len(merged)}")

if __name__ == '__main__':
    main()
