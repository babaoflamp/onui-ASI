
import pandas as pd
import csv
import os

def main():
    excel_path = 'data/강의별 단어_예문.xlsx'
    csv_target = 'data/sp_ko_questions.csv'
    
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    # 1. Load existing CSV sentences to avoid duplicates
    existing_sentences = set()
    next_id = 1
    if os.path.exists(csv_target):
        with open(csv_target, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_sentences.add(row['sentence'].strip())
                try:
                    next_id = max(next_id, int(row['ko_id']) + 1)
                except:
                    pass
    
    # 2. Extract from Excel
    extracted = []
    xl = pd.ExcelFile(excel_path)
    current_order = next_id
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet)
        # Columns: ['단계', '주차', '분류', '차시', '주제', '단어', '예문1', '예문2', '예문3']
        for _, row in df.iterrows():
            level = str(row.get('단계', sheet))
            topic = str(row.get('주제', ''))
            
            for col in ['예문1', '예문2', '예문3']:
                sentence = str(row.get(col, '')).strip()
                if sentence and sentence != 'nan' and sentence not in existing_sentences:
                    extracted.append({
                        'ko_id': next_id,
                        'order': current_order,
                        'sentence': sentence,
                        'syll_ltrs': '',
                        'syll_phns': '',
                        'fst': ''
                    })
                    existing_sentences.add(sentence)
                    next_id += 1
                    current_order += 1

    print(f"Extracted {len(extracted)} new sentences.")

    # 3. Append to CSV
    file_exists = os.path.exists(csv_target)
    with open(csv_target, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ko_id', 'order', 'sentence', 'syll_ltrs', 'syll_phns', 'fst'])
        if not file_exists:
            writer.writeheader()
        for item in extracted:
            writer.writerow(item)

    print(f"Successfully added {len(extracted)} sentences to {csv_target}.")

if __name__ == '__main__':
    main()
