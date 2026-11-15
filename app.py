"""
PajakSeller — Kalkulator Pajak Penjual Online & UMKM (Streamlit)
Jalankan: streamlit run app.py
"""
import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pajak_engine import ATURAN, SUBJEK, BULAN, hitung_pajak, kurva_pajak, rp, pct

# ------------------------------------------------------------------
# KONFIGURASI
# ------------------------------------------------------------------
FASTWORK_URL = ""          # isi tautan listing Fastwork Anda
NAMA_APP = "PajakSeller"
NAMA_PEMBUAT = "Yeky Abil Nizar"                      # ganti sesuai nama Anda
URL_PEMBUAT = "https://github.com/Yekyabilnizar"      # kosongkan "" jika tidak ingin ada tautan

st.set_page_config(page_title=f"{NAMA_APP} — Kalkulator Pajak Penjual Online & UMKM", page_icon="🧾",
                   layout="wide", initial_sidebar_state="expanded")

NAVY, TEAL, BLUE, RED, AMBER, GREEN, SLATE, VIOLET = (
    "#0b1f3a", "#0f766e", "#2563eb", "#dc2626", "#f59e0b", "#16a34a", "#64748b", "#7c3aed")

# ------------------------------------------------------------------
# GAYA (CSS)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, button, input, textarea, [class*="css"] {font-family:'Inter','Segoe UI',Roboto,sans-serif;}
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"], .stDeployButton {display:none !important;}
[data-testid="stHeader"] {background:transparent;}
/* Pastikan tombol buka/tutup panel input selalu terlihat */
[data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"] {display:flex !important; visibility:visible !important; opacity:1 !important;
    z-index:999999; background:#0f766e; border-radius:10px; box-shadow:0 4px 14px rgba(15,118,110,.35);}
[data-testid="stSidebarCollapsedControl"] button, [data-testid="stExpandSidebarButton"] button,
[data-testid="collapsedControl"] button {color:#fff !important;}
[data-testid="stSidebarCollapsedControl"] svg, [data-testid="stExpandSidebarButton"] svg,
[data-testid="collapsedControl"] svg {fill:#fff !important; color:#fff !important;}

/* Latar halaman: gradasi lembut */
.stApp {background:
    radial-gradient(1100px 520px at 92% -8%, rgba(99,102,241,.13), transparent 60%),
    radial-gradient(900px 520px at -6% 6%, rgba(20,184,166,.15), transparent 58%),
    radial-gradient(800px 600px at 50% 110%, rgba(245,158,11,.08), transparent 60%),
    #f4f7fb;}
.block-container {padding-top:1.2rem; padding-bottom:4rem; max-width:1320px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#ffffff 0%,#f1f7f6 100%); border-right:1px solid #dbe7e5;}
[data-testid="stSidebar"] .block-container {padding-top:1rem;}

/* Hero */
.hero {position:relative; overflow:hidden; color:#fff; border-radius:22px; padding:30px 36px; margin-bottom:20px;
       background:linear-gradient(118deg,#0b1f3a 0%,#1e3a8a 42%,#0f766e 100%);
       box-shadow:0 18px 40px rgba(30,58,138,.28);}
.hero:before {content:""; position:absolute; right:-70px; top:-110px; width:340px; height:340px; border-radius:50%;
              background:radial-gradient(circle,rgba(94,234,212,.35),rgba(94,234,212,0) 68%);}
.hero:after {content:""; position:absolute; right:140px; bottom:-150px; width:300px; height:300px; border-radius:50%;
             background:radial-gradient(circle,rgba(129,140,248,.40),rgba(129,140,248,0) 68%);}
.hero > * {position:relative; z-index:1;}
.hero .eyebrow {display:inline-block; font-size:11px; letter-spacing:.16em; text-transform:uppercase; font-weight:700;
                color:#5eead4; background:rgba(94,234,212,.12); border:1px solid rgba(94,234,212,.3); padding:4px 12px; border-radius:999px;}
.hero h1 {margin:12px 0 6px 0; font-size:34px; font-weight:800; color:#fff; letter-spacing:-.025em; line-height:1.12;}
.hero p {margin:0; opacity:.9; font-size:14.5px; max-width:760px; line-height:1.6;}
.chip {display:inline-block; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.24); backdrop-filter:blur(4px);
       border-radius:999px; padding:5px 14px; font-size:11.5px; margin:16px 8px 0 0; font-weight:500;}

/* Kartu hasil utama */
.main-card {position:relative; overflow:hidden; border:1px solid #cdeee9; border-radius:20px; padding:24px 28px; height:100%;
            background:linear-gradient(135deg,#ffffff 0%,#effcf9 60%,#eef2ff 100%);
            box-shadow:0 10px 26px rgba(15,118,110,.12);}
.main-card:before {content:""; position:absolute; left:0; top:0; bottom:0; width:7px; background:linear-gradient(180deg,#14b8a6,#6366f1);}
.main-card .l {font-size:12px; letter-spacing:.09em; text-transform:uppercase; color:#0f766e; font-weight:700;}
.main-card .v {font-size:44px; font-weight:800; letter-spacing:-.03em; margin:6px 0 2px 0; line-height:1.1;
               background:linear-gradient(90deg,#0b1f3a,#0f766e 60%,#4f46e5); -webkit-background-clip:text; background-clip:text; color:transparent;}
.main-card .s {font-size:13px; color:#64748b;}
.main-card .row {display:flex; justify-content:space-between; align-items:center; padding:11px 0; border-top:1px dashed #cfe3e0; font-size:13.5px; color:#334155;}
.main-card .row:first-of-type {margin-top:16px;}
.main-card .row b {font-weight:700; color:#0f172a;}
.pill {display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700;}
.pill.bad {background:#fee2e2; color:#b91c1c;} .pill.good {background:#dcfce7; color:#15803d;} .pill.neutral {background:#e0e7ff; color:#4338ca;}

/* KPI */
.kpi {position:relative; overflow:hidden; border:1px solid #e2e8f0; border-radius:18px; padding:18px 20px; height:100%;
      box-shadow:0 4px 14px rgba(15,23,42,.06); transition:transform .18s, box-shadow .18s;}
.kpi:before {content:""; position:absolute; left:0; right:0; top:0; height:5px; background:var(--ac,#0f766e);}
.kpi:hover {transform:translateY(-3px); box-shadow:0 14px 28px rgba(15,23,42,.12);}
.kpi .top {display:flex; align-items:center; gap:10px;}
.kpi .ic {width:34px; height:34px; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:17px;
          box-shadow:inset 0 0 0 1px rgba(15,23,42,.05);}
.kpi .l {font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; color:#64748b; font-weight:700;}
.kpi .v {font-size:23px; font-weight:800; color:#0f172a; margin-top:12px; line-height:1.15; letter-spacing:-.015em;}
.kpi .s {font-size:12px; color:#7b8aa0; margin-top:5px;}
.kpi.good .v {color:#15803d;} .kpi.bad .v {color:#be123c;}

/* Progress */
.prog-card {border:1px solid #e0e7ff; border-radius:20px; padding:22px 26px; height:100%;
            background:linear-gradient(135deg,#ffffff 0%,#f5f7ff 100%); box-shadow:0 10px 26px rgba(79,70,229,.10);}
.prog-card h4 {margin:0 0 16px 0; font-size:12px; letter-spacing:.09em; text-transform:uppercase; color:#4f46e5; font-weight:700;}
.prog {margin-bottom:18px;} .prog:last-child {margin-bottom:0;}
.prog .t {display:flex; justify-content:space-between; font-size:13px; margin-bottom:7px; color:#334155; font-weight:600;}
.prog .t span {font-weight:500; color:#64748b;}
.bar {height:11px; background:#e6ebf5; border-radius:999px; overflow:hidden; box-shadow:inset 0 1px 2px rgba(15,23,42,.08);}
.bar i {display:block; height:100%; border-radius:999px;}

/* Catatan */
.note {border-radius:14px; padding:12px 18px; margin:10px 0; font-size:13.5px; border-left:6px solid; line-height:1.55; box-shadow:0 2px 8px rgba(15,23,42,.04);}
.n-ok {background:linear-gradient(90deg,#ecfdf5,#fff); border-color:#10b981;}
.n-info {background:linear-gradient(90deg,#eff6ff,#fff); border-color:#3b82f6;}
.n-warn {background:linear-gradient(90deg,#fffbeb,#fff); border-color:#f59e0b;}
.n-danger {background:linear-gradient(90deg,#fef2f2,#fff); border-color:#ef4444;}

/* Insight */
.ins {display:flex; gap:14px; align-items:flex-start; padding:12px 0; border-bottom:1px solid #eef2f7; font-size:13.5px; line-height:1.5; color:#334155;}
.ins:last-child {border-bottom:none;}
.ins .d {flex:0 0 34px; height:34px; border-radius:11px; background:linear-gradient(135deg,#ccfbf1,#e0e7ff); display:flex; align-items:center; justify-content:center; font-size:16px;}

/* Judul bagian */
.sect {font-size:15.5px; font-weight:700; color:#0f172a; margin:0 0 2px 0; display:flex; align-items:center;}
.sect:before {content:""; display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:10px;
              background:linear-gradient(135deg,#14b8a6,#6366f1);}
.sub {font-size:12.5px; color:#64748b; margin:0 0 8px 20px;}

/* Container kartu grafik */
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.sect) {background:#fff; border:1px solid #e3e9f3 !important; box-shadow:0 6px 18px rgba(15,23,42,.06);}

/* Tab bentuk pil */
.stTabs [data-baseweb="tab-list"] {gap:8px; border-bottom:none; padding:2px 0 10px 0;}
.stTabs [data-baseweb="tab"] {padding:9px 20px; font-weight:600; color:#475569; border-radius:999px; background:#fff; border:1px solid #e2e8f0; height:auto;}
.stTabs [aria-selected="true"] {background:linear-gradient(135deg,#0f766e,#2563eb) !important; color:#fff !important; border-color:transparent !important;
                                box-shadow:0 6px 16px rgba(37,99,235,.30);}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display:none;}

/* Tombol unduh */
.stDownloadButton button {background:linear-gradient(135deg,#0f766e,#2563eb); color:#fff; border:none; border-radius:12px; font-weight:600; padding:.5rem 1.1rem;
                          box-shadow:0 6px 14px rgba(37,99,235,.25);}
.stDownloadButton button:hover {filter:brightness(1.08); color:#fff;}
.stDownloadButton button p {color:#fff;}

/* Sidebar */
.side-title {font-size:21px; font-weight:800; color:#0b1f3a; letter-spacing:-.015em; margin-bottom:2px;}
.side-sec {display:inline-block; font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:#0f766e; font-weight:700;
           background:#d9f6f1; padding:5px 12px; border-radius:8px; margin:22px 0 6px 0;}

/* Badge pembuat (kanan bawah, di sebelah kiri tombol Manage app) */
.credit {position:fixed; bottom:14px; right:190px; z-index:999990; background:linear-gradient(135deg,#0b1f3a,#1e3a8a); color:#e2e8f0;
         padding:9px 16px; border-radius:999px; font-size:12.5px; font-weight:500; letter-spacing:.01em;
         box-shadow:0 8px 20px rgba(11,31,58,.32); border:1px solid rgba(255,255,255,.14); white-space:nowrap;}
.credit b {color:#5eead4; font-weight:700;}
.credit a {color:#5eead4 !important; font-weight:700; text-decoration:none;}
.credit a:hover {text-decoration:underline;}
@media (max-width:700px) {.credit {right:12px; bottom:62px; font-size:11.5px; padding:7px 13px;}
                          .hero {padding:22px 20px;} .hero h1 {font-size:26px;} .main-card .v {font-size:34px;}}

.disc {font-size:12px; color:#64748b; line-height:1.7; background:#fff; border:1px solid #e3e9f3; border-radius:16px; margin-top:34px; padding:16px 20px;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# FUNGSI BANTU
# ------------------------------------------------------------------
def idn(x, dec=1):
    """Format angka gaya Indonesia: 1234.5 -> 1.234,5"""
    return f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def short(x):
    """Rupiah ringkas: Rp 12,5 jt / Rp 4,8 M"""
    a = abs(x)
    sign = "-" if x < 0 else ""
    if a >= 1e12: return f"{sign}Rp {idn(a/1e12,2)} T"
    if a >= 1e9:  return f"{sign}Rp {idn(a/1e9,2)} M"
    if a >= 1e6:  return f"{sign}Rp {idn(a/1e6,1)} jt"
    if a >= 1e3:  return f"{sign}Rp {idn(a/1e3,0)} rb"
    return f"{sign}Rp {idn(a,0)}"


ACCENT = {"#dbeafe": "#2563eb", "#ede9fe": "#7c3aed", "#dcfce7": "#16a34a", "#fef3c7": "#f59e0b"}


def kpi(label, value, sub="", icon="💰", bg="#ecfeff", cls=""):
    ac = ACCENT.get(bg, "#0f766e")
    return (f'<div class="kpi {cls}" style="--ac:{ac}; background:linear-gradient(180deg,{bg}99 0%,#ffffff 62%)">'
            f'<div class="top"><div class="ic" style="background:{bg}">{icon}</div>'
            f'<div class="l">{label}</div></div><div class="v">{value}</div><div class="s">{sub}</div></div>')


def progress(label, used, total, hint=""):
    p = 0 if total == 0 else min(used / total, 1) * 100
    g1, g2 = ("#34d399", "#059669") if p < 70 else (("#fcd34d", "#f59e0b") if p < 95 else ("#fb7185", "#e11d48"))
    return (f'<div class="prog"><div class="t">{label}<span>{hint}</span></div>'
            f'<div class="bar"><i style="width:{p:.1f}%; background:linear-gradient(90deg,{g1},{g2})"></i></div></div>')


def show_chart(fig):
    cfg = {"displayModeBar": False, "scrollZoom": False, "doubleClick": "reset", "showAxisDragHandles": False}
    try:
        st.plotly_chart(fig, width="stretch", config=cfg)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config=cfg)


def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def style(fig, h=330, ytitle=None, legend=True):
    fig.update_layout(
        template="plotly_white", height=h, margin=dict(l=4, r=8, t=40 if legend else 12, b=4),
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, font=dict(size=12)) if legend else dict(visible=False),
        showlegend=legend, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(241,245,249,.55)",
        separators=",.", hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#e2e8f0"), bargap=0.28,
        dragmode=False)   # kunci zoom/geser agar tampilan tidak berubah tanpa sengaja
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont=dict(size=11), fixedrange=True)
    fig.update_yaxes(gridcolor="#eef2f7", zeroline=False, title_text=ytitle, tickfont=dict(size=11), fixedrange=True)
    return fig


def card_title(judul, sub=""):
    st.markdown(f'<div class="sect">{judul}</div><div class="sub">{sub}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cached_kurva(subjek, tahun):
    return kurva_pajak(subjek, tahun=tahun)

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown(f'<div class="side-title">🧾 {NAMA_APP}</div>', unsafe_allow_html=True)
    st.caption("Estimasi pajak toko online & UMKM")

    st.markdown('<div class="side-sec">1 · Profil usaha</div>', unsafe_allow_html=True)
    subjek = st.selectbox("Bentuk usaha", SUBJEK)
    tahun = st.selectbox("Tahun pajak", [2026, 2027, 2028, 2029])
    transisi, surat = False, True
    if subjek.startswith("CV"):
        transisi = st.checkbox("Masih masa transisi PPh final 0,5%",
                               help="Hanya untuk CV/Firma/PT yang sudah memakai fasilitas sebelum aturan baru dan belum berakhir masanya.")
    porsi_mp = st.slider("Omzet lewat marketplace (%)", 0, 100, 70, 5)
    if subjek == "Orang Pribadi":
        surat = st.checkbox("Sudah kirim surat pernyataan omzet ≤ Rp500 juta", value=True,
                            help="Tanpa surat ini, marketplace tetap memungut PPh 22 sebesar 0,5%.")

    st.markdown('<div class="side-sec">2 · Omzet</div>', unsafe_allow_html=True)
    mode = st.radio("Cara input omzet", ["Otomatis", "Manual per bulan"], horizontal=True, label_visibility="collapsed")
    if mode == "Otomatis":
        avg = st.number_input("Omzet bulan pertama (Rp)", min_value=0, value=40_000_000, step=5_000_000)
        st.caption(rp(avg))
        growth = st.slider("Pertumbuhan per bulan (%)", -10.0, 20.0, 3.0, 0.5)
        omzet = [round(avg * (1 + growth / 100) ** i) for i in range(12)]
    else:
        base = pd.DataFrame({"Bulan": BULAN, "Omzet (Rp)": [40_000_000] * 12})
        edit = st.data_editor(base, hide_index=True, disabled=["Bulan"], key="editor",
                              column_config={"Omzet (Rp)": st.column_config.NumberColumn(format="%d", min_value=0, step=1_000_000)})
        omzet = [float(x or 0) for x in edit["Omzet (Rp)"]]

    st.markdown('<div class="side-sec">3 · Biaya</div>', unsafe_allow_html=True)
    hpp = st.slider("HPP (% omzet)", 0, 95, 55)
    fee = st.slider("Biaya marketplace (%)", 0.0, 30.0, 9.0, 0.5,
                    help="Komisi, biaya layanan, gratis ongkir, voucher. Dihitung dari omzet yang lewat marketplace.")
    ads = st.slider("Iklan (% omzet)", 0.0, 30.0, 5.0, 0.5)
    fix = st.number_input("Biaya tetap per bulan (Rp)", min_value=0, value=2_000_000, step=500_000)
    st.caption(rp(fix))

    if FASTWORK_URL:
        st.divider()
        st.markdown(f"💼 Butuh analisis data penjualan lebih dalam? **[Pesan di Fastwork]({FASTWORK_URL})**")

# ------------------------------------------------------------------
# HITUNG
# ------------------------------------------------------------------
h = hitung_pajak(omzet, subjek, tahun=tahun, transisi_cv=transisi, porsi_marketplace=porsi_mp / 100,
                 surat_pernyataan=surat, hpp_pct=hpp / 100, biaya_mp_pct=fee / 100,
                 iklan_pct=ads / 100, biaya_tetap=fix)
df = h["tabel"]
tot = df.sum(numeric_only=True)
is_op = subjek == "Orang Pribadi"
F = ATURAN["pph_final_umkm"]

# ------------------------------------------------------------------
# HERO
# ------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">Kalkulator perpajakan</div>
  <h1>Pajak Penjual Online & UMKM</h1>
  <p>Ketahui kewajiban pajak, kredit PPh 22 marketplace, dan laba bersih setelah pajak. Hasil langsung berubah saat Anda mengisi data di panel input (kiri). Jika panel tertutup, klik tombol hijau <b>»</b> di pojok kiri atas untuk membukanya kembali.</p>
  <span class="chip">PP 20/2026</span><span class="chip">PMK 37/2025</span>
  <span class="chip">Aturan per {ATURAN['diperbarui']}</span><span class="chip">Estimasi, bukan nasihat pajak</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# HASIL UTAMA + PROGRES
# ------------------------------------------------------------------
s = h["selisih"]
if s > 0:
    status = f'<span class="pill bad">Kurang bayar {rp(s)}</span>'
elif s < 0:
    status = f'<span class="pill good">Lebih bayar {rp(-s)}</span>'
else:
    status = '<span class="pill neutral">Tidak ada selisih</span>'

col_a, col_b = st.columns([1.15, 1], gap="medium")
with col_a:
    st.markdown(f"""
    <div class="main-card">
      <div class="l">Estimasi pajak penghasilan setahun</div>
      <div class="v">{rp(h['pajak_tahun'])}</div>
      <div class="s">{h['skema']} · {pct(h['tarif_efektif_omzet'])} dari omzet</div>
      <div class="row"><span>PPh 22 dipungut marketplace</span><b>{rp(h['pph22_total'])}</b></div>
      <div class="row"><span>Status setelah kredit PPh 22</span>{status}</div>
      <div class="row"><span>Rata-rata pajak per bulan</span><b>{rp(h['pajak_tahun']/12)}</b></div>
    </div>""", unsafe_allow_html=True)
with col_b:
    bars = ""
    if is_op:
        bars += progress("Fasilitas bebas PPh Rp500 juta", min(h["total_omzet"], F["bebas_pajak_op"]), F["bebas_pajak_op"],
                         f"{short(min(h['total_omzet'], F['bebas_pajak_op']))} terpakai")
    bars += progress("Batas omzet PPh final Rp4,8 miliar", h["total_omzet"], F["batas_omzet"],
                     f"{short(h['total_omzet'])} dari Rp 4,8 M")
    bars += progress("Beban pajak terhadap laba", max(0, h["pajak_tahun"]),
                     max(1, h["laba_sebelum_pajak"]) if h["laba_sebelum_pajak"] > 0 else max(1, h["pajak_tahun"]),
                     "dari laba sebelum pajak" if h["laba_sebelum_pajak"] > 0 else "usaha rugi")
    st.markdown(f'<div class="prog-card"><h4>Pemakaian batas &amp; beban pajak</h4>{bars}</div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------
# KPI
# ------------------------------------------------------------------
c = st.columns(4, gap="medium")
c[0].markdown(kpi("Total omzet", rp(h["total_omzet"]), f"Rata-rata {short(h['total_omzet']/12)} / bulan", "📈", "#dbeafe"), unsafe_allow_html=True)
c[1].markdown(kpi("Laba sebelum pajak", rp(h["laba_sebelum_pajak"]), "Omzet − HPP − biaya", "🧮", "#ede9fe",
                  "good" if h["laba_sebelum_pajak"] >= 0 else "bad"), unsafe_allow_html=True)
c[2].markdown(kpi("Laba bersih", rp(h["laba_bersih"]), f"Margin bersih {pct(h['margin_bersih'])}", "💎", "#dcfce7",
                  "good" if h["laba_bersih"] >= 0 else "bad"), unsafe_allow_html=True)
if is_op:
    c[3].markdown(kpi("Sisa omzet bebas PPh", rp(h["sisa_bebas"]), "Dari fasilitas Rp500 juta", "🎁", "#fef3c7"), unsafe_allow_html=True)
else:
    c[3].markdown(kpi("Fasilitas Rp500 juta", "Tidak tersedia", "Khusus Orang Pribadi", "🎁", "#fef3c7"), unsafe_allow_html=True)

for k, m in h["catatan"]:
    st.markdown(f'<div class="note n-{k}">{m}</div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------
# TAB
# ------------------------------------------------------------------
t1, t2, t3, t4, t5 = st.tabs(["Ringkasan", "Rincian bulanan", "Simulasi", "Bandingkan bentuk usaha", "Dasar hukum & FAQ"])

# ============ RINGKASAN ============
with t1:
    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(border=True):
            card_title("Omzet dan laba per bulan", "Dalam juta rupiah")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.Bulan, y=df.Omzet / 1e6, name="Omzet", marker_color="#818cf8",
                                 hovertemplate="%{x}<br>Omzet: Rp %{y:,.1f} jt<extra></extra>"))
            fig.add_trace(go.Bar(x=df.Bulan, y=df.Laba_Sebelum_Pajak / 1e6, name="Laba sebelum pajak", marker_color="#14b8a6",
                                 hovertemplate="%{x}<br>Laba: Rp %{y:,.1f} jt<extra></extra>"))
            fig.update_layout(barmode="group")
            show_chart(style(fig, ytitle="Juta Rp"))
    with b:
        with st.container(border=True):
            card_title("Pajak per bulan", "Dalam ribu rupiah")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.Bulan, y=df.PPh_Final / 1e3, name="PPh final", marker_color="#f43f5e",
                                 hovertemplate="%{x}<br>PPh final: Rp %{y:,.0f} rb<extra></extra>"))
            fig.add_trace(go.Bar(x=df.Bulan, y=df.PPh22_Dipungut / 1e3, name="PPh 22 dipungut", marker_color="#fbbf24",
                                 hovertemplate="%{x}<br>PPh 22: Rp %{y:,.0f} rb<extra></extra>"))
            fig.update_layout(barmode="group")
            if (df.PPh_Final.sum() + df.PPh22_Dipungut.sum()) == 0:
                fig.add_annotation(text="Tidak ada pajak terutang pada periode ini", showarrow=False,
                                   xref="paper", yref="paper", x=0.5, y=0.5, font=dict(size=14, color="#94a3b8"))
            show_chart(style(fig, ytitle="Ribu Rp"))

    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(border=True):
            card_title("Ke mana perginya omzet Anda?", "Struktur biaya, pajak, dan laba bersih")
            komponen = [("HPP", tot.HPP, "#6366f1"), ("Biaya marketplace", tot.Biaya_Marketplace, "#fb923c"),
                        ("Iklan", tot.Iklan, "#a855f7"), ("Biaya tetap", tot.Biaya_Tetap, "#38bdf8"),
                        ("Pajak", h["pajak_tahun"], "#f43f5e"), ("Laba bersih", max(0, h["laba_bersih"]), "#10b981")]
            komponen = sorted(komponen, key=lambda z: z[1])
            total_o = max(h["total_omzet"], 1)
            fig = go.Figure(go.Bar(
                y=[k[0] for k in komponen], x=[k[1] / 1e6 for k in komponen], orientation="h",
                marker_color=[k[2] for k in komponen],
                text=[f"{short(k[1])}  ·  {idn(k[1]/total_o*100,1)}%" for k in komponen],
                textposition="outside", cliponaxis=False,
                hovertemplate="%{y}: Rp %{x:,.1f} jt<extra></extra>"))
            maks = max([k[1] for k in komponen] + [1]) / 1e6
            fig.update_xaxes(range=[0, maks * 1.55], showgrid=True, gridcolor="#eef2f7", title_text="Juta Rp")
            fig.update_yaxes(showgrid=False)
            show_chart(style(fig, h=330, legend=False))
    with b:
        with st.container(border=True):
            card_title("Dari omzet ke laba bersih", "Alur setahun dalam juta rupiah")
            langkah = [("Omzet", h["total_omzet"]), ("HPP", -tot.HPP), ("Biaya marketplace", -tot.Biaya_Marketplace),
                       ("Iklan", -tot.Iklan), ("Biaya tetap", -tot.Biaya_Tetap), ("Pajak", -h["pajak_tahun"])]
            xs = [n for n, _ in langkah] + ["Laba bersih"]
            ys = [v / 1e6 for _, v in langkah] + [0]
            teks = [short(v) for _, v in langkah] + [short(h["laba_bersih"])]
            fig = go.Figure(go.Waterfall(
                x=xs, y=ys, measure=["absolute"] + ["relative"] * 5 + ["total"],
                text=teks, textposition="outside", cliponaxis=False,
                connector=dict(line=dict(color="#cbd5e1", width=1)),
                increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color="#f87171")),
                totals=dict(marker=dict(color=BLUE)),
                hovertemplate="%{x}: Rp %{y:,.1f} jt<extra></extra>"))
            fig.update_xaxes(tickangle=-25)
            show_chart(style(fig, h=330, ytitle="Juta Rp", legend=False))

    a, b = st.columns([1.35, 1], gap="medium")
    with a:
        with st.container(border=True):
            card_title("Omzet kumulatif sepanjang tahun", "Pantau kapan Anda mendekati batas fasilitas")
            cum = df.Omzet_Kumulatif / 1e6
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.Bulan, y=cum, mode="lines+markers", name="Omzet kumulatif",
                                     line=dict(color=TEAL, width=3), marker=dict(size=7),
                                     fill="tozeroy", fillcolor="rgba(15,118,110,.12)",
                                     hovertemplate="%{x}<br>Kumulatif: Rp %{y:,.1f} jt<extra></extra>"))
            ymax = float(cum.max()) if len(cum) else 0
            batas_list = [(F["bebas_pajak_op"] / 1e6, GREEN, "Bebas PPh Rp500 jt")] if is_op else []
            batas_list.append((F["batas_omzet"] / 1e6, RED, "Batas Rp4,8 M"))
            tampil_max = max(ymax * 1.15, 560)
            for yv, warna, label in batas_list:
                if yv <= tampil_max * 1.6:
                    fig.add_hline(y=yv, line_dash="dash", line_color=warna, line_width=1.6,
                                  annotation_text=label, annotation_position="top left",
                                  annotation_font=dict(color=warna, size=11))
                    tampil_max = max(tampil_max, yv * 1.12)
            fig.update_yaxes(range=[0, tampil_max])
            show_chart(style(fig, h=320, ytitle="Juta Rp", legend=False))
    with b:
        with st.container(border=True):
            card_title("Insight cepat", "Temuan otomatis dari data Anda")
            ins = []
            kena = df[df.PPh_Final > 0]
            if len(kena):
                ins.append(("🗓️", f"PPh final mulai terutang pada bulan <b>{kena.iloc[0].Bulan}</b>."))
            elif h["skema"].startswith("PPh Final"):
                ins.append(("✅", "Tidak ada bulan dengan PPh final terutang pada skenario ini."))
            mp_on = df[df.PPh22_Dipungut > 0]
            if len(mp_on):
                ins.append(("🛒", f"Marketplace mulai memungut PPh 22 pada bulan <b>{mp_on.iloc[0].Bulan}</b> (total {short(h['pph22_total'])} setahun)."))
            else:
                ins.append(("🛒", "Tidak ada pemungutan PPh 22 oleh marketplace pada skenario ini."))
            kontribusi = 1 - hpp / 100 - ads / 100 - (fee / 100) * (porsi_mp / 100)
            if kontribusi > 0 and fix > 0:
                ins.append(("⚖️", f"Titik impas operasional sekitar <b>{short(fix / kontribusi)}</b> omzet per bulan."))
            elif kontribusi <= 0:
                ins.append(("⚠️", "Biaya variabel Anda sudah melampaui omzet; usaha rugi di berapa pun omzetnya."))
            if h["laba_sebelum_pajak"] > 0:
                ins.append(("📊", f"Pajak mengambil <b>{idn(h['pajak_tahun']/h['laba_sebelum_pajak']*100,1)}%</b> dari laba sebelum pajak."))
            besar = max([("HPP", tot.HPP), ("Biaya marketplace", tot.Biaya_Marketplace), ("Iklan", tot.Iklan), ("Biaya tetap", tot.Biaya_Tetap)], key=lambda z: z[1])
            if besar[1] > 0:
                ins.append(("🔎", f"Komponen biaya terbesar: <b>{besar[0]}</b> ({idn(besar[1]/total_o*100,1)}% dari omzet)."))
            st.markdown("".join(f'<div class="ins"><div class="d">{i}</div><div>{t}</div></div>' for i, t in ins), unsafe_allow_html=True)

# ============ RINCIAN ============
with t2:
    with st.container(border=True):
        card_title("Rincian per bulan", "Seluruh komponen perhitungan, bisa diurutkan dengan klik judul kolom")
        tampil = df.copy().rename(columns=lambda c: c.replace("_", " "))
        kolom_rp = [c for c in tampil.columns if c != "Bulan"]
        show_df(tampil, column_config={c: st.column_config.NumberColumn(c, format="Rp %d") for c in kolom_rp})

        ringkas = pd.DataFrame({
            "Keterangan": ["Bentuk usaha", "Tahun pajak", "Skema pajak", "Total omzet", "Pajak penghasilan setahun",
                           "PPh 22 dipungut marketplace", "Kurang/(lebih) bayar", "Laba sebelum pajak", "Laba bersih"],
            "Nilai": [subjek, tahun, h["skema"], h["total_omzet"], h["pajak_tahun"], h["pph22_total"],
                      h["selisih"], h["laba_sebelum_pajak"], h["laba_bersih"]]})
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xw:
            ringkas.to_excel(xw, sheet_name="Ringkasan", index=False)
            df.to_excel(xw, sheet_name="Rincian Bulanan", index=False)
            for ws in xw.book.worksheets:
                for col in ws.columns:
                    ws.column_dimensions[col[0].column_letter].width = max(14, min(36, max(len(str(c.value or "")) for c in col) + 3))
                    for cell in col[1:]:
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0'
        d1, d2, _ = st.columns([1, 1, 3])
        d1.download_button("⬇️ Unduh Excel", buf.getvalue(), file_name="hasil_pajak_penjual_online.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        d2.download_button("⬇️ Unduh CSV", df.to_csv(index=False).encode("utf-8"), file_name="rincian_bulanan.csv", mime="text/csv")

# ============ SIMULASI ============
with t3:
    st.caption("Omzet diasumsikan merata tiap bulan. Bintang merah menandai posisi Anda sekarang.")
    a, b = st.columns(2, gap="medium")
    kurva = {n: cached_kurva(n, tahun) for n in ["Orang Pribadi", "PT Perorangan"]}
    with a:
        with st.container(border=True):
            card_title("Pajak tahunan vs omzet tahunan", "Dalam juta rupiah")
            fig = go.Figure()
            for nama, warna in [("Orang Pribadi", TEAL), ("PT Perorangan", BLUE)]:
                x2, y2 = kurva[nama]
                fig.add_trace(go.Scatter(x=[v / 1e6 for v in x2], y=[v / 1e6 for v in y2], name=nama,
                                         line=dict(color=warna, width=3),
                                         hovertemplate="Omzet Rp %{x:,.0f} jt<br>Pajak Rp %{y:,.1f} jt<extra></extra>"))
            if h["skema"].startswith("PPh Final"):
                fig.add_trace(go.Scatter(x=[h["total_omzet"] / 1e6], y=[h["pajak_tahun"] / 1e6], mode="markers", name="Posisi Anda",
                                         marker=dict(size=15, color=RED, symbol="star", line=dict(color="white", width=1))))
            fig.update_xaxes(title_text="Omzet setahun (juta Rp)")
            show_chart(style(fig, h=340, ytitle="Pajak (juta Rp)"))
    with b:
        with st.container(border=True):
            card_title("Tarif efektif", "Pajak sebagai persentase omzet")
            fig = go.Figure()
            for nama, warna in [("Orang Pribadi", TEAL), ("PT Perorangan", BLUE)]:
                x2, y2 = kurva[nama]
                ef = [(y / x * 100) if x else 0 for x, y in zip(x2, y2)]
                fig.add_trace(go.Scatter(x=[v / 1e6 for v in x2], y=ef, name=nama, line=dict(color=warna, width=3),
                                         hovertemplate="Omzet Rp %{x:,.0f} jt<br>Tarif efektif %{y:.2f}%<extra></extra>"))
            fig.update_xaxes(title_text="Omzet setahun (juta Rp)")
            show_chart(style(fig, h=340, ytitle="% dari omzet"))
    st.info("Orang Pribadi mendapat fasilitas Rp500 juta pertama bebas PPh, sehingga tarif efektifnya baru mendekati 0,5% pada omzet yang besar.")

# ============ BANDINGKAN ============
with t4:
    rows = []
    for sb in SUBJEK:
        r = hitung_pajak(omzet, sb, tahun=tahun, transisi_cv=False, porsi_marketplace=porsi_mp / 100,
                         surat_pernyataan=surat, hpp_pct=hpp / 100, biaya_mp_pct=fee / 100,
                         iklan_pct=ads / 100, biaya_tetap=fix)
        rows.append({"Bentuk usaha": sb, "Skema": r["skema"], "Pajak setahun": r["pajak_tahun"],
                     "Tarif efektif (% omzet)": r["tarif_efektif_omzet"] * 100, "Laba bersih": r["laba_bersih"]})
    cmp = pd.DataFrame(rows)
    with st.container(border=True):
        card_title("Pajak setahun per bentuk usaha", "Omzet, biaya, dan marketplace yang sama")
        fig = go.Figure(go.Bar(x=cmp["Bentuk usaha"], y=cmp["Pajak setahun"] / 1e6,
                               marker_color=[TEAL, BLUE, VIOLET, AMBER],
                               text=[short(v) for v in cmp["Pajak setahun"]], textposition="outside", cliponaxis=False,
                               hovertemplate="%{x}<br>Rp %{y:,.1f} jt<extra></extra>"))
        fig.update_yaxes(rangemode="tozero")
        show_chart(style(fig, h=360, ytitle="Juta Rp", legend=False))
    with st.container(border=True):
        card_title("Tabel perbandingan")
        show_df(cmp, column_config={
            "Pajak setahun": st.column_config.NumberColumn(format="Rp %d"),
            "Laba bersih": st.column_config.NumberColumn(format="Rp %d"),
            "Tarif efektif (% omzet)": st.column_config.NumberColumn(format="%.2f%%")})
    st.caption("CV/Firma/PT umum dihitung dengan PPh Badan tarif umum (perkiraan kasar dari laba). Bentuk usaha punya konsekuensi hukum lain, jadi jangan memutuskan hanya dari pajak.")

# ============ DASAR HUKUM ============
with t5:
    with st.container(border=True):
        card_title("Ringkasan aturan yang dipakai", "Sumber: DJP (pajak.go.id) dan peraturan terkait")
        aturan_tbl = pd.DataFrame([
            ["PPh final UMKM", "0,5% dari omzet; maksimal omzet Rp4,8 miliar per tahun", "PP 55/2022 jo. PP 20/2026"],
            ["Subjek PPh final 0,5%", "Orang Pribadi, PT Perorangan, Koperasi (CV/Firma/PT umum tidak lagi, kecuali masa transisi)", "PP 20/2026"],
            ["Bebas PPh Rp500 juta", "Omzet Rp500 juta pertama, khusus WP Orang Pribadi", "PP 55/2022 Pasal 60 ayat (2)"],
            ["PPh 22 marketplace", "0,5% dari omzet; OP sampai Rp500 juta dikecualikan dengan surat pernyataan", "PMK 37/2025"],
            ["Batas PKP", "Omzet di atas Rp4,8 miliar wajib dikukuhkan PKP", "UU PPN"],
            ["PPh Badan (CV/PT umum)", "Tarif 22%, dengan fasilitas Pasal 31E untuk omzet sampai Rp4,8 miliar", "UU PPh"]],
            columns=["Topik", "Ketentuan", "Dasar hukum"])
        show_df(aturan_tbl)
    with st.container(border=True):
        card_title("Pertanyaan umum")
        with st.expander("Apakah omzet di bawah Rp500 juta tetap harus lapor?"):
            st.write("Ya. Wajib pajak tetap melaporkan omzet dalam SPT Tahunan meski tidak ada PPh final yang terutang.")
        with st.expander("PPh 22 yang dipotong marketplace itu pajak tambahan?"):
            st.write("Tidak. Pemungutan itu dapat dikreditkan terhadap PPh final yang terutang, sehingga kalkulator ini mengurangkannya dari total pajak setahun.")
        with st.expander("Pajak final dihitung dari omzet atau laba?"):
            st.write("Dari omzet (peredaran bruto), bukan laba. Usaha yang rugi tetap membayar PPh final di atas batas bebas pajaknya.")
        with st.expander("Kapan pemungutan PPh 22 marketplace mulai berlaku?"):
            st.write(f"Pengaturan awal alat ini adalah bulan ke-{ATURAN['pph22_marketplace']['bulan_mulai_2026']} tahun 2026. "
                     "Sumber media menyebut tanggal berbeda, jadi cek pengumuman resmi DJP dan ubah di `pajak_engine.py` bila perlu.")

_nama = f'<a href="{URL_PEMBUAT}" target="_blank">{NAMA_PEMBUAT}</a>' if URL_PEMBUAT else f"<b>{NAMA_PEMBUAT}</b>"
st.markdown(f'<div class="credit">Created by {anonymass}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="disc"><b>Penting:</b> Hasil adalah <b>estimasi</b> untuk edukasi dan perencanaan, bukan nasihat pajak resmi.
Kondisi tertentu (penghasilan lain, pengecualian objek pajak, koreksi fiskal, PPN, dan lainnya) tidak tercakup.
Aturan pajak sering berubah; verifikasi ke <a href="https://www.pajak.go.id" target="_blank">pajak.go.id</a> atau konsultan pajak sebelum melapor.
Aturan terakhir diperbarui di alat ini: {ATURAN['diperbarui']}.</div>
""", unsafe_allow_html=True)
