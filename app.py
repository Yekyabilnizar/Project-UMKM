"""
PajakSeller — situs multi-halaman (Streamlit).
Kalkulator + artikel + halaman info dalam satu tautan.
Tambah artikel baru: cukup buat file  konten/artikel-NAMA.md  (baris pertama: # Judul).
"""
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="PajakSeller — Kalkulator & Panduan Pajak Penjual Online", page_icon="🧾",
                   layout="wide", initial_sidebar_state="expanded")

KONTEN = Path(__file__).parent / "konten"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, button, input {font-family:'Inter','Segoe UI',sans-serif;}
.stApp {background:radial-gradient(1000px 500px at 90% -8%, rgba(99,102,241,.12), transparent 60%),
        radial-gradient(900px 500px at -5% 5%, rgba(20,184,166,.14), transparent 58%), #f4f7fb;}
[data-testid="stAppDeployButton"], [data-testid="stToolbarActions"], #MainMenu, footer {display:none !important;}
.doc h1 {font-weight:800; letter-spacing:-.02em; color:#0b1f3a;}
.doc {background:#fff; border:1px solid #e3e9f3; border-radius:18px; padding:8px 34px 26px 34px; box-shadow:0 6px 18px rgba(15,23,42,.06); max-width:860px; margin:0 auto;}
.doc blockquote {background:#ecfeff; border-left:5px solid #0f766e; border-radius:10px; padding:4px 16px; margin:16px 0;}
</style>
""", unsafe_allow_html=True)


def judul(path: Path) -> str:
    for baris in path.read_text(encoding="utf-8").splitlines():
        if baris.startswith("# "):
            return baris[2:].strip()
    return path.stem


def buat_halaman(path: Path, artikel: bool = False):
    def render():
        st.markdown('<div class="doc">', unsafe_allow_html=True)
        st.markdown(path.read_text(encoding="utf-8"))
        st.markdown('</div>', unsafe_allow_html=True)
        if artikel:
            st.write("")
            st.page_link("kalkulator.py", label="Hitung pajak Anda di kalkulator", icon="🧮")
        st.caption("Informasi ini bersifat edukasi, bukan nasihat pajak resmi. Verifikasi ke pajak.go.id.")
    return render


artikel = [st.Page(buat_halaman(p, True), title=judul(p)[:48], url_path=p.stem.replace(" ", "-"), icon="📰")
           for p in sorted(KONTEN.glob("artikel-*.md"), reverse=True)]
info = [st.Page(buat_halaman(KONTEN / f), title=t, url_path=u, icon=i)
        for f, t, u, i in [("tentang.md", "Tentang & Kontak", "tentang", "👤"),
                           ("privasi.md", "Kebijakan Privasi", "privasi", "🔒")] if (KONTEN / f).exists()]

menu = {"Kalkulator": [st.Page("kalkulator.py", title="Kalkulator Pajak", icon="🧮", default=True)]}
if artikel: menu["Artikel"] = artikel
if info: menu["Info"] = info

try:
    nav = st.navigation(menu, position="top")
except TypeError:           # versi Streamlit lama: menu di sidebar
    nav = st.navigation(menu)
nav.run()
