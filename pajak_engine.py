"""Mesin perhitungan pajak penjual online & UMKM. Aturan dipisah di dict ATURAN agar mudah diperbarui."""
# ============================================================
# CELL 2 — ATURAN PAJAK (dipisahkan dari kode supaya mudah diperbarui)
# Perbarui bagian ini saja jika aturan berubah.
# ============================================================
ATURAN = {
    "diperbarui": "15 November 2026",
    "pph_final_umkm": {
        "tarif": 0.005,                    # 0,5% dari omzet (peredaran bruto)
        "batas_omzet": 4_800_000_000,      # maks. Rp4,8 miliar per tahun pajak
        "bebas_pajak_op": 500_000_000,     # Rp500 juta pertama bebas PPh (khusus WP Orang Pribadi)
        "subjek_boleh": ["Orang Pribadi", "PT Perorangan", "Koperasi"],
        "dasar_hukum": "PP 55/2022 sebagaimana diubah PP 20/2026 (berlaku 22 April 2026)",
    },
    "pph22_marketplace": {
        "tarif": 0.005,                    # dipungut marketplace, dari omzet (di luar PPN/PPnBM)
        "batas_surat_pernyataan": 500_000_000,
        "bulan_mulai_2026": 8,             # Sumber media berbeda (Juli/Agustus 2026). Ubah sesuai info resmi DJP.
        "dasar_hukum": "PMK 37/2025",
    },
    "pph_badan": {
        "tarif": 0.22,
        "diskon_31e": 0.5,                 # Pasal 31E: pengurangan tarif 50% untuk omzet s.d. Rp50 miliar
        "batas_omzet_31e_penuh": 4_800_000_000,
        "dasar_hukum": "UU PPh Pasal 17 & 31E",
    },
    "pkp_batas_omzet": 4_800_000_000,      # Pengusaha wajib dikukuhkan PKP jika omzet melebihi ini
}

SUBJEK = [
    "Orang Pribadi",
    "PT Perorangan",
    "Koperasi",
    "CV / Firma / PT (umum)",
]
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


# ============================================================
# CELL 3 — MESIN PERHITUNGAN
# ============================================================
import pandas as pd

def rp(x):
    """Format angka ke Rupiah: 1234567 -> Rp 1.234.567"""
    s = f"{abs(x):,.0f}".replace(",", ".")
    return ("-Rp " if x < 0 else "Rp ") + s

def pct(x):
    return f"{x*100:.2f}%".replace(".", ",")

