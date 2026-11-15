# Kalkulator Pajak Penjual Online & UMKM (Streamlit)

## Jalankan lokal
    pip install -r requirements.txt
    streamlit run app.py

## Deploy gratis (Streamlit Community Cloud)
1. Upload semua file ini ke repositori GitHub.
2. Buka share.streamlit.io, login dengan GitHub, pilih repositori dan file `app.py`, lalu Deploy.

## Memperbarui aturan pajak
Ubah dict `ATURAN` di `pajak_engine.py` (tarif, batas, tanggal mulai pemungutan PPh 22). Cek ke pajak.go.id secara berkala.
Isi `FASTWORK_URL` di `app.py` untuk menampilkan tautan ke listing Fastwork Anda.

Hasil adalah estimasi, bukan nasihat pajak resmi.
