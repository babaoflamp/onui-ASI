import pandas as pd
import os

def merge_level_info():
    excel_path = 'data/강의별 단어_예문.xlsx'
    csv_path = 'data/sp_ko_questions.csv'
    output_path = 'data/sp_ko_questions_with_levels.csv'

    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Load Excel and CSV
    df_excel = pd.read_excel(excel_path)
    df_csv = pd.read_csv(csv_path)

    print(f"Excel rows: {len(df_excel)}")
    print(f"CSV rows: {len(df_csv)}")

    # Create a mapping from sentence to level
    # We need to handle 예문1, 예문2, 예문3
    sentence_to_level = {}
    for _, row in df_excel.iterrows():
        level = row['단계']
        for col in ['예문1', '예문2', '예문3']:
            if pd.notna(row[col]):
                sentence = str(row[col]).strip()
                sentence_to_level[sentence] = level

    # Add level column to CSV
    unmatched_sentences = []
    def get_level(sentence):
        s = str(sentence).strip()
        level = sentence_to_level.get(s)
        if level is None:
            unmatched_sentences.append(s)
            return "기타"
        return level

    df_csv['level'] = df_csv['sentence'].apply(get_level)

    if unmatched_sentences:
        print("\n--- Unmatched Sentences ---")
        for s in unmatched_sentences:
            print(s)
        print(f"Total unmatched: {len(unmatched_sentences)} (out of {len(df_csv)})")

    # Save to new CSV
    df_csv.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Merged CSV saved to {output_path}")
    
    # Also backup original and replace
    os.rename(csv_path, csv_path + '.bak_no_level')
    os.rename(output_path, csv_path)
    print("Replaced sp_ko_questions.csv with the new version containing levels.")

if __name__ == "__main__":
    merge_level_info()
