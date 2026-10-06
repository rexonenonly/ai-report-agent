"""Satu check: fetch_data + determinism tanpa LLM.
Jalankan: python test_main.py
"""
import csv
import tempfile
import os
from pathlib import Path

from main import fetch_data

def test_fetch_data():
    p = Path("data/sales_sample.csv")
    rows = fetch_data(str(p))
    assert len(rows) == 12, f"seharusnya 12 baris, dapat {len(rows)}"
    assert rows[0]["produk"] == "Laptop Pro 14"
    assert int(rows[0]["unit"]) == 12
    # cek total unit bulan Juli
    juli = [int(r["unit"]) for r in rows if r["tanggal"].startswith("2026-07")]
    assert sum(juli) == 12 + 45 + 8 + 15, f"unit Juli salah: {sum(juli)}"
    print("PASS fetch_data")

if __name__ == "__main__":
    test_fetch_data()
    print("All checks passed.")
