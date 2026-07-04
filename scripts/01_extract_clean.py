"""Extract and clean the supplied ABC Bank loan portfolio Excel file."""
from __future__ import annotations
import argparse, csv, datetime, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RATING_RANK = {"AAA":1,"AA":2,"A":3,"BBB":4,"BB":5,"B":6,"CCC":7,"CC":8,"C":9,"D":10}


def col_to_idx(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def excel_date(serial: str) -> str:
    return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(serial))).date().isoformat()


def load_xlsx_first_sheet(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as z:
        shared = []
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(f"{NS}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{NS}t")))
        rows = []
        for _, elem in ET.iterparse(z.open("xl/worksheets/sheet1.xml"), events=("end",)):
            if elem.tag == f"{NS}row":
                vals = {}
                for c in elem.findall(f"{NS}c"):
                    v = c.find(f"{NS}v")
                    value = "" if v is None else (v.text or "")
                    if c.attrib.get("t") == "s" and value != "":
                        value = shared[int(value)]
                    vals[col_to_idx(c.attrib.get("r", "A1"))] = value
                if vals:
                    rows.append([vals.get(i, "") for i in range(max(vals) + 1)])
                elem.clear()
        return rows


def transform(rows: list[list[str]]) -> list[dict]:
    clean, seen = [], set()
    for r in rows[1:]:
        r += [""] * (8 - len(r))
        loan_id = r[0].strip()
        if not loan_id or loan_id in seen:
            continue
        seen.add(loan_id)
        date = excel_date(r[1])
        amount = float(r[7] or 0)
        sector = r[2].strip().replace("Telecommumication", "Telecommunication")
        status = r[6].strip().title().replace("Non Performing", "Non-Performing")
        rating = r[5].strip().upper()
        clean.append({
            "loan_id": loan_id,
            "loan_originating_date": date,
            "year": int(date[:4]),
            "month": date[:7],
            "sector": sector,
            "loan_type": r[3].strip(),
            "collateral": r[4].strip().title(),
            "initial_rating": rating,
            "rating_rank": RATING_RANK.get(rating, ""),
            "performance_status": status,
            "is_npl": 1 if status == "Non-Performing" else 0,
            "amount_outstanding_lkr": amount,
            "amount_outstanding_mn_lkr": amount / 1_000_000,
        })
    return clean


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/raw/loan_portfolio.xlsx")
    ap.add_argument("--output", default="data/processed/clean_loan_portfolio.csv")
    args = ap.parse_args()
    rows = transform(load_xlsx_first_sheet(Path(args.input)))
    assert len({r["loan_id"] for r in rows}) == len(rows), "Duplicate loan IDs remain"
    assert all(float(r["amount_outstanding_lkr"]) >= 0 for r in rows), "Negative exposure found"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows):,} cleaned rows to {args.output}")


if __name__ == "__main__":
    main()