def hitung_pajak(omzet, subjek, tahun=2026, transisi_cv=False,
                 porsi_marketplace=0.0, surat_pernyataan=True,
                 hpp_pct=0.0, biaya_mp_pct=0.0, iklan_pct=0.0, biaya_tetap=0.0,
                 aturan=ATURAN):
    """
    omzet            : list 12 angka omzet bulanan (Rp)
    subjek           : salah satu dari SUBJEK
    transisi_cv      : True jika CV/Firma/PT masih dalam masa transisi fasilitas 0,5%
    porsi_marketplace: 0-1, bagian omzet yang lewat marketplace (dipungut PPh 22)
    surat_pernyataan : True jika sudah kirim surat pernyataan omzet <= Rp500 juta (khusus OP)
    """
    f = aturan["pph_final_umkm"]
    m22 = aturan["pph22_marketplace"]
    omzet = [float(x or 0) for x in omzet]

    final_boleh = (subjek in f["subjek_boleh"]) or (subjek.startswith("CV") and transisi_cv)
    is_op = subjek == "Orang Pribadi"

    rows, cum = [], 0.0
    for i, o in enumerate(omzet):
        awal, akhir = cum, cum + o
        cum = akhir

        # --- PPh final 0,5% ---
        melebihi_batas = awal > f["batas_omzet"]          # bulan setelah omzet kumulatif > Rp4,8 M
        if final_boleh and not melebihi_batas:
            if is_op:
                dpp = max(0, akhir - f["bebas_pajak_op"]) - max(0, awal - f["bebas_pajak_op"])
            else:
                dpp = o
            final = dpp * f["tarif"]
        else:
            dpp, final = 0.0, 0.0

        # --- PPh 22 dipungut marketplace ---
        mulai_ok = (tahun != 2026) or ((i + 1) >= m22["bulan_mulai_2026"])
        omzet_mp = o * porsi_marketplace
        if not mulai_ok or omzet_mp == 0:
            pph22 = 0.0
        elif is_op and surat_pernyataan:
            # dikecualikan sampai omzet kumulatif melewati Rp500 juta; dipungut mulai bulan berikutnya
            pph22 = omzet_mp * m22["tarif"] if awal > m22["batas_surat_pernyataan"] else 0.0
        else:
            pph22 = omzet_mp * m22["tarif"]

        # --- Laba operasional ---
        hpp = o * hpp_pct
        mp = omzet_mp * biaya_mp_pct
        iklan = o * iklan_pct
        laba = o - hpp - mp - iklan - (biaya_tetap if o > 0 else 0)

        rows.append(dict(Bulan=BULAN[i], Omzet=o, Omzet_Kumulatif=akhir, DPP_Final=dpp,
                         PPh_Final=final, PPh22_Dipungut=pph22, HPP=hpp, Biaya_Marketplace=mp,
                         Iklan=iklan, Biaya_Tetap=(biaya_tetap if o > 0 else 0), Laba_Sebelum_Pajak=laba))
    df = pd.DataFrame(rows)

    total_omzet = df.Omzet.sum()
    laba_total = df.Laba_Sebelum_Pajak.sum()
    catatan = []

    # --- Pajak tahunan menurut jenis subjek ---
    if final_boleh:
        skema = "PPh Final UMKM 0,5%"
        pajak_tahun = df.PPh_Final.sum()
        if subjek.startswith("CV"):
            catatan.append(("info", "Fasilitas 0,5% untuk CV/Firma/PT umum hanya berlaku selama masa transisi bagi yang sudah memakainya sebelum aturan baru. Pastikan Anda memenuhi syarat transisi."))
    elif subjek.startswith("CV"):
        b = aturan["pph_badan"]
        tarif_eff = b["tarif"] * (1 - b["diskon_31e"]) if total_omzet <= b["batas_omzet_31e_penuh"] else b["tarif"]
        skema = "PPh Badan tarif umum (perkiraan kasar)"
        pajak_tahun = max(0, laba_total) * tarif_eff
        catatan.append(("warn", f"CV/Firma/PT umum tidak lagi memakai PPh final 0,5%. Angka di atas hanya PERKIRAAN KASAR: tarif {pct(tarif_eff)} x laba sebelum pajak. Laba fiskal sebenarnya memerlukan koreksi fiskal oleh akuntan/konsultan pajak."))
    else:
        skema, pajak_tahun = "-", 0.0

    if final_boleh and total_omzet > f["batas_omzet"]:
        catatan.append(("danger", f"Omzet melebihi {rp(f['batas_omzet'])}. Atas omzet bulan-bulan setelah batas terlewati, wajib memakai tarif umum PPh (tidak dihitung otomatis di sini). Konsultasikan dengan konsultan pajak."))
    if total_omzet > aturan["pkp_batas_omzet"]:
        catatan.append(("danger", f"Omzet melebihi {rp(aturan['pkp_batas_omzet'])}: Anda wajib dikukuhkan sebagai Pengusaha Kena Pajak (PKP) dan memungut PPN. Perhitungan PPN belum termasuk di alat ini."))
    if is_op and total_omzet <= f["bebas_pajak_op"]:
        catatan.append(("ok", f"Omzet setahun masih di bawah {rp(f['bebas_pajak_op'])}: tidak ada PPh final terutang. Tetap laporkan omzet di SPT Tahunan."))
    if is_op and porsi_marketplace > 0 and not surat_pernyataan and total_omzet <= f["bebas_pajak_op"]:
        catatan.append(("warn", "Tanpa surat pernyataan omzet, marketplace tetap memungut PPh 22 0,5% meski omzet Anda di bawah Rp500 juta. Kirim surat pernyataan lewat akun marketplace."))
    if not is_op and porsi_marketplace > 0:
        catatan.append(("info", "Pengecualian pemungutan PPh 22 (omzet s.d. Rp500 juta) hanya untuk WP Orang Pribadi; badan tetap dipungut."))
    if laba_total < 0 and pajak_tahun > 0:
        catatan.append(("warn", "Usaha Anda rugi, tetapi PPh final tetap dihitung dari omzet (bukan dari laba)."))

    kredit = df.PPh22_Dipungut.sum()
    selisih = pajak_tahun - kredit      # >0 kurang bayar, <0 lebih bayar
    hasil = dict(
        skema=skema, total_omzet=total_omzet, laba_sebelum_pajak=laba_total,
        pajak_tahun=pajak_tahun, pph22_total=kredit, selisih=selisih,
        laba_bersih=laba_total - pajak_tahun,
        tarif_efektif_omzet=(pajak_tahun / total_omzet if total_omzet else 0),
        margin_bersih=((laba_total - pajak_tahun) / total_omzet if total_omzet else 0),
        sisa_bebas=max(0, f["bebas_pajak_op"] - total_omzet) if is_op else 0,
        catatan=catatan, tabel=df,
    )
    return hasil

def kurva_pajak(subjek, batas_atas=5_200_000_000, titik=60, **kw):
    """Pajak tahunan untuk berbagai level omzet (omzet merata tiap bulan) — untuk grafik simulasi."""
    import numpy as np
    xs = np.linspace(0, batas_atas, titik)
    ys = [hitung_pajak([x / 12] * 12, subjek, **kw)["pajak_tahun"] for x in xs]
    return xs, ys
