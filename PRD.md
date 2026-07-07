# PRD: ThunderChat
### Chatbot Analitik Berbasis Gemini API — Dashboard Gebang Thunder

**Versi:** 1.0
**Tanggal:** 8 Juli 2026
**Status:** Ready for development

---

## 1. Latar Belakang & Ruang Lingkup

Gebang Thunder adalah dashboard Power BI dengan tiga section: **Summary** (ringkasan insight), **Analytics** (visualisasi interaktif), dan **ThunderChat** (chatbot dengan grounding pada dataset). Berbeda dari dua section lainnya, ThunderChat tidak membuka halaman Power BI — ia mengarahkan pengguna ke sebuah **web aplikasi terpisah** melalui browser.

**Ruang lingkup dokumen ini hanya mencakup web ThunderChat**, yaitu chatbot yang menjawab pertanyaan natural language pengguna berdasarkan satu dataset tetap, menggunakan Gemini API.

## 2. Tujuan & Success Criteria

**Tujuan:**
- Memberi pengguna dashboard cara cepat mendapatkan insight dari data tanpa menavigasi visual Power BI secara manual.
- Jawaban akurat dan dibatasi pada grounding data — bukan pengetahuan umum model.
- Sederhana untuk dikembangkan, dipelihara, dan berjalan gratis di atas free tier Gemini API.

**Success Criteria (Definition of Done):**
- Web berhasil di-deploy ke Streamlit Community Cloud dan dapat diakses lewat link statis publik.
- Chatbot menjawab pertanyaan seputar dataset dengan jawaban naratif yang akurat.
- Pertanyaan di luar konteks dataset direspons dengan fallback message yang sesuai (bukan halusinasi).
- Saat salah satu API key gagal/limit habis, sistem tetap berjalan (tidak crash) dan menampilkan fallback message yang jelas ke user.
- Tampilan sesuai mockup desain, color palette, dan font yang ditentukan.

## 3. Target Pengguna & Skala

| Aspek | Ketentuan |
|---|---|
| Akses | Publicly accessible, tanpa login/autentikasi |
| Concurrent users | ~8–10 user saat traffic ramai |
| Riwayat percakapan | Tidak perlu disimpan; tiap pertanyaan independen (stateless per-question) |

## 4. User Flow

1. User klik ThunderChat di dashboard Power BI → browser membuka web ThunderChat via **link statis**.
2. Landing page kosong tampil: hero text, branding, dan search bar (lihat Section 10 — Desain UI/UX).
3. User mengetik pertanyaan → submit.
4. Sistem memilih 1 API key (round-robin) → menyusun prompt grounding → memanggil Gemini.
5. Jawaban naratif ditampilkan sebagai chat bubble.
6. User dapat mengajukan pertanyaan baru — **tidak ada memori dari pertanyaan sebelumnya**.

## 5. Functional Requirements

**FR1 — Landing / Empty State**
Menampilkan hero text branding + search bar kosong (tanpa histori), sesuai mockup desain.

**FR2 — Contoh Pertanyaan (Suggested Prompts)**
Tampilkan beberapa contoh pertanyaan yang relevan dengan dataset di landing page untuk membantu user yang belum tahu harus bertanya apa. Desain/jumlah bebas ditentukan developer selama konsisten dengan style guide.

**FR3 — Input & Submit**
Text input single-line dengan tombol/icon submit; submit juga bisa lewat tombol Enter.

**FR4 — Proses Jawaban**
a. Pilih 1 API key dari pool secara round-robin.
b. Susun prompt: system instruction (pembatas domain) + representasi/agregasi data dari dataset + pertanyaan user.
c. Panggil Gemini API (lihat Section 7).
d. Render jawaban sebagai **teks naratif saja** (tanpa chart/tabel — demi efisiensi token).

**FR5 — Fallback: Out-of-domain**
Jika pertanyaan di luar cakupan dataset, tampilkan fallback message spesifik, contoh:
> "Maaf, ThunderChat hanya dapat menjawab pertanyaan seputar data yang tersedia di dashboard ini. Coba ajukan pertanyaan lain terkait data tersebut."

**FR6 — Fallback: API Error/Limit**
Jika API call gagal (quota habis, rate limit, error jaringan), tampilkan fallback message ramah — **bukan** raw error/stack trace, contoh:
> "Maaf, sistem sedang sibuk atau mencapai batas penggunaan. Silakan coba lagi dalam beberapa saat."

**FR7 — Loading State**
Animasi Lottie minimalis muncul saat aplikasi **pertama kali dibuka** (initial load). Saat menunggu jawaban Gemini, gunakan indikator loading standar (mis. `st.spinner`) sebagai penanda "sedang memproses".

