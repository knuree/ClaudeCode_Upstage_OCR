"""안내서비스.csv 를 카테고리별로 분리하고 집계표를 만드는 도구.

사용법:  python solution.py
표준 라이브러리(csv, pathlib, collections)만 사용합니다.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUT = BASE / "안내서비스.csv"
OUT_DIR = BASE / "출력_카테고리별"
SUMMARY = BASE / "결과_카테고리집계.csv"


def representative(orgs):
    """가장 많이 등장한 문의기관. 동률이면 가나다순으로 앞선 기관."""
    counts = Counter(orgs)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def main():
    # utf-8-sig: 엑셀에서 저장한 BOM 포함 CSV도 안전하게 읽는다
    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = [r for r in reader if (r.get("카테고리") or "").strip()]

    groups = defaultdict(list)
    for r in rows:
        groups[r["카테고리"].strip()].append(r)

    OUT_DIR.mkdir(exist_ok=True)
    print(f"[OK] 안내서비스 {len(rows)}건 카테고리별 분리 → {OUT_DIR.name}/")

    summary = []
    for cat, items in groups.items():  # CSV 등장 순서 유지
        with (OUT_DIR / f"{cat}.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(items)
        rep = representative([i["문의기관"] for i in items])
        summary.append((cat, len(items), rep))
        print(f" · {cat} {len(items)}건")

    with SUMMARY.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["카테고리", "건수", "대표_문의기관"])
        w.writerows(summary)
    print(f"[OK] 집계표 → {SUMMARY.name}")


if __name__ == "__main__":
    main()
