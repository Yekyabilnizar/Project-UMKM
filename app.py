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
.block-container {padding-top:1.2rem; padding-bottom:3rem; max-width:1320px;}
[data-testid="stSidebar"] {background:#ffffff; border-right:1px solid #e2e8f0;}
[data-testid="stSidebar"] .block-container {padding-top:1rem;}

/* Hero */
.hero {position:relative; overflow:hidden; background:linear-gradient(115deg,#0b1f3a 0%,#0f4c5c 55%,#0f766e 100%);
       color:#fff; border-radius:20px; padding:26px 32px; margin-bottom:18px;
       box-shadow:0 12px 32px rgba(11,31,58,.22);}
.hero:after {content:""; position:absolute; right:-60px; top:-80px; width:300px; height:300px; border-radius:50%;
             background:radial-gradient(circle,rgba(255,255,255,.16),rgba(255,255,255,0) 70%);}
.hero .eyebrow {font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; opacity:.75; font-weight:600;}
.hero h1 {margin:6px 0 4px 0; font-size:30px; font-weight:800; color:#fff; letter-spacing:-.02em; line-height:1.15;}
.hero p {margin:0; opacity:.88; font-size:14.5px; max-width:720px;}
.chip {display:inline-block; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.22);
       border-radius:999px; padding:4px 13px; font-size:11.5px; margin:14px 8px 0 0; font-weight:500;}

/* Kartu */
.main-card {background:#fff; border:1px solid #e2e8f0; border-left:6px solid #0f766e; border-radius:18px;
            padding:22px 26px; box-shadow:0 2px 10px rgba(15,23,42,.05); height:100%;}
.main-card .l {font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#64748b; font-weight:700;}
.main-card .v {font-size:40px; font-weight:800; color:#0b1f3a; letter-spacing:-.02em; margin:6px 0 2px 0; line-height:1.1;}
.main-card .s {font-size:13px; color:#64748b;}
.main-card .row {display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-top:1px solid #f1f5f9; font-size:13.5px;}
.main-card .row:first-of-type {margin-top:14px;}
.main-card .row b {font-weight:700; color:#0f172a;}
.pill {display:inline-block; padding:3px 11px; border-radius:999px; font-size:12px; font-weight:700;}
.pill.bad {background:#fee2e2; color:#b91c1c;} .pill.good {background:#dcfce7; color:#15803d;} .pill.neutral {background:#e2e8f0; color:#475569;}

.kpi {background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:16px 18px; height:100%;
      box-shadow:0 1px 3px rgba(15,23,42,.04); transition:transform .15s, box-shadow .15s;}
.kpi:hover {transform:translateY(-2px); box-shadow:0 8px 20px rgba(15,23,42,.08);}
.kpi .top {display:flex; align-items:center; gap:8px;}
.kpi .ic {width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:15px;}
.kpi .l {font-size:11.5px; letter-spacing:.05em; text-transform:uppercase; color:#64748b; font-weight:600;}
.kpi .v {font-size:22px; font-weight:800; color:#0f172a; margin-top:10px; line-height:1.15; letter-spacing:-.01em;}
.kpi .s {font-size:12px; color:#94a3b8; margin-top:4px;}
.kpi.good .v {color:#15803d;} .kpi.bad .v {color:#b91c1c;}

/* Progress */
.prog-card {background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:20px 24px; height:100%;
            box-shadow:0 2px 10px rgba(15,23,42,.05);}
.prog-card h4 {margin:0 0 14px 0; font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:#64748b;}
.prog {margin-bottom:16px;} .prog:last-child {margin-bottom:0;}
.prog .t {display:flex; justify-content:space-between; font-size:13px; margin-bottom:6px; color:#334155; font-weight:600;}
.prog .t span {font-weight:500; color:#64748b;}
.bar {height:10px; background:#eef2f7; border-radius:999px; overflow:hidden;}
.bar i {display:block; height:100%; border-radius:999px;}

/* Catatan */
.note {border-radius:12px; padding:11px 16px; margin:8px 0; font-size:13.5px; border-left:5px solid; line-height:1.55;}
.n-ok {background:#f0fdf4; border-color:#22c55e;} .n-info {background:#eff6ff; border-color:#3b82f6;}
.n-warn {background:#fffbeb; border-color:#f59e0b;} .n-danger {background:#fef2f2; border-color:#ef4444;}

/* Insight */
.ins {display:flex; gap:12px; padding:11px 0; border-bottom:1px solid #f1f5f9; font-size:13.5px; line-height:1.5; color:#334155;}
.ins:last-child {border-bottom:none;} .ins .d {font-size:17px; line-height:1.3;}

/* Badge pembuat (kanan bawah, di sebelah kiri tombol Manage app) */
.credit {position:fixed; bottom:14px; right:190px; z-index:999990; background:#0b1f3a; color:#e2e8f0;
         padding:9px 16px; border-radius:999px; font-size:12.5px; font-weight:500; letter-spacing:.01em;
         box-shadow:0 6px 18px rgba(11,31,58,.28); border:1px solid rgba(255,255,255,.12); white-space:nowrap;}
.credit b {color:#5eead4; font-weight:700;}
.credit a {color:#5eead4 !important; font-weight:700; text-decoration:none;}
.credit a:hover {text-decoration:underline;}
@media (max-width:700px) {.credit {right:12px; bottom:62px; font-size:11.5px; padding:7px 13px;}}

/* Judul bagian */
.sect {font-size:15px; font-weight:700; color:#0f172a; margin:0 0 2px 0;}
.sub {font-size:12.5px; color:#64748b; margin:0 0 6px 0;}

/* Container, tab */
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px;}
.stTabs [data-baseweb="tab-list"] {gap:4px; border-bottom:1px solid #e2e8f0;}
.stTabs [data-baseweb="tab"] {padding:10px 18px; font-weight:600; color:#64748b; border-radius:10px 10px 0 0;}
.stTabs [aria-selected="true"] {color:#0f766e;}
.stTabs [data-baseweb="tab-highlight"] {background-color:#0f766e;}

/* Sidebar */
.side-title {font-size:19px; font-weight:800; color:#0b1f3a; letter-spacing:-.01em; margin-bottom:2px;}
.side-sec {font-size:11.5px; letter-spacing:.1em; text-transform:uppercase; color:#0f766e; font-weight:700; margin:20px 0 4px 0;}
.disc {font-size:12px; color:#64748b; line-height:1.65; border-top:1px solid #e2e8f0; margin-top:32px; padding-top:16px;}
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


def kpi(label, value, sub="", icon="💰", bg="#ecfeff", cls=""):
    return (f'<div class="kpi {cls}"><div class="top"><div class="ic" style="background:{bg}">{icon}</div>'
            f'<div class="l">{label}</div></div><div class="v">{value}</div><div class="s">{sub}</div></div>')


def progress(label, used, total, hint=""):
    p = 0 if total == 0 else min(used / total, 1) * 100
    warna = GREEN if p < 70 else (AMBER if p < 95 else RED)
    return (f'<div class="prog"><div class="t">{label}<span>{hint}</span></div>'
            f'<div class="bar"><i style="width:{p:.1f}%; background:{warna}"></i></div></div>')


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
        showlegend=legend, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
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
            fig.add_trace(go.Bar(x=df.Bulan, y=df.Omzet / 1e6, name="Omzet", marker_color="#93c5fd",
                                 hovertemplate="%{x}<br>Omzet: Rp %{y:,.1f} jt<extra></extra>"))
            fig.add_trace(go.Bar(x=df.Bulan, y=df.Laba_Sebelum_Pajak / 1e6, name="Laba sebelum pajak", marker_color=TEAL,
                                 hovertemplate="%{x}<br>Laba: Rp %{y:,.1f} jt<extra></extra>"))
            fig.update_layout(barmode="group")
            show_chart(style(fig, ytitle="Juta Rp"))
    with b:
        with st.container(border=True):
            card_title("Pajak per bulan", "Dalam ribu rupiah")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.Bulan, y=df.PPh_Final / 1e3, name="PPh final", marker_color=RED,
                                 hovertemplate="%{x}<br>PPh final: Rp %{y:,.0f} rb<extra></extra>"))
            fig.add_trace(go.Bar(x=df.Bulan, y=df.PPh22_Dipungut / 1e3, name="PPh 22 dipungut", marker_color=AMBER,
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
            komponen = [("HPP", tot.HPP, "#94a3b8"), ("Biaya marketplace", tot.Biaya_Marketplace, "#fb923c"),
                        ("Iklan", tot.Iklan, VIOLET), ("Biaya tetap", tot.Biaya_Tetap, "#64748b"),
                        ("Pajak", h["pajak_tahun"], RED), ("Laba bersih", max(0, h["laba_bersih"]), GREEN)]
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
st.markdown(f'<div class="credit">Created by {_nama}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="disc"><b>Penting:</b> Hasil adalah <b>estimasi</b> untuk edukasi dan perencanaan, bukan nasihat pajak resmi.
Kondisi tertentu (penghasilan lain, pengecualian objek pajak, koreksi fiskal, PPN, dan lainnya) tidak tercakup.
Aturan pajak sering berubah; verifikasi ke <a href="https://www.pajak.go.id" target="_blank">pajak.go.id</a> atau konsultan pajak sebelum melapor.
Aturan terakhir diperbarui di alat ini: {ATURAN['diperbarui']}.</div>
""", unsafe_allow_html=True)