## 6. Data & Grounding Requirements

| Aspek | Ketentuan |
|---|---|
| Format | CSV |
| Volume | ±3.000–5.000 baris, 5–8 kolom |
| Relasi dengan dashboard | Dataset **identik** dengan yang dipakai section Summary & Analytics |
| Update | Tidak ada — data bersifat ad hoc, statis, satu dataset tetap |
| Status saat ini | **Dataset belum diserahkan** — lihat Section 13 (dependensi terbuka) |

**Strategi Grounding (direkomendasikan):**

Karena volume data kecil (±5.000 baris), keseluruhan data dapat masuk nyaman ke dalam context window 1M token Gemini 3.5 Flash tanpa perlu vector database/RAG. Pendekatan yang direkomendasikan untuk MVP:

1. Load dataset sekali ke memory via **pandas** saat aplikasi start.
2. Gunakan pandas/numpy untuk pre-agregasi metrik umum (total per bulan, per kategori, dsb.) sehingga **angka dihitung secara deterministic**, bukan ditebak oleh LLM dari teks mentah — penting untuk akurasi jawaban numerik.
3. Sertakan representasi data yang sudah bersih (plus hasil agregasi relevan) sebagai context/system instruction pada tiap request ke Gemini.
4. scikit-learn dipakai sesuai brief awal untuk kebutuhan EDA/preprocessing tambahan (mis. deteksi outlier atau normalisasi) bila diperlukan untuk meningkatkan kualitas grounding.

> **[ASUMSI — perlu dikonfirmasi]** Skema kolom final (nama, tipe data) belum tersedia. Ingestion layer harus **schema-agnostic** (auto-detect kolom via pandas), tidak hardcode nama kolom spesifik, agar tidak perlu refactor besar saat dataset asli diberikan.

## 7. Integrasi Gemini API & Strategi Multi-Key

> ⚠️ **Catatan penting untuk developer/agentic AI tool:** Lanskap model Gemini berubah cepat. Model lama seperti `gemini-2.0-flash`, `gemini-1.5-*`, atau `gemini-pro`, serta SDK Python lama `google-generativeai`, **sudah deprecated dan/atau dimatikan** per pertengahan 2026. Jangan gunakan default dari training data yang mungkin sudah usang — ikuti spesifikasi di bawah ini secara verbatim.

| Aspek | Ketentuan |
|---|---|
| Model | `gemini-3.5-flash` (GA, dirilis Mei 2026 — model Flash terbaru, gratis dengan rate limit) |
| SDK Python | Package resmi `google-genai` (**bukan** `google-generativeai` yang deprecated). Import: `from google import genai` |
| Jumlah API key | 3–5 API key, masing-masing dari akun Google gratis berbeda |
| Strategi rotasi | **Round-robin per eksekusi**: pertanyaan ke-1 pakai Key A, ke-2 pakai Key B, dst., lalu wrap-around. Index rotasi disimpan di `st.session_state` |
| Saat limit/error | **Tidak ada retry otomatis ke key lain dalam request yang sama** — langsung tampilkan fallback message (FR6). Simple by design, sesuai preferensi kesederhanaan |
| Budget/cost tracking | Tidak diperlukan — cukup fallback message saat limit/error tercapai |

*Catatan: karena tiap API key berasal dari akun Google/project berbeda, kuota tiap key terpisah (kuota bersifat per-project, bukan per-key dalam satu project) — pendekatan multi-akun ini valid untuk memperbesar kapasitas gratis.*

## 8. Non-Functional Requirements

- **Performance:** target jawaban tampil dalam hitungan detik, mengikuti kecepatan native Gemini 3.5 Flash — tidak ada SLA formal.
- **Scalability:** cukup untuk ±8–10 concurrent users pada resource default Streamlit Community Cloud (1 shared CPU, RAM terbatas); tidak perlu horizontal scaling.
- **Reliability:** sistem tidak boleh crash saat API gagal — selalu graceful fallback (lihat FR5/FR6).
- **Maintainability:** struktur kode modular, efisien, scalable (lihat Section 12).
- **Observability:** logging dasar (request, error, key yang dipakai) disimpan **secara internal saja** — log file lokal dalam repo/app storage atau log console bawaan Streamlit Cloud. **Tidak boleh** tampil ke publik/user.
- **Compatibility:** versi package di `requirements.txt`/`environment.yml` **tidak dikunci ketat**, demi kompatibilitas saat deploy ulang di Streamlit Community Cloud.

## 9. Keamanan

