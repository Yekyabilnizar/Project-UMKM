"""
Kalkulator Pajak Penjual Online & UMKM — Dashboard Streamlit
Jalankan: streamlit run app.py
"""
import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from pajak_engine import ATURAN, SUBJEK, BULAN, hitung_pajak, kurva_pajak, rp, pct

# ------------------------------------------------------------------
# KONFIGURASI
# ------------------------------------------------------------------
FASTWORK_URL = ""   # isi tautan listing Fastwork Anda, mis. "https://fastwork.id/..."
NAMA_APP = "PajakSeller"

st.set_page_config(page_title="Kalkulator Pajak Penjual Online & UMKM", page_icon="🧾",
                   layout="wide", initial_sidebar_state="expanded")

TEAL, BLUE, RED, AMBER, GREEN, SLATE = "#0f766e", "#1d4ed8", "#dc2626", "#f59e0b", "#16a34a", "#64748b"

st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
.block-container{padding-top:1.4rem;max-width:1280px;}
html, body, [class*="css"]{font-family:'Inter','Segoe UI',Roboto,sans-serif;}
.hero{background:linear-gradient(120deg,#0f766e 0%,#1d4ed8 100%);color:#fff;border-radius:18px;
      padding:26px 30px;margin-bottom:18px;box-shadow:0 10px 30px rgba(29,78,216,.18);}
.hero h1{margin:0;font-size:28px;font-weight:800;color:#fff;letter-spacing:-.01em}
.hero p{margin:6px 0 0 0;opacity:.92;font-size:14px}
.badge{display:inline-block;background:rgba(255,255,255,.18);border-radius:999px;padding:3px 12px;
       font-size:11.5px;margin:10px 6px 0 0;}
.kpi{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:16px 18px;height:100%;
     box-shadow:0 1px 2px rgba(15,23,42,.04);}
.kpi .l{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:#64748b;font-weight:600}
.kpi .v{font-size:23px;font-weight:800;color:#0f172a;margin-top:6px;line-height:1.15}
.kpi .s{font-size:12px;color:#64748b;margin-top:4px}
.kpi.accent{background:linear-gradient(135deg,#ecfeff,#eff6ff);border-color:#a5f3fc}
.kpi.good .v{color:#15803d}.kpi.bad .v{color:#b91c1c}
.note{border-radius:12px;padding:11px 15px;margin:8px 0;font-size:13.5px;border-left:5px solid;line-height:1.5}
.n-ok{background:#f0fdf4;border-color:#22c55e}.n-info{background:#eff6ff;border-color:#3b82f6}
.n-warn{background:#fffbeb;border-color:#f59e0b}.n-danger{background:#fef2f2;border-color:#ef4444}
.sect{font-size:16px;font-weight:700;margin:22px 0 8px 0;color:#0f172a}
.disc{font-size:12px;color:#64748b;line-height:1.6;border-top:1px solid #e2e8f0;margin-top:26px;padding-top:14px}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e2e8f0;}
.stTabs [data-baseweb="tab"]{font-weight:600;}
</style>
""", unsafe_allow_html=True)


def kpi(label, value, sub="", cls=""):
    return f'<div class="kpi {cls}"><div class="l">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>'


def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def base_layout(fig, h=380):
    fig.update_layout(template="plotly_white", height=h, margin=dict(l=8, r=8, t=48, b=8),
                      font=dict(family="Inter, Segoe UI, sans-serif", size=12),
                      legend=dict(orientation="h", y=-0.18), paper_bgcolor="rgba(0,0,0,0)")
    return fig


@st.cache_data(show_spinner=False)
def cached_kurva(subjek, tahun, transisi):
    return kurva_pajak(subjek, tahun=tahun, transisi_cv=transisi)


# ------------------------------------------------------------------
# SIDEBAR — INPUT
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### 🧾 {NAMA_APP}")
    st.caption("Hitung estimasi pajak toko online & UMKM")

    st.markdown("**1. Profil usaha**")
    subjek = st.selectbox("Bentuk usaha", SUBJEK)
    tahun = st.selectbox("Tahun pajak", [2026, 2027, 2028, 2029])
    transisi = False
    surat = True
    if subjek.startswith("CV"):
        transisi = st.checkbox("Masih dalam masa transisi PPh final 0,5%",
                               help="Hanya untuk CV/Firma/PT yang sudah memakai fasilitas sebelum aturan baru dan belum berakhir masanya.")
    porsi_mp = st.slider("Omzet lewat marketplace (%)", 0, 100, 70, 5)
    if subjek == "Orang Pribadi":
        surat = st.checkbox("Sudah kirim surat pernyataan omzet ≤ Rp500 juta ke marketplace", value=True,
                            help="Tanpa surat ini, marketplace tetap memungut PPh 22 0,5%.")

    st.markdown("**2. Omzet**")
    mode = st.radio("Cara input", ["Otomatis", "Manual per bulan"], horizontal=True, label_visibility="collapsed")
    if mode == "Otomatis":
        avg = st.number_input("Omzet bulan pertama (Rp)", min_value=0, value=40_000_000, step=5_000_000)
        growth = st.slider("Pertumbuhan per bulan (%)", -10.0, 20.0, 3.0, 0.5)
        omzet = [round(avg * (1 + growth / 100) ** i) for i in range(12)]
    else:
        base = pd.DataFrame({"Bulan": BULAN, "Omzet (Rp)": [40_000_000] * 12})
        edit = st.data_editor(base, hide_index=True, disabled=["Bulan"], key="editor",
                              column_config={"Omzet (Rp)": st.column_config.NumberColumn(format="%d", min_value=0, step=1_000_000)})
        omzet = [float(x or 0) for x in edit["Omzet (Rp)"]]

    st.markdown("**3. Biaya**")
    hpp = st.slider("HPP (% omzet)", 0, 95, 55)
    fee = st.slider("Biaya marketplace (% dari omzet marketplace)", 0.0, 30.0, 9.0, 0.5,
                    help="Komisi, biaya layanan, gratis ongkir, voucher, dll.")
    ads = st.slider("Iklan (% omzet)", 0.0, 30.0, 5.0, 0.5)
    fix = st.number_input("Biaya tetap per bulan (Rp)", min_value=0, value=2_000_000, step=500_000)

    if FASTWORK_URL:
        st.divider()
        st.markdown(f"💼 Butuh analisis data penjualan lebih dalam? [Pesan di Fastwork]({FASTWORK_URL})")

# ------------------------------------------------------------------
# HITUNG
# ------------------------------------------------------------------
h = hitung_pajak(omzet, subjek, tahun=tahun, transisi_cv=transisi, porsi_marketplace=porsi_mp / 100,
                 surat_pernyataan=surat, hpp_pct=hpp / 100, biaya_mp_pct=fee / 100,
                 iklan_pct=ads / 100, biaya_tetap=fix)
df = h["tabel"]

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <h1>Kalkulator Pajak Penjual Online & UMKM</h1>
  <p>Ketahui kewajiban pajak Anda, kredit PPh 22 marketplace, dan laba bersih setelah pajak dalam hitungan detik.</p>
  <span class="badge">PP 20/2026</span><span class="badge">PMK 37/2025</span>
  <span class="badge">Diperbarui {ATURAN['diperbarui']}</span><span class="badge">Estimasi, bukan nasihat pajak</span>
</div>
""", unsafe_allow_html=True)

# KPI
s = h["selisih"]
if s > 0:
    k4 = kpi("Kurang bayar (setor sendiri)", rp(s), "Setelah kredit PPh 22", "bad")
elif s < 0:
    k4 = kpi("Lebih bayar (kredit PPh 22)", rp(-s), "Dapat dikompensasi/restitusi", "good")
else:
    k4 = kpi("Sisa kewajiban", rp(0), "Tidak ada kurang/lebih bayar")

c = st.columns(4)
c[0].markdown(kpi("Total omzet setahun", rp(h["total_omzet"]), h["skema"]), unsafe_allow_html=True)
c[1].markdown(kpi("Pajak penghasilan setahun", rp(h["pajak_tahun"]), f"{pct(h['tarif_efektif_omzet'])} dari omzet", "accent"), unsafe_allow_html=True)
c[2].markdown(kpi("PPh 22 dipungut marketplace", rp(h["pph22_total"]), "Dikreditkan ke pajak final"), unsafe_allow_html=True)
c[3].markdown(k4, unsafe_allow_html=True)
st.write("")
c = st.columns(4)
c[0].markdown(kpi("Laba sebelum pajak", rp(h["laba_sebelum_pajak"]), "Omzet − HPP − biaya"), unsafe_allow_html=True)
c[1].markdown(kpi("Laba bersih setelah pajak", rp(h["laba_bersih"]), f"Margin bersih {pct(h['margin_bersih'])}",
                  "good" if h["laba_bersih"] >= 0 else "bad"), unsafe_allow_html=True)
if subjek == "Orang Pribadi":
    c[2].markdown(kpi("Sisa omzet bebas PPh", rp(h["sisa_bebas"]), "Dari fasilitas Rp500 juta"), unsafe_allow_html=True)
else:
    c[2].markdown(kpi("Fasilitas Rp500 juta", "Tidak tersedia", "Khusus WP Orang Pribadi"), unsafe_allow_html=True)
rata = h["total_omzet"] / 12
c[3].markdown(kpi("Rata-rata omzet/bulan", rp(rata), f"Pajak rata-rata {rp(h['pajak_tahun']/12)}/bln"), unsafe_allow_html=True)

st.write("")
for k, m in h["catatan"]:
    st.markdown(f'<div class="note n-{k}">{m}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB
# ------------------------------------------------------------------
t1, t2, t3, t4, t5 = st.tabs(["📊 Ringkasan", "📅 Rincian Bulanan", "🔬 Simulasi", "⚖️ Bandingkan Bentuk Usaha", "📚 Dasar Hukum & FAQ"])

with t1:
    a, b = st.columns(2)
    with a:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df.Bulan, y=df.Omzet, name="Omzet", marker_color="#7dd3fc"), secondary_y=False)
        fig.add_trace(go.Scatter(x=df.Bulan, y=df.PPh_Final, name="PPh final", mode="lines+markers",
                                 line=dict(color=RED, width=3)), secondary_y=True)
        fig.add_trace(go.Scatter(x=df.Bulan, y=df.PPh22_Dipungut, name="PPh 22 dipungut", mode="lines+markers",
                                 line=dict(color=AMBER, width=3, dash="dot")), secondary_y=True)
        fig.update_yaxes(title_text="Omzet (Rp)", secondary_y=False)
        fig.update_yaxes(title_text="Pajak (Rp)", secondary_y=True, showgrid=False)
        fig.update_layout(title="Omzet dan pajak per bulan")
        show_chart(base_layout(fig))
    with b:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Bulan, y=df.Omzet_Kumulatif, name="Omzet kumulatif", fill="tozeroy",
                                 line=dict(color=TEAL, width=3), fillcolor="rgba(15,118,110,.15)"))
        fig.add_hline(y=ATURAN["pph_final_umkm"]["bebas_pajak_op"], line_dash="dash", line_color=GREEN,
                      annotation_text="Rp500 jt — bebas PPh (OP)", annotation_position="top left")
        fig.add_hline(y=ATURAN["pph_final_umkm"]["batas_omzet"], line_dash="dash", line_color=RED,
                      annotation_text="Rp4,8 M — batas PPh final UMKM", annotation_position="top left")
        fig.update_layout(title="Progres omzet kumulatif terhadap batas")
        show_chart(base_layout(fig))

    a, b = st.columns(2)
    with a:
        t = df.sum(numeric_only=True)
        bagian = {"HPP": t.HPP, "Biaya marketplace": t.Biaya_Marketplace, "Iklan": t.Iklan,
                  "Biaya tetap": t.Biaya_Tetap, "Pajak": h["pajak_tahun"], "Laba bersih": max(0, h["laba_bersih"])}
        fig = go.Figure(go.Pie(labels=list(bagian), values=list(bagian.values()), hole=.58, sort=False,
                               marker=dict(colors=["#94a3b8", "#fb923c", "#a78bfa", "#cbd5e1", RED, GREEN]),
                               textinfo="percent"))
        fig.update_layout(title="Ke mana perginya omzet Anda?")
        show_chart(base_layout(fig))
    with b:
        langkah = [("Omzet", h["total_omzet"]), ("HPP", -t.HPP), ("Biaya marketplace", -t.Biaya_Marketplace),
                   ("Iklan", -t.Iklan), ("Biaya tetap", -t.Biaya_Tetap), ("Pajak", -h["pajak_tahun"])]
        fig = go.Figure(go.Waterfall(
            x=[x for x, _ in langkah] + ["Laba bersih"], y=[y for _, y in langkah] + [0],
            measure=["absolute"] + ["relative"] * 5 + ["total"],
            connector=dict(line=dict(color="#cbd5e1")),
            increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=RED)),
            totals=dict(marker=dict(color=BLUE))))
        fig.update_layout(title="Dari omzet ke laba bersih", showlegend=False)
        show_chart(base_layout(fig))

with t2:
    st.markdown('<div class="sect">Rincian per bulan</div>', unsafe_allow_html=True)
    tampil = df.copy().rename(columns=lambda c: c.replace("_", " "))
    kolom_rp = [c for c in tampil.columns if c != "Bulan"]
    show_df(tampil, column_config={c: st.column_config.NumberColumn(c, format="Rp %d") for c in kolom_rp})

    buf = io.BytesIO()
    ringkas = pd.DataFrame({
        "Keterangan": ["Bentuk usaha", "Tahun pajak", "Skema pajak", "Total omzet", "Pajak penghasilan setahun",
                       "PPh 22 dipungut marketplace", "Kurang/(lebih) bayar", "Laba sebelum pajak", "Laba bersih"],
        "Nilai": [subjek, tahun, h["skema"], h["total_omzet"], h["pajak_tahun"], h["pph22_total"],
                  h["selisih"], h["laba_sebelum_pajak"], h["laba_bersih"]]})
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        ringkas.to_excel(xw, sheet_name="Ringkasan", index=False)
        df.to_excel(xw, sheet_name="Rincian Bulanan", index=False)
    d1, d2, _ = st.columns([1, 1, 3])
    d1.download_button("⬇️ Unduh Excel", buf.getvalue(), file_name="hasil_pajak_penjual_online.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    d2.download_button("⬇️ Unduh CSV", df.to_csv(index=False).encode("utf-8"), file_name="rincian_bulanan.csv", mime="text/csv")

with t3:
    st.markdown('<div class="sect">Bagaimana pajak berubah jika omzet berubah?</div>', unsafe_allow_html=True)
    st.caption("Omzet diasumsikan merata setiap bulan. Titik merah menandai posisi Anda sekarang.")
    a, b = st.columns(2)
    with a:
        fig = go.Figure()
        for nama, warna in [("Orang Pribadi", TEAL), ("PT Perorangan", BLUE)]:
            x2, y2 = cached_kurva(nama, tahun, False)
            fig.add_trace(go.Scatter(x=x2, y=y2, name=nama, line=dict(color=warna, width=3)))
        if h["skema"].startswith("PPh Final"):
            fig.add_trace(go.Scatter(x=[h["total_omzet"]], y=[h["pajak_tahun"]], mode="markers", name="Posisi Anda",
                                     marker=dict(size=14, color=RED, symbol="star")))
        fig.update_layout(title="Pajak tahunan vs omzet tahunan", xaxis_title="Omzet setahun (Rp)", yaxis_title="Pajak (Rp)")
        show_chart(base_layout(fig))
    with b:
        fig = go.Figure()
        for nama, warna in [("Orang Pribadi", TEAL), ("PT Perorangan", BLUE)]:
            x2, y2 = cached_kurva(nama, tahun, False)
            ef = [(y / x * 100) if x else 0 for x, y in zip(x2, y2)]
            fig.add_trace(go.Scatter(x=x2, y=ef, name=nama, line=dict(color=warna, width=3)))
        fig.update_layout(title="Tarif efektif (% dari omzet)", xaxis_title="Omzet setahun (Rp)", yaxis_title="%")
        show_chart(base_layout(fig))
    st.info("Orang Pribadi punya keuntungan: Rp500 juta pertama bebas PPh, sehingga tarif efektifnya mendekati 0,5% hanya pada omzet besar.")

with t4:
    st.markdown('<div class="sect">Pajak dengan omzet & biaya yang sama, beda bentuk usaha</div>', unsafe_allow_html=True)
    rows = []
    for sb in SUBJEK:
        r = hitung_pajak(omzet, sb, tahun=tahun, transisi_cv=False, porsi_marketplace=porsi_mp / 100,
                         surat_pernyataan=surat, hpp_pct=hpp / 100, biaya_mp_pct=fee / 100,
                         iklan_pct=ads / 100, biaya_tetap=fix)
        rows.append({"Bentuk usaha": sb, "Skema": r["skema"], "Pajak setahun": r["pajak_tahun"],
                     "Tarif efektif (% omzet)": r["tarif_efektif_omzet"] * 100, "Laba bersih": r["laba_bersih"]})
    cmp = pd.DataFrame(rows)
    fig = go.Figure(go.Bar(x=cmp["Bentuk usaha"], y=cmp["Pajak setahun"],
                           marker_color=[TEAL, BLUE, "#8b5cf6", AMBER],
                           text=[rp(v) for v in cmp["Pajak setahun"]], textposition="outside"))
    fig.update_layout(title="Pajak setahun per bentuk usaha", yaxis_title="Rp", showlegend=False)
    show_chart(base_layout(fig, 400))
    show_df(cmp, column_config={
        "Pajak setahun": st.column_config.NumberColumn(format="Rp %d"),
        "Laba bersih": st.column_config.NumberColumn(format="Rp %d"),
        "Tarif efektif (% omzet)": st.column_config.NumberColumn(format="%.2f%%")})
    st.caption("CV/Firma/PT umum dihitung dengan PPh Badan tarif umum (perkiraan kasar dari laba). Memilih bentuk usaha punya konsekuensi hukum lain; jangan putuskan hanya dari pajak.")

with t5:
    st.markdown('<div class="sect">Ringkasan aturan yang dipakai</div>', unsafe_allow_html=True)
    aturan_tbl = pd.DataFrame([
        ["PPh final UMKM", "0,5% dari omzet; maks. omzet Rp4,8 miliar/tahun", "PP 55/2022 jo. PP 20/2026"],
        ["Subjek PPh final 0,5%", "Orang Pribadi, PT Perorangan, Koperasi (CV/Firma/PT umum tidak lagi, kecuali masa transisi)", "PP 20/2026"],
        ["Bebas PPh Rp500 juta", "Omzet Rp500 juta pertama, khusus WP Orang Pribadi", "PP 55/2022 Pasal 60 ayat (2)"],
        ["PPh 22 marketplace", "0,5% dari omzet; OP s.d. Rp500 juta dikecualikan dengan surat pernyataan", "PMK 37/2025"],
        ["Batas PKP", "Omzet > Rp4,8 miliar wajib dikukuhkan PKP", "UU PPN"],
        ["PPh Badan (CV/PT umum)", "Tarif 22%, dengan fasilitas Pasal 31E untuk omzet ≤ Rp4,8 miliar", "UU PPh"]],
        columns=["Topik", "Ketentuan", "Dasar hukum"])
    show_df(aturan_tbl)
    st.markdown('<div class="sect">Pertanyaan umum</div>', unsafe_allow_html=True)
    with st.expander("Apakah omzet di bawah Rp500 juta tetap harus lapor?"):
        st.write("Ya. Wajib pajak tetap melaporkan omzet dalam SPT Tahunan meski tidak ada PPh final yang terutang.")
    with st.expander("PPh 22 yang dipotong marketplace itu pajak tambahan?"):
        st.write("Tidak. Pemungutan tersebut dapat dikreditkan terhadap PPh final yang terutang, sehingga kalkulator ini menguranginya dari total pajak setahun.")
    with st.expander("Pajak final dihitung dari omzet atau laba?"):
        st.write("Dari omzet (peredaran bruto), bukan laba. Jadi usaha yang rugi tetap membayar PPh final di atas batas bebas pajaknya.")
    with st.expander("Kapan pemungutan PPh 22 marketplace mulai berlaku?"):
        st.write(f"Pengaturan awal di alat ini adalah bulan ke-{ATURAN['pph22_marketplace']['bulan_mulai_2026']} tahun 2026. Sumber media menyebut tanggal berbeda, jadi cek pengumuman resmi DJP dan ubah di `pajak_engine.py` bila perlu.")

st.markdown(f"""
<div class="disc"><b>Penting:</b> Hasil adalah <b>estimasi</b> untuk edukasi dan perencanaan, bukan nasihat pajak resmi.
Kondisi tertentu (penghasilan lain, pengecualian objek pajak, koreksi fiskal, PPN, dan lainnya) tidak tercakup.
Aturan pajak sering berubah; verifikasi ke <a href="https://www.pajak.go.id" target="_blank">pajak.go.id</a> atau konsultan pajak sebelum melapor.
Aturan terakhir diperbarui di alat ini: {ATURAN['diperbarui']}.</div>
""", unsafe_allow_html=True)
