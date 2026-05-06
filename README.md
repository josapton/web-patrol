# 🛡️ WEB-PATROL: Automated Web Security Command Center

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![NiceGUI](https://img.shields.io/badge/NiceGUI-UI-ff9800)
![License](https://img.shields.io/badge/license-MIT-green)

**WEB-PATROL** adalah sistem orkestrasi pemantauan keamanan siber berbasis *Asynchronous Scanning*. Sistem ini dirancang untuk melakukan audit kerentanan (vulnerability assessment) secara otomatis dan *real-time* pada aset digital web (seperti web pemerintahan, kampus, atau institusi publik) dan memberikan laporan remediasi yang dapat ditindaklanjuti.

---

## ✨ Fitur Utama

Sistem ini bertindak sebagai *Command Center* yang beroperasi 24/7 dengan fitur-fitur kelas *Enterprise*:

- **📡 8 Modul Intelijen Paralel:** 
  1. **Security Headers:** Audit konfigurasi HTTP Header (CSP, HSTS, dll).
  2. **Defacement Detection:** Memantau integritas konten web via *Hashing* (SHA-256).
  3. **SSL/TLS Verifier:** Memeriksa sisa hari masa berlaku sertifikat SSL.
  4. **Port Scanner:** Mendeteksi port kritis (21, 22, 3306) yang terekspos ke publik.
  5. **Directory Fuzzer:** Mencari file sensitif yang bocor (`.env`, `wp-admin`, `backup.zip`).
  6. **API Key Detector:** Regex engine untuk mendeteksi kebocoran *Secret Keys*.
  7. **Broken Link Hijacking:** Melacak tautan mati pada halaman target.
  8. **WHOIS Monitor:** Memantau masa kedaluwarsa domain target.
- **🛡️ WAF & Firewall Detection:** Mendeteksi keberadaan proteksi Cloudflare atau *Internal Firewall*.
- **📊 Real-Time UI:** Animasi *log terminal* interaktif dan grafik metrik berbasis NiceGUI & Apache ECharts.
- **🚨 Telegram Early Warning System:** Mengirimkan peringatan instan beserta bukti *screenshot* (menggunakan Playwright) jika terdeteksi ancaman kritis (Skor < 50).
- **📄 Auto-Generated PDF Reports:** Menghasilkan dokumen laporan audit lengkap dengan panduan **Saran Perbaikan (Remediasi)**.
- **⏱️ Background Scheduler:** Melakukan siklus patroli otomatis setiap 30 menit.

---

## 🛠️ Teknologi yang Digunakan

- **Backend / Orchestrator:** Python, FastAPI, Asyncio
- **Frontend / UI:** NiceGUI (Vue3 & TailwindCSS wrapper)
- **Database:** SQLite (dengan SQLModel ORM)
- **Engine Security:** Httpx, BeautifulSoup4, Playwright, Python-Whois
- **Reporting & Task:** FPDF2, APScheduler, Python-dotenv

---

## 🚀 Panduan Instalasi

### 1. Prasyarat
Pastikan Anda telah menginstal **Python 3.8+** dan **Git** di sistem (Windows/Linux/macOS).

### 2. Clone Repositori
```bash
git clone https://github.com/josapton/web-patrol.git
cd web-patrol
```

### 3. Buat Virtual Environment & Instal Dependensi
```bash
# Membuat virtual environment
python -m venv venv

# Aktivasi venv (Linux/macOS)
source venv/bin/activate
# Aktivasi venv (Windows)
venv\Scripts\activate

# Instalasi modul Python
pip install -r requirements.txt

# Instalasi browser Playwright (untuk fitur Screenshot)
playwright install chromium
# Jika sudah mempunyai browser berbasis chromium bisa langsung mengubah channel di 'scanner.py'
browser = await p.chromium.launch(headless=True, channel="msedge")
```

### 4. Konfigurasi Kredensial (.env)
Buat file bernama `.env` di folder utama (sejajar dengan `main.py`) dan isi dengan kredensial Bot Telegram Anda:
```env
TELEGRAM_TOKEN=123456789:ABCDefghIJKLmnopQRSTuvwxyz
TELEGRAM_CHAT_ID=123456789
```

---

## 💻 Cara Penggunaan

Jalankan server aplikasi melalui terminal:
```bash
python3 main.py
```
Akses *dashboard* pemantauan melalui *browser* di alamat:
**`http://localhost:8080`**

- Tambahkan URL target lengkap dengan protokol (contoh: `[https://josapton.github.io](https://josapton.github.io)`).
- Klik **Jalankan Audit Penuh** untuk memulai simulasi pemindaian, atau biarkan sistem bekerja otomatis di latar belakang sesuai jadwal.

---

## ⚠️ Peringatan Legal (Disclaimer)

Sistem ini dikembangkan **murni untuk tujuan edukasi, riset, dan audit internal yang sah**. 
Pengguna **WAJIB** memiliki izin tertulis (*authorization*) dari pemilik aset / administrator jaringan sebelum memasukkan target ke dalam sistem ini. Pengembang (Author) tidak bertanggung jawab atas penyalahgunaan *tool* ini untuk kegiatan *scanning* ilegal atau serangan siber ke pihak yang tidak memberikan wewenang.

---
*Developed with ☕ and 🛡️ for a safer digital public infrastructure.*