- API key **wajib** disimpan via Streamlit Secrets (`.streamlit/secrets.toml` untuk lokal; Secrets dashboard bawaan untuk Streamlit Community Cloud) — **tidak pernah** hardcoded di source code.
- `.gitignore` wajib meng-exclude `secrets.toml`, `.env`, `__pycache__`, dan file sensitif lain.
- Tidak ada autentikasi/otorisasi user (akses publik, sesuai keputusan produk).
- Input user sebaiknya dibatasi panjangnya secara wajar untuk mengurangi risiko penyalahgunaan (rekomendasi ringan, opsional untuk MVP).

## 10. Desain UI/UX

Mengacu pada mockup desain yang sudah dibuat:

**Landing / Empty State:**
- Hero text branding (mis. tagline besar + nama "Gebang Thunder" beserta tag identifier).
- Search bar minimalis, rounded, dengan placeholder *"Apa yang ingin kamu tahu?"*.
- Contoh pertanyaan (suggested prompts) ditampilkan di sekitar search bar (lihat FR2).

**Tampilan Percakapan:**
- Pertanyaan user tampil sebagai chat bubble (putih, rata kanan).
- Jawaban chatbot tampil sebagai teks naratif tanpa bubble/background khusus.
- Search bar tetap tersedia di bagian bawah untuk pertanyaan berikutnya.

**Style Guide (dari brief awal):**

| Elemen | Nilai |
|---|---|
| Font | Inter |
| Background | `#F6F8FA` |
| Input Prompt | `#FFFFFF` |
| Primary Text | `#0D1117` |
| Secondary Text & Border Input | `#737373` |
| Primary Accent (judul, logo, elemen utama) | `#2563EB` |
| Shadow | Tipis, minimalis |
| Styling | Custom CSS dengan referensi shadcn/ui, dibantu library `streamlit-shadcn-ui` |

## 11. Tech Stack

| Kebutuhan | Pilihan |
|---|---|
| Framework | Streamlit (target deploy: Streamlit Community Cloud) |
| Styling | Custom CSS + `streamlit-shadcn-ui` |
| Data processing | pandas, numpy, scikit-learn |
| Loading animation | `streamlit-lottie` |
| LLM | Gemini API (`gemini-3.5-flash`) via package `google-genai` |
| Font | Inter |

## 12. Arsitektur & Struktur Repository

Struktur modular, efisien, scalable, dan mudah dipelihara:

```
thunderchat/
├── app.py                    # Entry point Streamlit
├── src/
│   ├── config.py             # Load secrets & daftar API key
│   ├── gemini_client.py      # Wrapper Gemini API: rotasi key + error handling
│   ├── data_loader.py        # Load & preprocessing CSV (pandas/numpy/scikit-learn)
│   ├── grounding.py          # Bangun prompt/context grounding
│   ├── ui/
│   │   ├── styles.py         # Custom CSS (shadcn/ui, color palette, font Inter)
│   │   └── components.py     # Komponen UI (chat bubble, input, suggested prompts)
│   └── utils/
│       └── logger.py         # Logging internal (tidak tampil ke publik)
├── data/
│   └── dataset.csv           # Dataset grounding (ad hoc, statis)
├── assets/
│   ├── loading.json          # File animasi Lottie
│   ├── icons/                # Icon logo (Gebang Thunder) & elemen UI (mis. ikon submit/"enter")
│   └── fonts/                # File font Inter (mis. Inter-Regular.ttf, Inter-Bold.ttf, dst.)
├── .streamlit/
│   └── secrets.toml          # API keys — JANGAN di-commit (masuk .gitignore)
├── .gitignore
├── requirements.txt           # Untuk deployment
├── environment.yml            # Versi package tidak dikunci ketat
└── README.md
```

## 13. Asumsi & Dependensi Terbuka

- **Dataset asli (.csv) belum diserahkan** — wajib disediakan sebelum atau di awal development. Skema kolom final akan menentukan detail implementasi grounding.
- Target response time tidak didefinisikan secara ketat — mengikuti performa native Gemini 3.5 Flash.
- Copy/teks hero landing page (mis. tagline) mengikuti mockup yang ada, dapat disesuaikan lebih lanjut oleh tim desain.
- Rate limit aktual free tier `gemini-3.5-flash` sebaiknya dicek langsung di Google AI Studio saat implementasi, karena kebijakan free tier dapat berubah sewaktu-waktu.

## 14. Out of Scope

- Percakapan multi-turn dengan memori/follow-up context.
- Visualisasi chart/tabel di dalam jawaban chatbot.
- Dashboard monitoring publik untuk log/usage.
- Autentikasi/login user.
- Update data otomatis/real-time sync.
- Budget/cost tracking otomatis untuk pemakaian API.
- Retry otomatis lintas API key dalam satu request yang sama.
