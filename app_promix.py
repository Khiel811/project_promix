
import io
import re
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PROMIX PDF Reader", page_icon="📄", layout="centered")

st.markdown("""
<style>
.stApp{background:#fff}
.block-container{max-width:820px;padding:30px 32px 90px}
#MainMenu,header,footer{visibility:hidden}
.hero{color:#292b36;font-family:Arial,sans-serif;font-size:clamp(42px,7vw,76px);
font-weight:800;line-height:1.38;letter-spacing:-2px;margin:10px 0 30px}
.desc{color:#888b91;font-size:22px;line-height:1.75;margin-bottom:30px}
.visitors{color:#888b91;font-size:21px;margin-bottom:35px}
.dot{display:inline-block;width:28px;height:28px;border-radius:50%;vertical-align:-5px;margin-right:8px;
background:linear-gradient(145deg,#b7f9d4,#42d99b);box-shadow:inset 0 0 0 1px #79dcae}
.section-title{color:#292b36;font-size:42px;font-weight:800;line-height:1.35;margin-top:48px}
.card{background:#f5f6f8;border-radius:16px;padding:18px 22px;margin:10px 0}
.metric{font-size:26px;font-weight:700;color:#292b36}
.small{color:#888b91}
.info{background:#e7f2ff;border-radius:17px;color:#24639a;padding:22px 28px;font-size:20px;margin-top:20px}
[data-testid="stExpander"]{border:1px solid #d9d9dd;border-radius:15px;margin:12px 0}
div.stButton>button{border-radius:12px;background:#fff;border:1px solid #cfcfd4}
.footer-badge{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);
background:#fff;border-radius:28px;box-shadow:0 5px 24px rgba(0,0,0,.13);
padding:14px 25px;color:#354a8d;font-size:16px;line-height:1.45;z-index:99;
width:min(390px,calc(100vw - 90px))}
@media(max-width:600px){.block-container{padding:20px 31px 90px}.hero{font-size:46px}
.desc{font-size:20px}.section-title{font-size:40px}.visitors{font-size:19px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero">PROMIX PDF<br>Reader SUPAYA<br>CICILAN PROMIX<br>ANDA LEBIH<br>NGEBUGUT !!</div>""", unsafe_allow_html=True)
st.markdown("""<div class="desc">Upload 1 file PDF laporan PROMIX untuk melihat hasil per<br>kategori dan menyiapkan data copy-paste.</div>""", unsafe_allow_html=True)
st.markdown('<div class="visitors"><span class="dot"></span>Pengunjung sedang aktif: 1</div>', unsafe_allow_html=True)

pdf = st.file_uploader("Upload file PDF PROMIX", type=["pdf"], accept_multiple_files=False)

def get_pdf_text(uploaded):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(uploaded.getvalue()))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

def num(s):
    s = re.sub(r"[^0-9]", "", str(s))
    return int(s) if s else 0

def money(v):
    return f"{int(v):,}".replace(",", ".")

def parse_summary(text):
    out = {}
    pats = {
        "Sales Total": r"Sales Total\s+([\d\.]+)",
        "Discount Total": r"Discount Total\s+([\d\.]+)",
        "Net Sales": r"Net Sales\s+([\d\.]+)",
        "Gross Sales": r"Gross Sales\s+([\d\.]+)",
        "Pax Total": r"Pax Total\s+([\d\.]+)",
        "Number of Bills": r"Number of Bills\s+([\d\.]+)",
        "Void Total": r"Void Total\s+([\d\.]+)",
    }
    for k,p in pats.items():
        m=re.search(p,text,re.I)
        if m: out[k]=num(m.group(1))
    return out

# Parses the "Sales By Menu" portion of the PROMIX report.
# The parser keeps the report's category / DINE IN / TAKE AWAY hierarchy.
def parse_sales_by_menu(text):
    start = text.find("Sales By Menu")
    end = text.find("Non Sales By Menu")
    section = text[start:end if end!=-1 else len(text)]
    lines=[x.strip() for x in section.splitlines() if x.strip()]
    category=None
    channel=None
    rows=[]
    known_categories=[
        "BEVERAGES","BEVERAGES ICE.","BEVERAGES ISIAN","DIMSUM",
        "ES BUAH","MIE","MIE ISIAN","MIE.","PACKAGING","PAKET"
    ]
    for i,line in enumerate(lines):
        u=line.upper()
        # Category headings
        for cat in known_categories:
            if u == cat or u.startswith(cat+" "):
                category=cat
                channel=None
                break
        # Channel headings
        if " DINE IN" in u and not re.match(r"^(TOTAL|MIE GACOAN|MIE HOMPIMPA)",u):
            channel="DINE IN"
            continue
        if " TAKE AWAY" in u and not re.match(r"^(TOTAL|MIE GACOAN|MIE HOMPIMPA)",u):
            channel="TAKE AWAY"
            continue

        # Simple three-column menu rows: NAME QTY VALUE.
        m=re.match(r"^(.+?)\s+(\d[\d\.]*)\s+(\d[\d\.]*)$",line)
        if m and category and channel:
            name=m.group(1).strip()
            qty=num(m.group(2)); value=num(m.group(3))
            if not name.lower().startswith("total -") and qty>=0:
                rows.append({"Kategori":category,"Channel":channel,"Menu":name,
                             "Qty":qty,"Value":value})
    df=pd.DataFrame(rows)
    if df.empty: return df
    # Remove obvious subtotal lines accidentally captured.
    df=df[~df["Menu"].str.upper().str.startswith("TOTAL")]
    return df.drop_duplicates(["Kategori","Channel","Menu"],keep="first")

