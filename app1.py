import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from io import BytesIO
import base64

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="PROMIX PDF Reader",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #666;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("📄 PROMIX PDF Reader")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload PDF File",
        type=["pdf"],
        help="Pilih file PDF yang ingin dibaca"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    show_text = st.checkbox("Extract Text", value=True)
    show_metadata = st.checkbox("Show Metadata", value=True)
    viewer_height = st.slider("Viewer Height (px)", 400, 1200, 700, 50)

    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit")

# ====================== MAIN CONTENT ======================
st.markdown('<div class="main-header">📄 PROMIX PDF Reader</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload PDF dan baca langsung di browser</div>', unsafe_allow_html=True)

if uploaded_file is None:
    st.info("👈 Silakan upload file PDF di sidebar untuk mulai.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### ✅ Preview PDF")
        st.write("Lihat PDF langsung di browser tanpa download.")
    with col2:
        st.markdown("### 📝 Extract Text")
        st.write("Ekstrak teks dari PDF untuk dicopy atau diunduh.")
    with col3:
        st.markdown("### ℹ️ Metadata")
        st.write("Lihat informasi dokumen (judul, author, halaman, dll).")

else:
    pdf_bytes = uploaded_file.getvalue()
    
    tab1, tab2, tab3 = st.tabs(["📖 PDF Viewer", "📝 Extracted Text", "ℹ️ Metadata"])

    # ---------- TAB 1: PDF VIEWER ----------
    with tab1:
        try:
            st.pdf(pdf_bytes, height=viewer_height)
        except Exception:
            st.warning("Menggunakan fallback PDF viewer.")
            b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f'''
                <iframe 
                    src="data:application/pdf;base64,{b64}" 
                    width="100%" 
                    height="{viewer_height}px" 
                    type="application/pdf"
                    style="border: none; border-radius: 8px;">
                </iframe>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)

    # ---------- TAB 2: EXTRACT TEXT ----------
    with tab2:
        if show_text:
            with st.spinner("Mengekstrak teks dari PDF..."):
                try:
                    text_content = []
                    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                        for i, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text:
                                text_content.append(f"--- Halaman {i+1} ---\n{page_text}\n")
                    
                    full_text = "\n".join(text_content)
                    
                    if full_text.strip():
                        st.text_area(
                            "Teks yang diekstrak:",
                            full_text,
                            height=500,
                            key="extracted_text"
                        )
                        
                        st.download_button(
                            label="⬇️ Download Teks (.txt)",
                            data=full_text,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_extracted.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("Tidak ada teks yang bisa diekstrak. PDF mungkin berbasis gambar/scan.")
                except Exception as e:
                    st.error(f"Gagal mengekstrak teks: {e}")
        else:
            st.info("Centang **Extract Text** di sidebar untuk menampilkan teks.")

    # ---------- TAB 3: METADATA ----------
    with tab3:
        if show_metadata:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                meta = doc.metadata or {}
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Informasi Dokumen")
                    st.write(f"**Judul:** {meta.get('title') or '-'}")
                    st.write(f"**Author:** {meta.get('author') or '-'}")
                    st.write(f"**Subject:** {meta.get('subject') or '-'}")
                    st.write(f"**Creator:** {meta.get('creator') or '-'}")
                
                with col2:
                    st.subheader("Detail File")
                    st.write(f"**Jumlah Halaman:** {len(doc)}")
                    st.write(f"**Ukuran File:** {len(pdf_bytes) / 1024:.1f} KB")
                    st.write(f"**Producer:** {meta.get('producer') or '-'}")
                    st.write(f"**Format:** PDF")
                
                doc.close()
            except Exception as e:
                st.error(f"Gagal membaca metadata: {e}")
        else:
            st.info("Centang **Show Metadata** di sidebar untuk menampilkan informasi.")

st.markdown("---")
st.caption("PROMIX PDF Reader • Built with Streamlit")
