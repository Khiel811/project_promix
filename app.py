
import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PROMIX PDF Reader", page_icon="📄", layout="centered")

st.markdown("""
<style>
.stApp{background:#fff}
.block-container{max-width:820px;padding:38px 32px 110px}
#MainMenu,header,footer{visibility:hidden}
.hero{color:#292b36;font-family:Arial,sans-serif;font-size:clamp(42px,7vw,76px);
font-weight:800;line-height:1.38;letter-spacing:-2px;margin:10px 0 30px}
.desc{color:#888b91;font-size:22px;line-height:1.75;margin-bottom:30px}
.visitors{color:#888b91;font-size:21px;margin-bottom:35px}
.dot{display:inline-block;width:28px;height:28px;border-radius:50%;vertical-align:-5px;margin-right:8px;
background:linear-gradient(145deg,#b7f9d4,#42d99b);box-shadow:inset 0 0 0 1px #79dcae}
.info{background:#e7f2ff;border-radius:17px;color:#24639a;padding:22px 28px;font-size:20px;margin-top:20px}
.card{background:#f4f5f7;border-radius:16px;padding:18px 22px;margin:12px 0}
.card h3{margin:0 0 8px;color:#292b36}
.metric{font-size:26px;font-weight:700;color:#292b36}
.small{color:#888b91}
.footer-badge{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);
background:#fff;border-radius:28px;box-shadow:0 5px 24px rgba(0,0,0,.13);
padding:16px 28px;color:#354a8d;font-size:17px;line-height:1.45;z-index:99;
width:min(390px,calc(100vw - 90px))}
@media(max-width:600px){.block-container{padding:20px 31px 120px}.hero{font-size:46px}
.desc{font-size:20px}.visitors{font-size:19px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero">PROMIX PDF<br>Reader SUPAYA<br>CICILAN PROMIX<br>ANDA LEBIH<br>NGEBUGUT !!</div>""", unsafe_allow_html=True)
st.markdown("""<div class="desc">Upload 1 file PDF laporan PROMIX untuk melihat hasil per<br>kategori dan menyiapkan data copy-paste.</div>""", unsafe_allow_html=True)
st.markdown('<div class="visitors"><span class="dot"></span>Pengunjung sedang aktif: 3</div>', unsafe_allow_html=True)

st.markdown("### Upload file PDF PROMIX")
pdf = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=False)

def extract_text(uploaded):
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(uploaded.getvalue()))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception as e:
        st.error(f"Gagal membaca PDF: {e}")
        return ""

def money_to_int(s):
    s = re.sub(r"[^0-9]", "", str(s))
    return int(s) if s else 0

def parse_summary(text):
    result = {}
    patterns = {
        "Sales Total": r"Sales Total\s+([\d\.]+)",
        "Discount Total": r"Discount Total\s+([\d\.]+)",
        "Net Sales": r"Net Sales\s+([\d\.]+)",
        "Order Fee Total": r"Order Fee Total\s+([\d\.]+)",
        "Gross Sales": r"Gross Sales\s+([\d\.]+)",
        "Pax Total": r"Pax Total\s+([\d\.]+)",
        "Number of Bills": r"Number of Bills\s+([\d\.]+)",
        "Void Total": r"Void Total\s+([\d\.]+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        if m:
            result[key] = money_to_int(m.group(1))
    return result

def parse_category_totals(text):
    # Extract the category total rows from "Sales By Menu".
    rows = []
    for m in re.finditer(r"Total\s*-\s*([A-Z][A-Z0-9 .]+?)\s+([\d\.]+)\s+([\d\.]+)", text):
        name = m.group(1).strip()
        qty = money_to_int(m.group(2))
        value = money_to_int(m.group(3))
        if name and name not in {"BEVERAGES", "MIE"}:
            rows.append({"Kategori": name, "Qty": qty, "Value": value})
    # Remove duplicate category names while preserving first occurrence.
    seen = set()
    clean = []
    for r in rows:
        if r["Kategori"] not in seen:
            seen.add(r["Kategori"])
            clean.append(r)
    return pd.DataFrame(clean)

if not pdf:
    st.markdown('<div class="info">Silakan upload 1 file PDF terlebih dahulu.</div>', unsafe_allow_html=True)
else:
    st.success(f"PDF berhasil diupload: {pdf.name}")
    text = extract_text(pdf)

    if text:
        summary = parse_summary(text)
        st.subheader("Sales Recapitulation")

        cols = st.columns(2)
        metrics = [
            ("Sales Total", summary.get("Sales Total")),
            ("Net Sales", summary.get("Net Sales")),
            ("Gross Sales", summary.get("Gross Sales")),
            ("Pax Total", summary.get("Pax Total")),
        ]
        for i, (label, value) in enumerate(metrics):
            with cols[i % 2]:
                display = f"{value:,}".replace(",", ".") if value is not None else "-"
                st.markdown(f'<div class="card"><div class="small">{label}</div><div class="metric">{display}</div></div>', unsafe_allow_html=True)

        st.subheader("Hasil per Kategori")
        df = parse_category_totals(text)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "promix_kategori.csv", "text/csv")
            st.markdown("**Copy-paste:**")
            st.code(df.to_csv(index=False), language="text")
        else:
            st.warning("Data kategori belum berhasil dikenali dari PDF ini.")

        with st.expander("Lihat teks PDF mentah"):
            st.text_area("Extracted text", text, height=450)

        st.markdown('<div class="info">PDF berhasil diproses. Data di atas berasal dari laporan PROMIX yang di-upload.</div>', unsafe_allow_html=True)

st.markdown("""<div class="footer-badge">Developed by Eldwin Manalu<br>From Regional Kalimantan 1</div>""", unsafe_allow_html=True)
