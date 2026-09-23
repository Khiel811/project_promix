import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Usage Bahan / Gramasi / COST CONTROLLING",
    page_icon="📊",
    layout="wide"
)

st.title("Usage Bahan / Gramasi / COST CONTROLLING / MANAJER ORDERING CONTROLLING")
st.caption("Developed by Eldwin Manalu • Regional Kalimantan 1")

# ====================== DATA RESEP (sementara - akan diganti setelah kamu kirim PDF/video) ======================
# Format: Menu → {Bahan: gramasi per porsi}
RESEP = {
    "MIE GACOAN": {
        "Mie": 1,                    # pcs
        "Kerupuk Mie": 0.004,        # pack
        "Gula Pasir (Bukan Biang)": 0.0065,  # Kg
    },
    "MIE HOMPIMPA": {
        "Mie": 1,
        "Kerupuk Mie": 0.004,
        "Gula Pasir (Bukan Biang)": 0.0065,
    },
    "MIE SUIT": {
        "Mie": 1,
        "Kerupuk Mie": 0.004,
        "Gula Pasir (Bukan Biang)": 0.0065,
    },
    "UDANG KEJU": {
        "Kulit Pangsit": 0.013,      # ball
        "Surai Naga": 0.006,         # pack
    },
    "UDANG RAMBUTAN": {
        "Kulit Pangsit": 0.013,
        "Surai Naga": 0.006,
    },
    "LUMPIA UDANG": {
        "Kulit Pangsit": 0.013,
        "Surai Naga": 0.006,
    },
    "SIOMAY": {
        "Kulit Pangsit": 0.013,
    },
    "PANGSIT GORENG": {
        "Kulit Pangsit": 0.013,
    },
    "ES GOBAK SODOR": {
        "Buah Apel": 8,              # gram
        "Buah Peer": 18,             # gram
        "Cincau": 18,                # gram
        "Nata de Coco": 18,          # gram
        "Gula Pasir (Bukan Biang)": 0.015,
    },
    "ES PETAK UMPET": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015,
    },
    "ES SLUKU BATHOK": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015,
    },
    "ES TEKLEK": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015,
    },
    "TEA": {
        "Gula Pasir (Bukan Biang)": 0.012,
    },
    "LEMON TEA": {
        "Gula Pasir (Bukan Biang)": 0.015,
    },
    "THAI TEA": {
        "Gula Pasir (Bukan Biang)": 0.015,
        "Susu UHT": 50,              # ML
    },
    "THAI GREEN TEA": {
        "Gula Pasir (Bukan Biang)": 0.015,
        "Susu UHT": 50,
    },
    "MILO": {
        "Susu UHT": 50,
        "Gula Pasir (Bukan Biang)": 0.01,
    },
    "ORANGE": {
        "Gula Pasir (Bukan Biang)": 0.012,
    },
}

# Satuan bahan
SATUAN = {
    "Mie": "pcs",
    "Kulit Pangsit": "ball",
    "Surai Naga": "pack",
    "Kerupuk Mie": "pack",
    "Buah Apel": "gram",
    "Buah Peer": "gram",
    "Cincau": "gram",
    "Nata de Coco": "gram",
    "Gula Pasir (Bukan Biang)": "Kg",
    "Susu UHT": "ML",
}

# ====================== SIDEBAR - INPUT PENJUALAN ======================
with st.sidebar:
    st.header("📥 Input Jumlah Penjualan")
    st.info("Copy-paste dari laporan Sales Menu (format: Nama Menu lalu Qty)")

    contoh = """MIE GACOAN
1438
UDANG KEJU
852
UDANG RAMBUTAN
206
LUMPIA UDANG
160
SIOMAY
189
PANGSIT GORENG
46
ES GOBAK SODOR
86
ES PETAK UMPET
13
ES SLUKU BATHOK
11
ES TEKLEK
18
TEA
229
LEMON TEA
112
THAI TEA
72
THAI GREEN TEA
59
MILO
27
ORANGE
61"""

    input_text = st.text_area(
        "Paste data penjualan di sini:",
        value=contoh,
        height=350,
        help="Format: Nama Menu di baris ganjil, Qty di baris genap"
    )

    hitung = st.button("🔄 Hitung Usage Bahan", type="primary", use_container_width=True)

# ====================== PROSES HITUNG ======================
def parse_penjualan(text):
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    penjualan = {}
    i = 0
    while i < len(lines) - 1:
        menu = lines[i].upper()
        try:
            qty = float(lines[i+1].replace(".", "").replace(",", "."))
            penjualan[menu] = qty
            i += 2
        except:
            i += 1
    return penjualan

if hitung or input_text:
    penjualan = parse_penjualan(input_text)

    # Hitung usage
    usage = {}
    for menu, qty in penjualan.items():
        if menu in RESEP:
            for bahan, gramasi in RESEP[menu].items():
                usage[bahan] = usage.get(bahan, 0) + (qty * gramasi)

    # Buat DataFrame hasil
    if usage:
        df = pd.DataFrame([
            {
                "Bahan": bahan,
                "Usage": round(jumlah, 4) if isinstance(jumlah, float) else jumlah,
                "Satuan": SATUAN.get(bahan, "")
            }
            for bahan, jumlah in usage.items()
        ])
        df = df.sort_values("Bahan").reset_index(drop=True)

        st.subheader("📊 Hasil Perhitungan Usage Bahan")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Bahan": st.column_config.TextColumn("Bahan", width="medium"),
                "Usage": st.column_config.NumberColumn("Usage", format="%.4f"),
                "Satuan": st.column_config.TextColumn("Satuan", width="small"),
            }
        )

        # Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Hasil (CSV)",
            csv,
            "usage_bahan.csv",
            "text/csv",
            use_container_width=True
        )

        st.success(f"Berhasil menghitung usage dari {len(penjualan)} menu")
    else:
        st.warning("Tidak ada menu yang cocok dengan resep. Pastikan nama menu sama persis.")

# ====================== INFO ======================
with st.expander("ℹ️ Cara Pakai"):
    st.markdown("""
    1. Copy data **Sales Menu** dari laporan PDF (nama menu + qty)
    2. Paste di kotak kiri
    3. Klik **Hitung Usage Bahan**
    4. Hasil akan muncul di tabel

    **Catatan:**  
    Daftar resep/gramasi saat ini masih contoh.  
    Kirimkan **video + PDF resep/gramasi** supaya saya update agar hasilnya 100% akurat.
    """)

st.markdown("---")
st.caption("PROMIX Cost Controlling • Siap dikembangkan lebih lanjut")
