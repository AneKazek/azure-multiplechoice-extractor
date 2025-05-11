```markdown
# 🚀 Azure Multiple Choice Extractor

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Programz** adalah kumpulan skrip Python canggih untuk:
- 📄 **Menganalisis dokumen** dengan Azure AI Document Intelligence  
- ✍️ **Mendeteksi jawaban** dari lembar jawaban ujian secara otomatis  

---

## 📂 Struktur Proyek

```

Programz/
├── LICENSE
├── README.md
├── test.py
└── get\_jawaban\_himpunan.py

````

- **test.py**  
  Menunjukkan contoh alur kerja: ekstraksi teks & layout dari dokumen, lalu deteksi jawaban ujian.  
- **get_jawaban_himpunan.py**  
  Implementasi fungsi `get_jawaban_himpunan()` untuk memperoleh jawaban siswa dengan pendekatan himpunan.

---

## 🔧 Prasyarat

- Python 3.8 atau lebih baru  
- Akun & API Key Azure Cognitive Services  
- Azure AI Document Intelligence SDK

---

## 🚀 Instalasi

1. **Clone** repositori:  
   ```bash
   git clone https://github.com/username/Programz.git
   cd Programz
````

2. **Buat virtual environment** (opsional tapi direkomendasikan):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Konfigurasi

1. Buat file `.env` di root proyek:

   ```text
   AZURE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
   AZURE_API_KEY=<your-api-key>
   ```
2. Pastikan variabel environment sudah ter-load (bila menggunakan virtualenv, jalankan `source .env`).

---

## 🎯 Cara Menggunakan

1. **Analisis Dokumen**

   ```bash
   python test.py --input path/to/document.pdf
   ```

   * Output: struktur layout & teks terdeteksi di console.

2. **Deteksi Jawaban Ujian**

   ```bash
   python get_jawaban_himpunan.py --input path/to/answer-sheet.pdf
   ```

   * Output: daftar jawaban siswa berdasarkan nomor soal.

---

## 🛠️ Contoh Kode

```python
from azure.ai.documentintelligence import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from get_jawaban_himpunan import get_jawaban_himpunan

# Inisialisasi klien
client = DocumentAnalysisClient(
    endpoint="YOUR_ENDPOINT",
    credential=AzureKeyCredential("YOUR_API_KEY")
)

# Analisis dokumen
poller = client.begin_analyze_document("prebuilt-document", "sample.pdf")
result = poller.result()

# Cetak hasil ekstraksi teks
for page in result.pages:
    print(page.lines)

# Deteksi jawaban
jawaban = get_jawaban_himpunan("answer-sheet.pdf")
print("Jawaban siswa:", jawaban)
```

---

## 🤝 Contributing

1. Fork repositori ini.
2. Buat branch baru: `git checkout -b fitur-baru`
3. Commit perubahan Anda: `git commit -m "Menambahkan fitur baru"`
4. Push ke branch Anda: `git push origin fitur-baru`
5. Buka Pull Request.

---

## 📄 License

Proyek ini dilisensikan di bawah MIT License.
Lihat file [LICENSE](LICENSE) untuk detail.

```

Dengan struktur dan penjelasan di atas, README Anda akan lebih menarik, mudah dipahami, dan siap dipakai oleh kontributor baru. Semoga membantu!
```
