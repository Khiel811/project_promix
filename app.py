import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO
import re

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

# ====================== RESEP (sementara - akan diganti akurat nanti) ======================
RESEP = {
    "MIE GACOAN": {"Mie": 1.0, "Kerupuk Mie": 0.004, "Gula Pasir (Bukan Biang)": 0.0065},
    "MIE HOMPIMPA": {"Mie": 1.0, "Kerupuk Mie": 0.004, "Gula Pasir (Bukan Biang)": 0.0065},
    "MIE SUIT": {"Mie": 1.0, "Kerupuk Mie": 0.004, "Gula Pasir (Bukan Biang)": 0.0065},
    "UDANG KEJU": {"Kulit Pangsit": 0.013, "Surai Naga": 0.006},
    "UDANG RAMBUTAN": {"Kulit Pangsit": 0.013, "Surai Naga": 0.006},
    "LUMPIA UDANG": {"Kulit Pangsit": 0.013, "Surai Naga": 0.006},
    "SIOMAY": {"Kulit Pangsit": 0.013},
    "PANGSIT GORENG": {"Kulit Pangsit": 0.013},
    "ES GOBAK SODOR": {"Buah Apel": 8, "Buah Peer": 18, "Cincau": 18, "Nata de Coco": 18, "Gula Pasir (Bukan Biang)": 0.015},
    "ES PETAK UMPET": {"Buah Apel": 8, "Buah Peer": 18, "Cincau": 18, "Nata de Coco": 18, "Gula Pasir (Bukan Biang)": 0.015},
    "ES SLUKU BATHOK": {"Buah Apel": 8, "Buah Peer": 18, "Cincau": 18, "Nata de Coco": 18, "Gula Pasir (Bukan Biang)": 0.015},
    "ES TEKLEK": {"Buah Apel": 8, "Buah Peer": 18, "Cincau": 18, "Nata de Coco": 18, "Gula Pasir (Bukan Biang)": 0.015},
    "TEA": {"Gula Pasir (Bukan Biang)": 0.012},
    "LEMON TEA": {"Gula Pasir (Bukan Biang)": 0.015},
    "THAI TEA": {"Gula Pasir (Bukan Biang)": 0.015, "Susu UHT": 50},
    "THAI GREEN TEA": {"Gula Pasir (Bukan Biang)": 0.015, "Susu UHT": 50},
    "MILO": {"Susu UHT": 50, "Gula Pasir (Bukan Biang)": 0.01},
    "ORANGE": {"Gula Pasir (Bukan Biang)": 0.012},
    "TEH TARIK": {"Gula Pasir (Bukan Biang)": 0.012, "Susu UHT": 40},
    "VANILLA LATTE": {"Susu UHT": 50, "Gula Pasir (Bukan Biang)": 0.01},
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

# ====================== FUNGSI PARSE PDF ======================
def extract_sales_from_pdf(pdf_file):
    """Ekstrak nama menu + qty dari PDF laporan penjualan PROMIX"""
    penjualan = {}
    
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    # Cari pola menu yang umum di PDF PROMIX
    # Contoh: MIE GACOAN 1.438 atau MIE GACOAN\n1438
    lines = full_text.splitlines()
    
    for i, line in enumerate(lines):
        line_clean = line.strip().upper()
        
        # Cek apakah baris ini nama menu yang ada di RESEP
        for menu in RESEP.keys():
            if menu in line_clean:
                # Coba ambil angka di baris yang sama atau baris berikutnya
                # Ambil semua angka di sekitarnya
                numbers = re.findall(r'[\d.]+', line_clean.replace(",", ""))
                
                # Jika tidak ada angka di baris yang sama, cek baris berikutnya
                if not numbers and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    numbers = re.findall(r'[\d.]+', next_line.replace(",", ""))
                
                if numbers:
                    try:
                        # Ambil angka terbesar (biasanya qty)
                        qty = max([float(n.replace(".", "")) if "." in n and len(n) > 4 else float(n) for n in numbers])
                        if qty > 0:
                            penjualan[menu] = qty
                    except:
                        pass
                break
    
    return penjualan

# ====================== FUNGSI PARSE TEXT (COPY PASTE) ======================
def parse_paste(text):
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

# ====================== UI ======================
tab1, tab2 = st.tabs(["📄 Scan PDF Laporan", "📋 Copy-Paste Penjualan"])

penjualan = {}

with tab1:
    st.markdown("### Upload PDF Laporan Penjualan")
    st.caption("Upload file PDF PROMIX (Sales Recapitulation)")
    
    uploaded_pdf = st.file_uploader("Pilih file PDF", type=["pdf"], key="pdf_uploader")
    
    if uploaded_pdf:
        with st.spinner("Sedang scan PDF..."):
            try:
                penjualan = extract_sales_from_pdf(BytesIO(uploaded_pdf.read()))
                
                if penjualan:
                    st.success(f"Berhasil membaca {len(penjualan)} menu dari PDF")
                    
                    # Tampilkan hasil scan
                    df_scan = pd.DataFrame([
                        {"Menu": k, "Qty": v} for k, v in sorted(penjualan.items())
                    ])
                    st.dataframe(df_scan, use_container_width=True, hide_index=True)
                else:
                    st.warning("Tidak berhasil membaca data penjualan dari PDF. Coba gunakan fitur Copy-Paste.")
            except Exception as e:
                st.error(f"Gagal membaca PDF: {e}")

with tab2:
    st.markdown("### Paste Jumlah Penjualan")
    st.caption("Copy dari laporan → paste di bawah (Nama Menu lalu Qty)")
    
    input_text = st.text_area(
        "Data Penjualan",
        value="",
        height=250,
        placeholder="MIE GACOAN\n1438\nUDANG KEJU\n852\nLUMPIA UDANG\n160"
    )
    
    if input_text.strip():
        penjualan = parse_paste(input_text)

# ====================== TOMBOL HITUNG ======================
st.markdown("---")
hitung = st.button("Hitung Usage Bahan", type="primary", use_container_width=True)

if hitung:
    if not penjualan:
        st.warning("Belum ada data penjualan. Silakan Scan PDF atau Copy-Paste dulu.")
    else:
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
                    "Bahan": st.column_config.TextColumn("Bahan"),
                    "Usage": st.column_config.NumberColumn("Usage", format="%.4f"),
                    "Satuan": st.column_config.TextColumn("Satuan"),
                }
            )

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv,
                "usage_bahan.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.warning("Tidak ada bahan yang terhitung.")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #555; font-size: 0.95rem; padding: 8px;'>
    <b>Developed by Eldwin Manalu</b><br>
    From Regional Kalimantan 2
</div>
""", unsafe_allow_html=True)