# Fallback parser for the first "Sales Menu" table when hierarchy parsing misses rows.
def parse_sales_menu_table(text):
    start=text.find("Sales Menu")
    end=text.find("Sales By Menu")
    sec=text[start:end if end!=-1 else len(text)]
    rows=[]
    for line in sec.splitlines():
        m=re.match(r"^(.+?)\s+(\d[\d\.]*)\s+([\d\.]+)",line.strip())
        if m:
            name=m.group(1).strip()
            qty=num(m.group(2))
            grand=num(m.group(3))
            if name and name.upper() not in {"MENU","TOTAL"}:
                rows.append({"Menu":name,"Qty":qty,"Grand Total":grand})
    return pd.DataFrame(rows)

def copy_box(title, text):
    # Native Streamlit code blocks include a copy-to-clipboard button.
    st.markdown(f"**{title}**")
    st.code(text if text else "(tidak ada data)", language="text")

if not pdf:
    st.markdown('<div class="info">Silakan upload 1 file PDF terlebih dahulu.</div>', unsafe_allow_html=True)
else:
    text=get_pdf_text(pdf)
    summary=parse_summary(text)

    st.markdown('<div class="section-title">Ringkasan PROMIX</div>', unsafe_allow_html=True)
    cols=st.columns(2)
    for i,(label,key) in enumerate([
        ("Sales Total","Sales Total"),("Net Sales","Net Sales"),
        ("Gross Sales","Gross Sales"),("Pax Total","Pax Total")
    ]):
        with cols[i%2]:
            st.markdown(
                f'<div class="card"><div class="small">{label}</div>'
                f'<div class="metric">{money(summary.get(key,0))}</div></div>',
                unsafe_allow_html=True)

    sales=parse_sales_by_menu(text)
    if sales.empty:
        fallback=parse_sales_menu_table(text)
        st.warning("Struktur kategori DINE IN/TAKE AWAY tidak terbaca sempurna. Data Sales Menu dasar tetap tersedia.")
        st.dataframe(fallback,use_container_width=True,hide_index=True)
    else:
        st.markdown('<div class="section-title">Preview Hasil per Kategori</div>', unsafe_allow_html=True)

        for cat in sales["Kategori"].drop_duplicates():
            with st.expander(cat.title(), expanded=False):
                c1,c2,c3=st.columns(3)
                for j,ch in enumerate(["DINE IN","TAKE AWAY","TOTAL"]):
                    d=sales[(sales["Kategori"]==cat)&(sales["Channel"]==ch)] if ch!="TOTAL" else sales[sales["Kategori"]==cat]
                    txt="\n".join(f"{r.Menu}\t{r.Qty}" for _,r in d.iterrows())
                    with [c1,c2,c3][j]:
                        copy_box(f"Copy {cat.title()} {ch.title()}",txt)

                show=sales[sales["Kategori"]==cat][["Menu","Channel","Qty","Value"]].copy()
                st.dataframe(show,use_container_width=True,hide_index=True)

    st.markdown('<div class="section-title">Usage Bahan / Gramasi / COST<br>CONTROLLING / MANAJER<br>ORDERING CONTROLLING</div>', unsafe_allow_html=True)

    st.info("Untuk menghitung Usage Bahan secara akurat, aplikasi membutuhkan Master Recipe/Gramasi: Menu → Bahan → pemakaian per porsi. Data penjualan sudah diambil dari PDF; gramasi tidak tercantum di laporan PDF ini.")

    recipe_file=st.file_uploader(
        "Upload Master Recipe / Gramasi (CSV)",
        type=["csv"],
        key="recipe"
    )

    if recipe_file:
        recipe=pd.read_csv(recipe_file)
        required={"Menu","Bahan","Usage","Satuan"}
        if required.issubset(recipe.columns):
            recipe["Usage"]=pd.to_numeric(recipe["Usage"],errors="coerce").fillna(0)
            merged=sales.merge(recipe,on="Menu",how="inner")
            merged["Total Usage"]=merged["Qty"]*merged["Usage"]

            usage=(merged.groupby(["Bahan","Satuan"],as_index=False)["Total Usage"]
                   .sum().rename(columns={"Total Usage":"Usage"}))
            usage["Usage"]=usage["Usage"].round(4)

            st.dataframe(usage,use_container_width=True,hide_index=True)
            copy_box("Copy Usage Bahan",
                     "\n".join(f"{r.Bahan}\t{r.Usage}\t{r.Satuan}" for _,r in usage.iterrows()))
        else:
            st.error("CSV harus memiliki kolom: Menu, Bahan, Usage, Satuan")
    else:
        st.markdown("""
        **Format Master Recipe CSV:**
        ```
        Menu,Bahan,Usage,Satuan
        MIE GACOAN,Mie,1,pcs
        MIE GACOAN,Kulit Pangsit,0.02,ball
        ```
        Setelah file recipe di-upload, sistem akan menghitung:
        **Qty penjualan × Usage per menu = total pemakaian bahan.**
        """)

    st.markdown('<div class="section-title">Data Copy-Paste</div>', unsafe_allow_html=True)
    if not sales.empty:
        copy_box("Copy Semua Data Penjualan",
                 "\n".join(f"{r.Menu}\t{r.Channel}\t{r.Qty}\t{r.Value}" for _,r in sales.iterrows()))

st.markdown("""<div class="footer-badge">Developed by KHAIRIL<br>PDF → Sales → Usage → Copy-Paste</div>""", unsafe_allow_html=True)
