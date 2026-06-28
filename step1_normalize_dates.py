import csv
import re
from datetime import datetime

def normalize_date(raw: str) -> str:
    raw = raw.strip()

    # 이미 YYYY-MM-DD
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
        return raw

    # YYYY/MM/DD
    m = re.fullmatch(r'(\d{4})/(\d{2})/(\d{2})', raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 5월 4일  (연도 없음 → 2026 가정)
    m = re.fullmatch(r'(\d{1,2})월\s*(\d{1,2})일', raw)
    if m:
        return f"2026-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

    # YY.M.D  (예: 26.5.6)
    m = re.fullmatch(r'(\d{2})\.(\d{1,2})\.(\d{1,2})', raw)
    if m:
        year = 2000 + int(m.group(1))
        return f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    return raw  # 변환 불가 시 원본 유지

INPUT  = "Day3_과제_feedback.csv"
OUTPUT = "step1_normalized.csv"

with open(INPUT, encoding='utf-8-sig', newline='') as fin, \
     open(OUTPUT, 'w', encoding='utf-8-sig', newline='') as fout:

    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        original = row['받은날짜']
        row['받은날짜'] = normalize_date(original)
        if original != row['받은날짜']:
            print(f"  변환: '{original}' → '{row['받은날짜']}'")
        writer.writerow(row)

print(f"\n저장 완료: {OUTPUT}")
