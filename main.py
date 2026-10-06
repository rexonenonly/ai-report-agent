"""AI Report Agent: baca data CSV -> analisis pakai LLM -> generate laporan.

Usage:
    python main.py --input data/sales_sample.csv [--out report.md]

Butuh: pip install openai python-dotenv
Set OPENAI_API_KEY di .env (lihat .env.example).
"""
import argparse
import csv
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
MODEL = "kr/deepseek-3.2"  # ponytail: satu model hardcoded; ganti via --model kalau perlu multi-model
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY")


def get_client():
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def fetch_data(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def analyze(rows: list[dict]) -> str:
    """Agent loop: data + instruksi -> LLM -> laporan terstruktur."""
    system = (
        "Kamu adalah analyst AI agent. Kamu menerjemahkan kebutuhan bisnis "
        "(laporan rekap penjualan) menjadi output terstruktur dari data. "
        "Jawab dalam bahasa Indonesia, format markdown."
    )
    user = (
        f"Dari data rekap penjualan berikut:\n"
        f"{json.dumps(rows, indent=2, ensure_ascii=False)}\n\n"
        "Buat:\n"
        "1. Rekap per bulan (total penjualan & total unit)\n"
        "2. 3 insight / temuan penting\n"
        "3. 2 rekomendasi tindakan nyata untuk tim sales\n"
        "Output: markdown rapi, pakai tabel untuk rekap."
    )
    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="path file CSV")
    p.add_argument("--out", default="report.md", help="path output markdown")
    p.add_argument("--model", default=MODEL)
    args = p.parse_args()
    globals()["MODEL"] = args.model

    rows = fetch_data(args.input)
    if not rows:
        raise SystemExit(f"CSV kosong: {args.input}")
    print(f"[agent] {len(rows)} baris data dimuat dari {args.input}")

    report = analyze(rows)
    out = Path(args.out)
    out.write_text(report, encoding="utf-8")
    print(f"[agent] laporan disimpan ke {out.resolve()}")


if __name__ == "__main__":
    main()
