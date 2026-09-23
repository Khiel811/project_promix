import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Usage Bahan / Gramasi / COST CONTROLLING",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ====================== JUDUL ======================
st.markdown("""
# Usage Bahan / Gramasi /  
COST CONTROLLING /  
MANAJER ORDERING CONTROLLING
""")

# ====================== RESEP (berdasarkan nama produk di PDF) ======================
# Catatan: Gramasi masih sementara.
# Kirim PDF/video resep yang akurat nanti agar Usage-nya 100% pas.
RESEP = {
    "MIE GACOAN": {
        "Mie": 1.0,
        "Kerupuk Mie": 0.004,
        "Gula Pasir (Bukan Biang)": 0.0065
    },
    "MIE HOMPIMPA": {
        "Mie": 1.0,
        "Kerupuk Mie": 0.004,
        "Gula Pasir (Bukan Biang)": 0.0065
    },
    "MIE SUIT": {
        "Mie": 1.0,
        "Kerupuk Mie": 0.004,
        "Gula Pasir (Bukan Biang)": 0.0065
    },
    "UDANG KEJU": {
        "Kulit Pangsit": 0.013,
        "Surai Naga": 0.006
    },
    "UDANG RAMBUTAN": {
        "Kulit Pangsit": 0.013,
        "Surai Naga": 0.006
    },
    "LUMPIA UDANG": {
        "Kulit Pangsit": 0.013,
        "Surai Naga": 0.006
    },
    "SIOMAY": {
        "Kulit Pangsit": 0.013
    },
    "PANGSIT GORENG": {
        "Kulit Pangsit": 0.013
    },
    "ES GOBAK SODOR": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015
    },
    "ES PETAK UMPET": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015
    },
    "ES SLUKU BATHOK": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015
    },
    "ES TEKLEK": {
        "Buah Apel": 8,
        "Buah Peer": 18,
        "Cincau": 18,
        "Nata de Coco": 18,
        "Gula Pasir (Bukan Biang)": 0.015
    },
    "TEA": {
        "Gula Pasir (Bukan Biang)": 0.012
    },
    "LEMON TEA": {
        "Gula Pasir (Bukan Biang)": 0.015
    },
    "THAI TEA": {
        "Gula Pasir (Bukan Biang)": 0.015,
        "Susu UHT": 50
    },
    "THAI GREEN TEA": {
        "Gula Pasir (Bukan Biang)": 0.015,
        "Susu UHT": 50
    },
    "MILO": {
        "Susu UHT": 50,
        "Gula Pasir (Bukan Biang)": 0.01
    },
    "ORANGE": {
        "Gula Pasir (Bukan Biang)": 0.012
    },
    "TEH TARIK": {
        "Gula Pasir (Bukan Biang)": 0.012,
        "Susu UHT": 40
    },
    "VANILLA LATTE": {
        "Susu UHT": 50,
        "Gula Pasir (Bukan Biang)": 0.01
    },
    "AIR MINERAL": {},
}

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

# ====================== INPUT PENJUALAN (KOSONG) ======================
st.markdown("### Paste Jumlah Penjualan")
st.caption("Copy dari laporan Sales Menu → paste di bawah (Nama Menu lalu Qty)")

input_text = st.text_area(
    label="Data Penjualan",
    value="",
    height=260,
    placeholder="Contoh format:\nMIE GACOAN\n1438\nUDANG KEJU\n852\nLUMPIA UDANG\n160"
)

hitung = st.button("Hitung Usage Bahan", type="primary", use_container_width=True)

# ====================== FUNGSI PARSE ======================
def parse_data(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    result = {}
    i = 0
    while i < len(lines) - 1:
        menu = lines[i].upper()
        try:
            qty = float(lines[i + 1].replace(".", "").replace(",", "."))
            result[menu] = qty
            i += 2
        except:
            i += 1
    return result

# ====================== HITUNG & TAMPILKAN HASIL ======================
if hitung:
    if not input_text.strip():
        st.warning("Silakan paste data penjualan terlebih dahulu.")
    else:
        penjualan = parse_data(input_text)
        usage = {}

        for menu, qty in penjualan.items():
            if menu in RESEP:
                for bahan, gramasi in RESEP[menu].items():
                    if gramasi > 0:
                        usage[bahan] = usage.get(bahan, 0) + (qty * gramasi)

        if usage:
            data = []
            for bahan, jumlah in sorted(usage.items()):
                data.append({
                    "Bahan": bahan,
                    "Usage": round(jumlah, 4),
                    "Satuan": SATUAN.get(bahan, "-")
                })

            df = pd.DataFrame(data)

            st.markdown("### Hasil Usage Bahan")
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

            # Tombol Download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="usage_bahan.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Tidak ada bahan yang terhitung. Periksa nama menu apakah sesuai.")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #555; font-size: 0.95rem; padding: 10px;'>
    <b>Developed by Eldwin Manalu</b><br>
    From Regional Kalimantan 2
</div>
""", unsafe_allow_html=True)
