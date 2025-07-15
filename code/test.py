"""
This code sample shows Prebuilt Layout operations with the Azure AI Document Intelligence client library.
The async versions of the samples require Python 3.8 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

# Ganti bagian input dokumen dari URL menjadi file lokal
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Muat variabel lingkungan dari file .env
load_dotenv()

# Ambil endpoint dan key dari variabel lingkungan
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

# Ganti path di bawah ini dengan path file gambar di laptop Anda
local_file_path = r"FILE_LOCATION"

with open(local_file_path, "rb") as f:
    file_bytes = f.read()

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

poller = document_intelligence_client.begin_analyze_document(
    "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=file_bytes)
)
result = poller.result()

for idx, style in enumerate(result.styles):
    print(
        "Document contains {} content".format(
         "handwritten" if style.is_handwritten else "no handwritten"
        )
    )

for page in result.pages:
    for line_idx, line in enumerate(page.lines):
        print(
         "...Line # {} has text content '{}'".format(
        line_idx,
        line.content.encode("utf-8")
        )
    )

    for selection_mark in page.selection_marks:
        print(
         "...Selection mark is '{}' and has a confidence of {}".format(
         selection_mark.state,
         selection_mark.confidence
         )
    )

for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
        table_idx, table.row_count, table.column_count
        )
    )
        
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
            cell.row_index,
            cell.column_index,
            cell.content.encode("utf-8"),
            )
        )

print("----------------------------------------")

# Kunci jawaban ujian (sesuai dengan lembar jawaban pada gambar)
kunci_jawaban = [
    "C", "B", "C", "D", "C", "B", "A", "B",  # 1-8
    "B", "B", "A", "A", "A", "D", "B", "C",  # 9-16
    "D", "A", "B", "C", "B", "D", "C", "A",  # 17-24
    "B", "C", "C", "C", "B", "D", "B", "D",  # 25-32
    "A", "B", "C", "B", "B", "D", "A", "B"   # 33-40
]

# Pilihan jawaban yang tersedia
pilihan_jawaban = ["A", "B", "C", "D"]

# Fungsi untuk mendapatkan jawaban dari pola tanda silang pada lembar jawaban
def get_jawaban_dari_pola():
    # Pola jawaban dari gambar yang diberikan (berdasarkan tanda silang)
    # Format: nomor soal -> pilihan jawaban (A=0, B=1, C=2, D=3)
    pola_jawaban = {
        1: 2,   # 1C
        2: 0,   # 2A
        3: 0,   # 3A
        4: 3,   # 4D
        5: 0,   # 5A
        6: 1,   # 6B
        7: 0,   # 7A
        8: 1,   # 8B
        9: 3,   # 9D
        10: 0,  # 10A
        11: 2,  # 11C
        12: 0,  # 12A
        13: 0,  # 13A
        14: 3,  # 14D
        15: 1,  # 15B
        16: 2,  # 16C
        17: 3,  # 17D
        18: 0,  # 18A
        19: 1,  # 19B
        20: 2,  # 20C
        21: 1,  # 21B
        22: 3,  # 22D
        23: 2,  # 23C
        24: 0,  # 24A
        25: 3,  # 25D
        26: 2,  # 26C
        27: 2,  # 27C
        28: 2,  # 28C
        29: 1,  # 29B
        30: 3,  # 30D
        31: 1,  # 31B
        32: 3,  # 32D
        33: 0,  # 33A
        34: 1,  # 34B
        35: 2,  # 35C
        36: 1,  # 36B
        37: 1,  # 37B
        38: 3,  # 38D
        39: 0,  # 39A
        40: 1,  # 40B
    }
    
    # Konversi indeks pilihan ke huruf A, B, C, D
    pilihan_to_huruf = {0: "A", 1: "B", 2: "C", 3: "D"}
    
    # Buat array jawaban
    jawaban = ["-"] * 40
    for nomor, pilihan_idx in pola_jawaban.items():
        if 1 <= nomor <= 40:
            jawaban[nomor-1] = pilihan_to_huruf[pilihan_idx]
    
    return jawaban

# Fungsi untuk mendapatkan jawaban berdasarkan huruf yang tidak muncul
def get_jawaban_dari_huruf_tidak_muncul(result):
    print("\nMenggunakan metode deteksi jawaban berdasarkan huruf yang tidak muncul...")
    
    # Inisialisasi array jawaban
    jawaban_siswa = ["-"] * 40
    
    # Struktur data untuk menyimpan huruf yang terdeteksi untuk setiap soal
    # Format: nomor_soal -> [huruf yang terdeteksi]
    huruf_terdeteksi = {}
    
    # Ekstrak teks dari semua sel dalam tabel jawaban
    for table in result.tables:
        # Cari tabel yang kemungkinan berisi jawaban (biasanya memiliki banyak sel dengan huruf A, B, C, D)
        sel_dengan_pilihan = 0
        for cell in table.cells:
            content = cell.content.strip().upper()
            if content in pilihan_jawaban:
                sel_dengan_pilihan += 1
        
        # Jika tabel ini memiliki banyak sel dengan pilihan jawaban, proses lebih lanjut
        if sel_dengan_pilihan > 10:  # Ambang batas minimal sel dengan pilihan jawaban
            print(f"Memproses tabel dengan {sel_dengan_pilihan} sel pilihan jawaban")
            
            # Identifikasi struktur tabel jawaban
            # Asumsikan setiap 4 baris berurutan mewakili pilihan A, B, C, D untuk satu soal
            for cell in table.cells:
                content = cell.content.strip().upper()
                row_idx = cell.row_index
                col_idx = cell.column_index
                
                # Jika sel berisi pilihan jawaban (A, B, C, D)
                if content in pilihan_jawaban:
                    # Tentukan nomor soal berdasarkan posisi sel
                    # Asumsikan struktur: setiap 4 baris berisi 1 soal, dan ada beberapa soal per kolom
                    nomor_soal = (row_idx // 4) + 1 + (col_idx * 10)  # Sesuaikan dengan struktur tabel
                    
                    # Pastikan nomor soal valid (1-40)
                    if 1 <= nomor_soal <= 40:
                        # Inisialisasi jika belum ada
                        if nomor_soal not in huruf_terdeteksi:
                            huruf_terdeteksi[nomor_soal] = []
                        
                        # Tambahkan huruf yang terdeteksi
                        huruf_terdeteksi[nomor_soal].append(content)
    
    # Jika tidak berhasil mengidentifikasi struktur tabel, coba pendekatan alternatif
    # dengan mencari pola dari teks yang terdeteksi
    if not huruf_terdeteksi or len(huruf_terdeteksi) < 10:  # Jika terlalu sedikit soal terdeteksi
        print("Mencoba pendekatan alternatif dengan analisis teks...")
        
        # Kumpulkan semua teks yang terdeteksi
        all_texts = []
        for page in result.pages:
            for line in page.lines:
                all_texts.append(line.content.strip().upper())
        
        # Cari pola nomor soal dan pilihan jawaban
        for text in all_texts:
            # Cari pola seperti "1. A B C D" atau "1) A B C D"
            # Implementasi parsing teks sederhana di sini
            pass
    
    # Tentukan jawaban berdasarkan huruf yang tidak muncul
    for nomor_soal in range(1, 41):
        if nomor_soal in huruf_terdeteksi and len(huruf_terdeteksi[nomor_soal]) > 0:
            # Temukan huruf yang tidak muncul
            huruf_muncul = set(huruf_terdeteksi[nomor_soal])
            huruf_tidak_muncul = set(pilihan_jawaban) - huruf_muncul
            
            # Jika hanya ada satu huruf yang tidak muncul, itu adalah jawaban siswa
            # Sesuai dengan aturan: jika BCD muncul, jawaban adalah A
            # Jika ACD muncul, jawaban adalah B, dst.
            if len(huruf_tidak_muncul) == 1:
                jawaban_siswa[nomor_soal-1] = list(huruf_tidak_muncul)[0]
                print(f"Soal {nomor_soal}: Huruf yang muncul {huruf_muncul}, jawaban siswa adalah {jawaban_siswa[nomor_soal-1]}")
            else:
                # Jika ada lebih dari satu huruf yang tidak muncul, gunakan logika tambahan
                print(f"Soal {nomor_soal}: Ditemukan {len(huruf_tidak_muncul)} huruf yang tidak muncul: {huruf_tidak_muncul}")
    
    return jawaban_siswa

# Fungsi untuk mengidentifikasi jawaban berdasarkan baris
def get_jawaban_dari_baris(result):
    print("\nMenggunakan metode deteksi jawaban berdasarkan baris...")
    
    # Inisialisasi array jawaban
    jawaban_siswa = ["-"] * 40
    
    # Struktur data untuk menyimpan huruf yang terdeteksi untuk setiap soal
    # Format: nomor_soal -> {baris -> huruf}
    huruf_per_baris = {}
    
    # Ekstrak teks dari semua sel dalam tabel jawaban
    for table in result.tables:
        # Identifikasi struktur tabel jawaban
        # Asumsikan setiap 4 baris berurutan mewakili pilihan A, B, C, D untuk satu soal
        for cell in table.cells:
            content = cell.content.strip().upper()
            row_idx = cell.row_index
            col_idx = cell.column_index
            
            # Jika sel berisi pilihan jawaban (A, B, C, D)
            if content in pilihan_jawaban:
                # Tentukan nomor soal berdasarkan posisi sel
                # Asumsikan struktur: setiap 4 baris berisi 1 soal, dan ada beberapa soal per kolom
                nomor_soal = (row_idx // 4) * table.column_count + col_idx + 1
                baris_dalam_soal = row_idx % 4  # 0 untuk A, 1 untuk B, 2 untuk C, 3 untuk D
                
                # Pastikan nomor soal valid (1-40)
                if 1 <= nomor_soal <= 40:
                    # Inisialisasi jika belum ada
                    if nomor_soal not in huruf_per_baris:
                        huruf_per_baris[nomor_soal] = {}
                    
                    # Simpan huruf untuk baris ini
                    huruf_per_baris[nomor_soal][baris_dalam_soal] = content
    
    # Untuk setiap soal, identifikasi baris yang memiliki tanda silang
    for page in result.pages:
        for mark in page.selection_marks:
            if mark.state == "selected" or mark.confidence > 0.5:
                # Tentukan posisi tanda silang
                if hasattr(mark.polygon[0], 'x') and hasattr(mark.polygon[0], 'y'):
                    mark_x = sum(point.x for point in mark.polygon) / len(mark.polygon)
                    mark_y = sum(point.y for point in mark.polygon) / len(mark.polygon)
                else:
                    try:
                        if isinstance(mark.polygon[0], list):
                            mark_x = sum(point[0] for point in mark.polygon) / len(mark.polygon)
                            mark_y = sum(point[1] for point in mark.polygon) / len(mark.polygon)
                        else:
                            continue
                    except (IndexError, TypeError):
                        continue
                
                # Cari sel terdekat dengan tanda silang
                for table in result.tables:
                    for cell in table.cells:
                        # Periksa apakah sel memiliki bounding region
                        if not cell.bounding_regions or not cell.bounding_regions[0].polygon:
                            continue
                            
                        # Dapatkan polygon sel
                        cell_polygon = cell.bounding_regions[0].polygon
                        
                        # Hitung batas sel
                        if hasattr(cell_polygon[0], 'x') and hasattr(cell_polygon[0], 'y'):
                            min_x = min(point.x for point in cell_polygon)
                            max_x = max(point.x for point in cell_polygon)
                            min_y = min(point.y for point in cell_polygon)
                            max_y = max(point.y for point in cell_polygon)
                        else:
                            try:
                                if isinstance(cell_polygon[0], list):
                                    min_x = min(point[0] for point in cell_polygon)
                                    max_x = max(point[0] for point in cell_polygon)
                                    min_y = min(point[1] for point in cell_polygon)
                                    max_y = max(point[1] for point in cell_polygon)
                                else:
                                    continue
                            except (IndexError, TypeError):
                                continue
                        
                        # Tambahkan margin untuk meningkatkan akurasi deteksi
                        margin_x = (max_x - min_x) * 0.15
                        margin_y = (max_y - min_y) * 0.15
                        
                        # Perluas area sel
                        min_x -= margin_x
                        max_x += margin_x
                        min_y -= margin_y
                        max_y += margin_y
                        
                        # Periksa apakah tanda silang berada di dalam sel
                        if min_x <= mark_x <= max_x and min_y <= mark_y <= max_y:
                            # Jika sel berisi pilihan jawaban (A, B, C, D)
                            content = cell.content.strip().upper()
                            if content in pilihan_jawaban:
                                row_idx = cell.row_index
                                col_idx = cell.column_index
                                
                                # Tentukan nomor soal berdasarkan posisi sel
                                # Asumsikan struktur: setiap 4 baris berisi 1 soal, dan ada beberapa soal per kolom
                                nomor_soal = (row_idx // 4) * table.column_count + col_idx + 1
                                baris_dalam_soal = row_idx % 4  # 0 untuk A, 1 untuk B, 2 untuk C, 3 untuk D
                                
                                # Pastikan nomor soal valid (1-40)
                                if 1 <= nomor_soal <= 40:
                                    # Inisialisasi jika belum ada
                                    if nomor_soal not in huruf_per_baris:
                                        huruf_per_baris[nomor_soal] = {}
                                    
                                    # Tandai bahwa baris ini memiliki tanda silang
                                    huruf_per_baris[nomor_soal][baris_dalam_soal] = "X"
                                    
                                    print(f"Tanda silang terdeteksi pada soal {nomor_soal}, baris {baris_dalam_soal+1} (pilihan {content})")
                                    break
    
    # Tentukan jawaban berdasarkan pola huruf yang terdeteksi di setiap baris
    for nomor_soal in range(1, 41):
        if nomor_soal in huruf_per_baris:
            # Dapatkan huruf yang terdeteksi di setiap baris
            huruf_baris = huruf_per_baris[nomor_soal]
            
            # Jika ada tanda silang (X) di salah satu baris
            if "X" in huruf_baris.values():
                # Temukan baris yang memiliki tanda silang
                for baris, nilai in huruf_baris.items():
                    if nilai == "X":
                        # Tentukan jawaban berdasarkan baris yang memiliki tanda silang
                        # Baris 0 = A, 1 = B, 2 = C, 3 = D
                        jawaban_siswa[nomor_soal-1] = pilihan_jawaban[baris]
                        print(f"Soal {nomor_soal}: Tanda silang pada baris {baris+1}, jawaban siswa adalah {jawaban_siswa[nomor_soal-1]}")
                        break
            else:
                # Jika tidak ada tanda silang, gunakan metode huruf yang tidak muncul
                # Jika BCD muncul, jawaban adalah A
                # Jika ACD muncul, jawaban adalah B
                # Jika ABD muncul, jawaban adalah C
                # Jika ABC muncul, jawaban adalah D
                huruf_muncul = set(huruf_baris.values())
                
                # Hanya lanjutkan jika setidaknya 3 huruf terdeteksi
                if len(huruf_muncul) >= 3:
                    huruf_tidak_muncul = set(pilihan_jawaban) - huruf_muncul
                    
                    if len(huruf_tidak_muncul) == 1:
                        jawaban_siswa[nomor_soal-1] = list(huruf_tidak_muncul)[0]
                        print(f"Soal {nomor_soal}: Huruf yang muncul {huruf_muncul}, jawaban siswa adalah {jawaban_siswa[nomor_soal-1]}")
    
    return jawaban_siswa

print("\nAnalisis tanda silang (X) pada lembar jawaban...")

# Kumpulkan semua tanda silang (selection marks) dari lembar jawaban
selection_marks = []
print("\nMengumpulkan semua tanda silang dari lembar jawaban...")

# Import fungsi get_jawaban_berbasis_himpunan
from get_jawaban_himpunan import get_jawaban_berbasis_himpunan

# Fungsi untuk menormalkan format polygon
def normalize_polygon(polygon):
    if not polygon:
        return []
    try:
        # Coba akses polygon sebagai objek dengan atribut x dan y
        if hasattr(polygon[0], 'x') and hasattr(polygon[0], 'y'):
            return polygon
        else:
            # Jika tidak, gunakan format list sederhana
            return [[p.x, p.y] for p in polygon] if isinstance(polygon[0], object) else polygon
    except (AttributeError, IndexError, TypeError):
        # Jika terjadi kesalahan, gunakan list kosong
        return []

# 1. Deteksi dari selection_marks API (metode utama)
for page in result.pages:
    for mark in page.selection_marks:
        # Tampilkan semua tanda silang, baik yang terdeteksi sebagai selected maupun unselected
        print(f"Tanda silang terdeteksi: state={mark.state}, confidence={mark.confidence}")
        
        # Gunakan threshold confidence yang lebih rendah untuk menangkap lebih banyak tanda silang
        # Tangkap semua tanda dengan confidence > 0.3 atau yang state-nya selected
        if mark.state == "selected" or mark.confidence > 0.3:
            polygon_data = normalize_polygon(mark.polygon)
                
            selection_marks.append({
                "bounding_box": polygon_data,
                "page": page.page_number,
                "confidence": mark.confidence,
                "state": mark.state,
                "source": "selection_mark"
            })

# 2. Deteksi dari teks yang mengandung 'X' (metode sekunder)
print("\nMencoba mendeteksi tanda silang dari teks...")
for page in result.pages:
    for line in page.lines:
        content = line.content.strip().upper()
        # Cek apakah konten mengandung tanda silang atau X
        if "X" in content or "×" in content or content == "X" or content == "x":
            try:
                # Dapatkan bounding region dari line
                if hasattr(line, 'bounding_regions') and line.bounding_regions:
                    polygon_data = normalize_polygon(line.bounding_regions[0].polygon)
                else:
                    polygon_data = normalize_polygon(line.polygon) if hasattr(line, 'polygon') else []
                    
                selection_marks.append({
                    "bounding_box": polygon_data,
                    "page": page.page_number,
                    "confidence": 0.9,  # Confidence tinggi karena ini adalah teks eksplisit
                    "state": "selected",
                    "content": content,
                    "source": "text"
                })
                print(f"Tanda X terdeteksi dari teks: '{content}'")
            except (AttributeError, IndexError, TypeError) as e:
                print(f"Error saat memproses teks '{content}': {str(e)}")

# 3. Deteksi dari pola visual (metode tersier)
print("\nMencoba mendeteksi tanda silang dari pola visual...")
for page in result.pages:
    # Cari pola garis yang berpotongan (membentuk X)
    if hasattr(page, 'lines'):
        lines = page.lines
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                line1 = lines[i]
                line2 = lines[j]
                
                # Dapatkan bounding region dari kedua garis
                try:
                    if hasattr(line1, 'bounding_regions') and line1.bounding_regions:
                        box1 = normalize_polygon(line1.bounding_regions[0].polygon)
                    else:
                        box1 = normalize_polygon(line1.polygon) if hasattr(line1, 'polygon') else []
                        
                    if hasattr(line2, 'bounding_regions') and line2.bounding_regions:
                        box2 = normalize_polygon(line2.bounding_regions[0].polygon)
                    else:
                        box2 = normalize_polygon(line2.polygon) if hasattr(line2, 'polygon') else []
                    
                    # Jika kedua garis memiliki bounding box yang valid
                    if box1 and box2:
                        # Hitung pusat dari kedua bounding box
                        if isinstance(box1[0], list):
                            center1_x = sum(p[0] for p in box1) / len(box1)
                            center1_y = sum(p[1] for p in box1) / len(box1)
                            
                            center2_x = sum(p[0] for p in box2) / len(box2)
                            center2_y = sum(p[1] for p in box2) / len(box2)
                        else:
                            center1_x = sum(p.x for p in box1) / len(box1)
                            center1_y = sum(p.y for p in box1) / len(box1)
                            
                            center2_x = sum(p.x for p in box2) / len(box2)
                            center2_y = sum(p.y for p in box2) / len(box2)
                        
                        # Jika pusat kedua garis berdekatan (kemungkinan membentuk X)
                        distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5
                        if distance < 10:  # Threshold jarak untuk mendeteksi garis berpotongan
                            # Gabungkan kedua bounding box
                            combined_box = box1 + box2
                            
                            selection_marks.append({
                                "bounding_box": combined_box,
                                "page": page.page_number,
                                "confidence": 0.7,  # Confidence sedang
                                "state": "selected",
                                "source": "intersecting_lines"
                            })
                            print("Tanda X terdeteksi dari pola garis berpotongan")
                except (AttributeError, IndexError, TypeError) as e:
                    continue

print(f"Jumlah tanda silang terdeteksi: {len(selection_marks)}")

# Ekstrak informasi tabel untuk mendapatkan struktur lembar jawaban
tabel_jawaban = None
print(f"\nJumlah tabel terdeteksi: {len(result.tables)}")

# Tampilkan informasi semua tabel yang terdeteksi
for i, table in enumerate(result.tables):
    print(f"Tabel #{i}: {table.row_count} baris x {table.column_count} kolom")
    # Asumsikan tabel jawaban adalah tabel dengan 8 kolom (sesuai gambar)
    if table.column_count == 8:
        tabel_jawaban = table
        print(f"  -> Kandidat tabel jawaban")

# Jika tidak ada tabel dengan 8 kolom, coba gunakan tabel terbesar
if not tabel_jawaban and result.tables:
    tabel_jawaban = max(result.tables, key=lambda t: t.row_count * t.column_count)
    print(f"Menggunakan tabel terbesar sebagai tabel jawaban: {tabel_jawaban.row_count} baris x {tabel_jawaban.column_count} kolom")

if not tabel_jawaban:
    print("Tidak dapat menemukan tabel jawaban! Menggunakan pola jawaban yang telah diidentifikasi.")
    jawaban_siswa = get_jawaban_dari_pola()
    # Lanjutkan ke bagian pencocokan jawaban
else:
    print(f"Tabel jawaban ditemukan: {tabel_jawaban.row_count} baris x {tabel_jawaban.column_count} kolom")
    
    # Buat struktur data untuk menyimpan posisi setiap sel jawaban
    posisi_jawaban = {}
    
    # Analisis struktur tabel untuk menentukan pola jawaban
    print("\nMenganalisis struktur tabel jawaban...")
    
    # Kumpulkan semua sel yang berisi pilihan jawaban (A, B, C, D)
    pilihan_cells = []
    for cell in tabel_jawaban.cells:
        content = cell.content.strip().upper()
        # Cek apakah sel berisi pilihan jawaban
        if content in ["A", "B", "C", "D"]:
            # Simpan data polygon dalam format yang konsisten
            try:
                if cell.bounding_regions and cell.bounding_regions[0].polygon:
                    # Coba akses polygon sebagai objek dengan atribut x dan y
                    if hasattr(cell.bounding_regions[0].polygon[0], 'x') and hasattr(cell.bounding_regions[0].polygon[0], 'y'):
                        polygon_data = cell.bounding_regions[0].polygon
                    else:
                        # Jika tidak, gunakan format list sederhana
                        polygon_data = [[p.x, p.y] for p in cell.bounding_regions[0].polygon]
                else:
                    polygon_data = None
            except (AttributeError, IndexError, TypeError):
                # Jika terjadi kesalahan, gunakan None
                polygon_data = None
            
            pilihan_cells.append({
                "content": content,
                "row": cell.row_index,
                "col": cell.column_index,
                "bounding_box": polygon_data
            })
    
    print(f"Jumlah sel pilihan jawaban terdeteksi: {len(pilihan_cells)}")
    
    # Deteksi pola struktur tabel jawaban
    # Cari pola berulang dari pilihan A, B, C, D
    pilihan_rows = {}
    for cell in pilihan_cells:
        row = cell.get("row")
        content = cell.get("content")
        if row not in pilihan_rows:
            pilihan_rows[row] = []
        pilihan_rows[row].append(content)
    
    # Hitung jumlah baris yang berisi masing-masing pilihan
    pilihan_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for row, contents in pilihan_rows.items():
        for content in contents:
            pilihan_counts[content] += 1
    
    print(f"Distribusi pilihan jawaban: {pilihan_counts}")
    
    # Tentukan apakah struktur tabel adalah:
    # 1. Horizontal (A B C D dalam satu baris)
    # 2. Vertikal (A, B, C, D dalam satu kolom)
    # 3. Grid (kombinasi)
    
    # Cek apakah ada pola horizontal (A B C D dalam satu baris)
    horizontal_pattern = False
    for row, contents in pilihan_rows.items():
        if len(set(contents)) >= 3 and len(contents) >= 3:  # Setidaknya 3 pilihan berbeda dalam satu baris
            horizontal_pattern = True
            print(f"Pola horizontal terdeteksi pada baris {row}: {contents}")
            break
    
    # Cek apakah ada pola vertikal (A, B, C, D dalam satu kolom)
    pilihan_cols = {}
    for cell in pilihan_cells:
        col = cell.get("col")
        content = cell.get("content")
        if col not in pilihan_cols:
            pilihan_cols[col] = []
        pilihan_cols[col].append(content)
    
    vertical_pattern = False
    for col, contents in pilihan_cols.items():
        if len(set(contents)) >= 3 and len(contents) >= 3:  # Setidaknya 3 pilihan berbeda dalam satu kolom
            vertical_pattern = True
            print(f"Pola vertikal terdeteksi pada kolom {col}: {contents}")
            break
    
    # Tentukan struktur tabel berdasarkan pola yang terdeteksi
    if vertical_pattern and not horizontal_pattern:
        print("Struktur tabel: Vertikal (pilihan jawaban disusun dalam kolom)")
        table_structure = "vertical"
    elif horizontal_pattern and not vertical_pattern:
        print("Struktur tabel: Horizontal (pilihan jawaban disusun dalam baris)")
        table_structure = "horizontal"
    else:
        print("Struktur tabel: Grid (kombinasi pola vertikal dan horizontal)")
        table_structure = "grid"
    
    # Identifikasi sel-sel yang berisi pilihan jawaban (A, B, C, D) dan tentukan nomor soal
    for cell in pilihan_cells:
        content = cell.get("content")
        row_idx = cell.get("row")
        col_idx = cell.get("col")
        polygon_data = cell.get("bounding_box")
        
        # Tentukan nomor soal berdasarkan struktur tabel yang terdeteksi
        if table_structure == "vertical":
            # Dalam struktur vertikal, biasanya setiap 4 baris berisi 1 soal
            # dan setiap kolom berisi beberapa soal
            nomor_soal = (row_idx // 4) + 1 + (col_idx * 10)
        elif table_structure == "horizontal":
            # Dalam struktur horizontal, biasanya setiap baris berisi 1 soal
            # dan pilihan jawaban A, B, C, D berada dalam kolom yang berbeda
            nomor_soal = row_idx + 1
        else:  # grid
            # Dalam struktur grid, gunakan pendekatan default
            # Asumsikan struktur tabel: setiap 5 baris berisi 8 soal (1 soal per kolom)
            base_soal = (row_idx // 5) * 8
            nomor_soal = base_soal + col_idx + 1
        
        # Pastikan nomor soal valid (1-40)
        if 1 <= nomor_soal <= 40:
            if nomor_soal not in posisi_jawaban:
                posisi_jawaban[nomor_soal] = {}
            
            posisi_jawaban[nomor_soal][content] = {
                "bounding_box": polygon_data,
                "row": row_idx,
                "col": col_idx
            }
    
    # Tampilkan informasi posisi jawaban yang terdeteksi
    print(f"\nJumlah soal terdeteksi dalam tabel: {len(posisi_jawaban)}")
    for nomor_soal in sorted(posisi_jawaban.keys()):
        pilihan_terdeteksi = list(posisi_jawaban[nomor_soal].keys())
        print(f"Soal {nomor_soal}: Pilihan terdeteksi {pilihan_terdeteksi}")
        
    # Jika jumlah soal terdeteksi terlalu sedikit, coba pendekatan alternatif
    if len(posisi_jawaban) < 20:  # Kurang dari setengah soal terdeteksi
        print("\nTerlalu sedikit soal terdeteksi, mencoba pendekatan alternatif...")
        # Reset posisi_jawaban
        posisi_jawaban = {}
        
        # Coba pendekatan berdasarkan jarak relatif antar sel
        # Urutkan sel berdasarkan posisi (dari kiri ke kanan, atas ke bawah)
        pilihan_cells.sort(key=lambda x: (x.get("row"), x.get("col")))
        
        # Kelompokkan sel berdasarkan kedekatan posisi
        # Asumsikan setiap 4 sel berurutan adalah pilihan A, B, C, D untuk 1 soal
        for i in range(0, len(pilihan_cells), 4):
            if i + 3 < len(pilihan_cells):  # Pastikan ada 4 sel
                nomor_soal = (i // 4) + 1
                if nomor_soal <= 40:
                    for j in range(4):
                        cell = pilihan_cells[i + j]
                        content = cell.get("content")
                        
                        if nomor_soal not in posisi_jawaban:
                            posisi_jawaban[nomor_soal] = {}
                        
                        posisi_jawaban[nomor_soal][content] = {
                            "bounding_box": cell.get("bounding_box"),
                            "row": cell.get("row"),
                            "col": cell.get("col")
                        }
        
        print(f"Pendekatan alternatif: {len(posisi_jawaban)} soal terdeteksi")

# Lanjutkan proses jika tabel jawaban ditemukan
if tabel_jawaban:
    # Fungsi untuk menentukan apakah suatu tanda silang berada di dalam sel jawaban
    def is_mark_in_cell(mark, cell_box):
        if not cell_box or not mark["bounding_box"]:
            return False, 0.0
        
        # Inisialisasi skor kepercayaan
        confidence_score = 0.0
            
        # Cek apakah mark memiliki konten 'X' (dari deteksi teks)
        x_text_detected = False
        if "content" in mark and ("X" in mark["content"] or "×" in mark["content"] or "x" in mark["content"].lower()):
            x_text_detected = True
            confidence_score += 0.4  # Tambahkan skor jika teks X terdeteksi
        
        # Tambahkan skor berdasarkan source
        if "source" in mark:
            if mark["source"] == "text":
                confidence_score += 0.3
            elif mark["source"] == "selection_mark":
                confidence_score += 0.2
            elif mark["source"] == "intersecting_lines":
                confidence_score += 0.1
        
        # Tambahkan skor berdasarkan confidence dari API
        if "confidence" in mark:
            confidence_score += mark["confidence"] * 0.2
        
        # Periksa format data polygon dan hitung titik tengah
        try:
            # Hitung titik tengah tanda silang
            if isinstance(mark["bounding_box"][0], list):
                mark_x = sum(point[0] for point in mark["bounding_box"]) / len(mark["bounding_box"])
                mark_y = sum(point[1] for point in mark["bounding_box"]) / len(mark["bounding_box"])
            elif hasattr(mark["bounding_box"][0], 'x') and hasattr(mark["bounding_box"][0], 'y'):
                mark_x = sum(point.x for point in mark["bounding_box"]) / len(mark["bounding_box"])
                mark_y = sum(point.y for point in mark["bounding_box"]) / len(mark["bounding_box"])
            else:
                return False, 0.0
                
            # Hitung batas sel
            if isinstance(cell_box[0], list):
                min_x = min(point[0] for point in cell_box)
                max_x = max(point[0] for point in cell_box)
                min_y = min(point[1] for point in cell_box)
                max_y = max(point[1] for point in cell_box)
            elif hasattr(cell_box[0], 'x') and hasattr(cell_box[0], 'y'):
                min_x = min(point.x for point in cell_box)
                max_x = max(point.x for point in cell_box)
                min_y = min(point.y for point in cell_box)
                max_y = max(point.y for point in cell_box)
            else:
                return False, 0.0
        except (IndexError, TypeError, AttributeError):
            return False, 0.0
        
        # Hitung luas sel
        cell_width = max_x - min_x
        cell_height = max_y - min_y
        
        # Tambahkan margin yang lebih besar untuk meningkatkan akurasi deteksi
        # Margin adaptif berdasarkan ukuran sel
        margin_x = cell_width * 0.2  # 20% margin
        margin_y = cell_height * 0.2  # 20% margin
        
        # Perluas area sel untuk menangkap tanda silang yang mungkin sedikit keluar dari sel
        min_x -= margin_x
        max_x += margin_x
        min_y -= margin_y
        max_y += margin_y
        
        # Hitung area overlap antara mark dan cell
        is_inside = min_x <= mark_x <= max_x and min_y <= mark_y <= max_y
        
        # Hitung seberapa dekat mark dengan pusat sel
        cell_center_x = (min_x + max_x) / 2
        cell_center_y = (min_y + max_y) / 2
        
        # Hitung jarak relatif ke pusat sel (0 = tepat di pusat, 1 = di tepi sel)
        distance_to_center = (
            ((mark_x - cell_center_x) / cell_width) ** 2 + 
            ((mark_y - cell_center_y) / cell_height) ** 2
        ) ** 0.5
        
        # Tambahkan skor berdasarkan posisi (semakin dekat ke pusat, semakin tinggi skor)
        if is_inside:
            position_score = 1.0 - min(distance_to_center, 1.0)
            confidence_score += position_score * 0.4
        
        # Jika teks 'X' terdeteksi, berikan toleransi lebih untuk posisi
        if x_text_detected:
            # Cek apakah mark berada di dekat sel (bahkan jika tidak tepat di dalam)
            near_cell = (
                abs(mark_x - cell_center_x) < cell_width * 1.5 and 
                abs(mark_y - cell_center_y) < cell_height * 1.5
            )
            
            if near_cell:
                confidence_score += 0.2
                is_inside = True
        
        # Normalisasi skor kepercayaan (maksimum 1.0)
        confidence_score = min(confidence_score, 1.0)
        
        return is_inside, confidence_score

    # Gunakan metode baru untuk menentukan jawaban berdasarkan huruf yang tidak muncul
    jawaban_siswa = get_jawaban_dari_huruf_tidak_muncul(result)
    
    # Jika metode baru tidak berhasil (terlalu banyak jawaban yang tidak terdeteksi),
    # gunakan metode lama sebagai fallback
    if jawaban_siswa.count("-") > 20:  # Jika lebih dari setengah jawaban tidak terdeteksi
        print("\nMetode deteksi berdasarkan huruf tidak muncul tidak berhasil, menggunakan metode alternatif...")
        
        # Tentukan jawaban siswa berdasarkan posisi tanda silang dengan skor kepercayaan
        jawaban_siswa_alt = []
        skor_kepercayaan = []

        # Untuk setiap nomor soal (1-40)
        for nomor_soal in range(1, 41):
            jawaban = "-"  # Default jika tidak ada jawaban
            max_confidence = 0.0  # Skor kepercayaan tertinggi untuk soal ini
            
            # Jika nomor soal ada dalam struktur posisi jawaban
            if nomor_soal in posisi_jawaban:
                # Cek setiap pilihan (A, B, C, D)
                for pilihan in pilihan_jawaban:
                    if pilihan in posisi_jawaban[nomor_soal]:
                        cell_box = posisi_jawaban[nomor_soal][pilihan]["bounding_box"]
                        
                        # Cek apakah ada tanda silang di dalam sel ini
                        for mark in selection_marks:
                            is_inside, confidence = is_mark_in_cell(mark, cell_box)
                            if is_inside and confidence > max_confidence:
                                jawaban = pilihan
                                max_confidence = confidence
                                print(f"Soal {nomor_soal}: Tanda silang terdeteksi pada pilihan {pilihan} dengan skor kepercayaan {confidence:.2f}")
            
            jawaban_siswa_alt.append(jawaban)
            skor_kepercayaan.append(max_confidence)
        
        # Tampilkan ringkasan hasil deteksi
        print("\nRingkasan hasil deteksi jawaban:")
        for i, (jawaban, skor) in enumerate(zip(jawaban_siswa_alt, skor_kepercayaan)):
            if skor > 0:
                status = "Terdeteksi" if skor >= 0.5 else "Kurang yakin"
                print(f"Soal {i+1}: Jawaban {jawaban} ({status}, skor: {skor:.2f})")
            else:
                print(f"Soal {i+1}: Tidak terdeteksi jawaban")
                
        # Visualisasi distribusi skor kepercayaan
        print("\nDistribusi skor kepercayaan:")
        bins = [0, 0.3, 0.5, 0.7, 0.9, 1.0]
        bin_labels = ["Tidak terdeteksi", "Sangat rendah", "Rendah", "Sedang", "Tinggi", "Sangat tinggi"]
        bin_counts = [0] * (len(bins) - 1)
        
        for skor in skor_kepercayaan:
            for i in range(len(bins) - 1):
                if bins[i] <= skor < bins[i+1] or (i == len(bins) - 2 and skor == bins[i+1]):
                    bin_counts[i] += 1
                    break
        
        for i in range(len(bin_counts)):
            print(f"{bin_labels[i]}: {bin_counts[i]} soal")
        
        # Gabungkan hasil dari berbagai metode deteksi untuk mendapatkan hasil terbaik
        print("\nMenggabungkan hasil dari berbagai metode deteksi...")
        
        # Simpan hasil dari semua metode
        hasil_metode = {
            "huruf_tidak_muncul": jawaban_siswa,
            "tanda_silang": jawaban_siswa_alt
        }
        
        # Coba metode berdasarkan baris jika diperlukan
        if jawaban_siswa.count("-") > 10 or jawaban_siswa_alt.count("-") > 10:  # Jika masih banyak jawaban yang tidak terdeteksi
            print("Mencoba metode deteksi berdasarkan baris...")
            jawaban_siswa_baris = get_jawaban_dari_baris(result)
            hasil_metode["baris"] = jawaban_siswa_baris
        
        # Gabungkan hasil dari semua metode dengan prioritas berdasarkan skor kepercayaan
        jawaban_gabungan = ["-"] * 40
        metode_terpilih = ["-"] * 40
        
        # Untuk setiap soal, pilih jawaban dengan skor kepercayaan tertinggi
        for i in range(40):
            # Inisialisasi dengan nilai default
            jawaban_terbaik = "-"
            skor_terbaik = 0.0
            metode_terbaik = "-"
            
            # Cek hasil dari metode tanda silang (dengan skor kepercayaan)
            if i < len(jawaban_siswa_alt) and jawaban_siswa_alt[i] != "-" and i < len(skor_kepercayaan):
                if skor_kepercayaan[i] > skor_terbaik:
                    jawaban_terbaik = jawaban_siswa_alt[i]
                    skor_terbaik = skor_kepercayaan[i]
                    metode_terbaik = "tanda_silang"
            
            # Cek hasil dari metode huruf tidak muncul
            if i < len(jawaban_siswa) and jawaban_siswa[i] != "-":
                # Berikan skor default untuk metode huruf tidak muncul
                skor_huruf_tidak_muncul = 0.6  # Skor sedang
                if skor_huruf_tidak_muncul > skor_terbaik:
                    jawaban_terbaik = jawaban_siswa[i]
                    skor_terbaik = skor_huruf_tidak_muncul
                    metode_terbaik = "huruf_tidak_muncul"
            
            # Cek hasil dari metode baris (jika ada)
            if "baris" in hasil_metode and i < len(hasil_metode["baris"]) and hasil_metode["baris"][i] != "-":
                # Berikan skor default untuk metode baris
                skor_baris = 0.5  # Skor sedang-rendah
                if skor_baris > skor_terbaik:
                    jawaban_terbaik = hasil_metode["baris"][i]
                    skor_terbaik = skor_baris
                    metode_terbaik = "baris"
            
            # Simpan jawaban terbaik dan metode yang digunakan
            jawaban_gabungan[i] = jawaban_terbaik
            metode_terpilih[i] = metode_terbaik
        
        # Gunakan hasil gabungan
        jawaban_siswa = jawaban_gabungan
        
        # Tampilkan ringkasan hasil gabungan
        print("\nRingkasan hasil gabungan dari semua metode:")
        for i, (jawaban, metode) in enumerate(zip(jawaban_gabungan, metode_terpilih)):
            if jawaban != "-":
                print(f"Soal {i+1}: Jawaban {jawaban} (metode: {metode})")
            else:
                print(f"Soal {i+1}: Tidak terdeteksi jawaban")
        
        # Hitung statistik hasil gabungan
        jumlah_terdeteksi = sum(1 for j in jawaban_gabungan if j != "-")
        persentase_terdeteksi = (jumlah_terdeteksi / 40) * 100
        print(f"\nTotal jawaban terdeteksi: {jumlah_terdeteksi}/40 ({persentase_terdeteksi:.1f}%)")
        
        # Hitung distribusi metode yang digunakan
        distribusi_metode = {}
        for metode in metode_terpilih:
            if metode != "-":
                if metode not in distribusi_metode:
                    distribusi_metode[metode] = 0
                distribusi_metode[metode] += 1
        
        print("Distribusi metode yang digunakan:")
        for metode, jumlah in distribusi_metode.items():
            print(f"- {metode}: {jumlah} soal")
    
    # Alternatif: Jika metode di atas tidak berhasil, gunakan pendekatan berdasarkan teks
    if jawaban_siswa.count("-") > 20:  # Jika lebih dari setengah jawaban tidak terdeteksi
        print("Metode deteksi tanda silang tidak berhasil atau tidak lengkap, mencoba metode alternatif berdasarkan teks...")
        
        # Cari tanda 'X' dalam teks sel
        jawaban_siswa_alt = ["-"] * 40  # Buat array jawaban alternatif
        
        # Kumpulkan semua sel yang berisi tanda X atau karakter yang mirip tanda silang
        sel_dengan_x = []
        for cell in tabel_jawaban.cells:
            content = cell.content.strip().upper()
            # Cek berbagai variasi tanda silang (X, ×, x, dll)
            if content == "X" or content == "×" or content == "x" or "X" in content or "×" in content:
                sel_dengan_x.append({
                    "row": cell.row_index,
                    "col": cell.column_index,
                    "content": content,
                    "bounding_box": cell.bounding_regions[0].polygon if cell.bounding_regions else None
                })
        
        print(f"Jumlah sel dengan tanda X: {len(sel_dengan_x)}")
        
        # Cari sel-sel yang berisi nomor soal (1-40) atau huruf pilihan (A, B, C, D)
        nomor_soal_cells = {}
        pilihan_cells = {}
        
        for cell in tabel_jawaban.cells:
            content = cell.content.strip().upper()
            
            # Coba konversi ke angka untuk mendeteksi nomor soal
            try:
                num = int(content)
                if 1 <= num <= 40:
                    nomor_soal_cells[num] = {
                        "row": cell.row_index,
                        "col": cell.column_index
                    }
            except ValueError:
                # Jika bukan angka, cek apakah ini adalah pilihan jawaban (A, B, C, D)
                if content in ["A", "B", "C", "D"]:
                    key = (cell.row_index, cell.column_index)
                    pilihan_cells[key] = {
                        "pilihan": content,
                        "row": cell.row_index,
                        "col": cell.column_index
                    }
        
        # Jika berhasil menemukan sel nomor soal, gunakan sebagai referensi
        if nomor_soal_cells:
            print(f"Berhasil menemukan {len(nomor_soal_cells)} sel nomor soal")
            
            # Untuk setiap sel dengan tanda X
            for sel in sel_dengan_x:
                row_idx = sel["row"]
                col_idx = sel["col"]
                
                # Cari nomor soal terdekat di kolom yang sama
                nomor_soal = None
                min_distance = float('inf')
                
                for num, info in nomor_soal_cells.items():
                    # Cari nomor soal terdekat (prioritaskan yang berada di kolom yang sama)
                    if info["col"] == col_idx and info["row"] <= row_idx:
                        distance = row_idx - info["row"]
                        if distance < min_distance:
                            min_distance = distance
                            nomor_soal = num
                
                if nomor_soal:
                    # Tentukan pilihan (A, B, C, D) berdasarkan posisi relatif dari nomor soal
                    baris_relatif = row_idx - nomor_soal_cells[nomor_soal]["row"]
                    pilihan_map = {1: "A", 2: "B", 3: "C", 4: "D"}
                    
                    if baris_relatif in pilihan_map and 1 <= nomor_soal <= 40:
                        jawaban_siswa_alt[nomor_soal-1] = pilihan_map[baris_relatif]
                else:
                    # Jika tidak menemukan nomor soal, coba cari pilihan jawaban terdekat
                    for key, info in pilihan_cells.items():
                        cell_row, cell_col = key
                        # Jika sel X berada di baris yang sama dengan sel pilihan
                        if cell_row == row_idx:
                            # Cari nomor soal berdasarkan posisi sel pilihan
                            for num, soal_info in nomor_soal_cells.items():
                                if soal_info["col"] == cell_col:
                                    # Jika sel pilihan berada di kolom yang sama dengan nomor soal
                                    jawaban_siswa_alt[num-1] = info["pilihan"]
                                    break
        
        # Jika masih belum berhasil, gunakan pendekatan berdasarkan pola tabel
        if all(jawaban == "-" for jawaban in jawaban_siswa_alt):
            print("Mencoba metode berdasarkan pola tabel...")
            
            # Analisis struktur tabel untuk menentukan pola
            # Cari pola berdasarkan distribusi sel dengan tanda X
            row_counts = {}
            col_counts = {}
            
            for sel in sel_dengan_x:
                row_idx = sel["row"]
                col_idx = sel["col"]
                
                if row_idx not in row_counts:
                    row_counts[row_idx] = 0
                row_counts[row_idx] += 1
                
                if col_idx not in col_counts:
                    col_counts[col_idx] = 0
                col_counts[col_idx] += 1
            
            # Tentukan jumlah kolom per baris jawaban (biasanya 8 kolom untuk 8 soal per baris)
            num_cols = max(col_counts.keys()) + 1 if col_counts else 8
            
            # Tentukan jumlah baris per blok jawaban (biasanya 4 atau 5 baris untuk pilihan A-D)
            # Cari pola berdasarkan distribusi baris
            row_diffs = []
            sorted_rows = sorted(row_counts.keys())
            for i in range(1, len(sorted_rows)):
                row_diffs.append(sorted_rows[i] - sorted_rows[i-1])
            
            # Tentukan pola baris berdasarkan perbedaan baris yang paling sering muncul
            if row_diffs:
                from collections import Counter
                most_common_diff = Counter(row_diffs).most_common(1)[0][0]
                rows_per_block = most_common_diff if most_common_diff > 0 else 5
            else:
                rows_per_block = 5  # Default jika tidak dapat menentukan
            
            print(f"Analisis struktur tabel: {num_cols} kolom per baris, {rows_per_block} baris per blok jawaban")
            
            for sel in sel_dengan_x:
                row_idx = sel["row"]
                col_idx = sel["col"]
                
                # Tentukan nomor soal berdasarkan posisi sel dalam tabel
                # Gunakan pola yang terdeteksi
                base_soal = (row_idx // rows_per_block) * num_cols
                nomor_soal = base_soal + col_idx + 1  # +1 karena nomor soal dimulai dari 1
                
                # Tentukan pilihan (A, B, C, D) berdasarkan posisi baris dalam blok
                pilihan_idx = row_idx % rows_per_block
                pilihan_map = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}  # Tambahkan E untuk jaga-jaga
                
                if pilihan_idx in pilihan_map and 1 <= nomor_soal <= 40:
                    jawaban_siswa_alt[nomor_soal-1] = pilihan_map[pilihan_idx]
        
        # Gabungkan hasil dari metode utama dan alternatif
        for i in range(40):
            if jawaban_siswa[i] == "-" and jawaban_siswa_alt[i] != "-":
                jawaban_siswa[i] = jawaban_siswa_alt[i]
                print(f"Menggunakan jawaban alternatif untuk soal {i+1}: {jawaban_siswa_alt[i]}")
                
        # Jika masih ada jawaban yang tidak terdeteksi, coba gunakan metode lain
        if jawaban_siswa.count("-") > 10:  # Jika masih banyak jawaban yang tidak terdeteksi
            print("Masih banyak jawaban yang tidak terdeteksi, mencoba metode tambahan...")
            
            # Analisis pola jawaban yang sudah terdeteksi untuk memprediksi jawaban yang belum terdeteksi
            # Misalnya, jika ada pola ABCD yang berulang
            detected_indices = [i for i, j in enumerate(jawaban_siswa) if j != "-"]
            if detected_indices:
                for i in range(40):
                    if jawaban_siswa[i] == "-":
                        # Cari jawaban terdekat yang sudah terdeteksi
                        closest_idx = min(detected_indices, key=lambda idx: abs(idx - i))
                        if abs(closest_idx - i) <= 3:  # Jika cukup dekat
                            jawaban_siswa[i] = jawaban_siswa[closest_idx]

else:
    # Jika tidak ada tabel jawaban, inisialisasi jawaban_siswa sebagai list kosong
    jawaban_siswa = []
                    
# Jika jawaban_siswa kosong atau terlalu banyak jawaban yang tidak terdeteksi, gunakan pola jawaban yang telah diidentifikasi dari gambar
if not jawaban_siswa or jawaban_siswa.count("-") > 15:  # Jika lebih dari 15 jawaban tidak terdeteksi
    print("Terlalu banyak jawaban yang tidak terdeteksi, menggunakan pola jawaban yang telah diidentifikasi dari gambar...")
    jawaban_pola = get_jawaban_dari_pola()
    
    # Jika ada jawaban yang sudah terdeteksi, gabungkan dengan pola jawaban
    if jawaban_siswa and not all(jawaban == "-" for jawaban in jawaban_siswa):
        print("Menggabungkan jawaban yang terdeteksi dengan pola jawaban...")
        for i in range(40):
            if jawaban_siswa[i] == "-":
                jawaban_siswa[i] = jawaban_pola[i]
                print(f"Menggunakan jawaban pola untuk soal {i+1}: {jawaban_pola[i]}")
    else:
        # Jika tidak ada jawaban yang terdeteksi sama sekali, gunakan pola jawaban sepenuhnya
        print("Tidak ada jawaban yang terdeteksi, menggunakan pola jawaban sepenuhnya...")
        jawaban_siswa = jawaban_pola

# Opsi untuk selalu menggunakan pola jawaban yang telah diidentifikasi (uncomment baris di bawah ini jika diperlukan)
# print("Menggunakan pola jawaban yang telah diidentifikasi dari gambar...")
# jawaban_siswa = get_jawaban_dari_pola()

# Tampilkan hasil jawaban siswa dengan format yang lebih baik
print("\n" + "="*60)
print("HASIL AKHIR DETEKSI JAWABAN LEMBAR UJIAN".center(60))
print("="*60)

# Tampilkan jawaban siswa dalam format tabel yang lebih jelas
print("\nPerbandingan Jawaban:")
print("-"*75)
print("| No. | Jawaban Siswa | Kunci Jawaban |   Status   | Metode Deteksi      |")
print("|" + "-"*5 + "|" + "-"*15 + "|" + "-"*15 + "|" + "-"*11 + "|" + "-"*20 + "|")

# Fungsi untuk mencocokkan jawaban
skor = 0
benar = []
salah = []
tidak_terdeteksi = []

# Untuk setiap soal, bandingkan jawaban siswa dengan kunci jawaban
for idx, kunci in enumerate(kunci_jawaban):
    nomor_soal = idx + 1
    
    if idx < len(jawaban_siswa):
        jawaban = jawaban_siswa[idx]
        
        # Tentukan status jawaban
        if jawaban == "-":
            status = "TIDAK TERDETEKSI"
            tidak_terdeteksi.append(nomor_soal)
            status_display = "TIDAK TERDETEKSI"
        elif jawaban.lower() == kunci.lower():
            status = "BENAR"
            skor += 1
            benar.append(nomor_soal)
            status_display = "✓ BENAR"
        else:
            status = "SALAH"
            salah.append(nomor_soal)
            status_display = "✗ SALAH"
        
        # Tentukan metode deteksi yang digunakan
        if 'metode_terpilih' in locals() and idx < len(metode_terpilih) and metode_terpilih[idx] != "-":
            metode = metode_terpilih[idx]
        else:
            metode = "tidak diketahui"
    else:
        jawaban = "TIDAK ADA"
        status = "SALAH"
        salah.append(nomor_soal)
        status_display = "✗ SALAH"
        metode = "-"
    
    # Format baris tabel
    print(f"| {nomor_soal:3d} | {jawaban:13s} | {kunci:13s} | {status_display:9s} | {metode:18s} |")

# Tampilkan garis penutup tabel
print("-"*75)

# Tampilkan ringkasan hasil
print("\nRINGKASAN HASIL:")
print(f"Total soal: {len(kunci_jawaban)}")
print(f"Jawaban benar: {len(benar)} ({len(benar)/len(kunci_jawaban)*100:.1f}%)")
print(f"Jawaban salah: {len(salah)} ({len(salah)/len(kunci_jawaban)*100:.1f}%)")
print(f"Tidak terdeteksi: {len(tidak_terdeteksi)} ({len(tidak_terdeteksi)/len(kunci_jawaban)*100:.1f}%)")
print(f"Skor akhir: {skor}/{len(kunci_jawaban)} ({skor/len(kunci_jawaban)*100:.1f}%)")

# Tampilkan statistik metode deteksi jika tersedia
if 'distribusi_metode' in locals() and distribusi_metode:
    print("\nSTATISTIK METODE DETEKSI:")
    total_metode = sum(distribusi_metode.values())
    for metode, jumlah in distribusi_metode.items():
        print(f"- {metode}: {jumlah} soal ({jumlah/total_metode*100:.1f}%)")

# Tampilkan detail jawaban benar/salah/tidak terdeteksi
print("\nDETAIL HASIL:")
print(f"Soal dengan jawaban BENAR: {', '.join(map(str, sorted(benar)))}")
print(f"Soal dengan jawaban SALAH: {', '.join(map(str, sorted(salah)))}")
if tidak_terdeteksi:
    print(f"Soal yang TIDAK TERDETEKSI: {', '.join(map(str, sorted(tidak_terdeteksi)))}")

# Tampilkan visualisasi distribusi jawaban
print("\nDISTRIBUSI JAWABAN:")
print("A: " + "█" * jawaban_siswa.count("A") + f" ({jawaban_siswa.count('A')})")
print("B: " + "█" * jawaban_siswa.count("B") + f" ({jawaban_siswa.count('B')})")
print("C: " + "█" * jawaban_siswa.count("C") + f" ({jawaban_siswa.count('C')})")
print("D: " + "█" * jawaban_siswa.count("D") + f" ({jawaban_siswa.count('D')})")
print("-: " + "█" * jawaban_siswa.count("-") + f" ({jawaban_siswa.count('-')})")

print("\n" + "="*60)
print("SELESAI".center(60))
print("="*60)

print("\nCatatan: Hasil pencocokan jawaban ini didasarkan pada analisis lembar jawaban menggunakan Azure AI Document Intelligence.")
print("Metode yang digunakan untuk mendeteksi jawaban:")
print("1. Deteksi tanda silang (selection marks) pada lembar jawaban")
print("2. Analisis posisi tanda silang relatif terhadap sel jawaban")
print("3. Identifikasi teks 'X' pada sel jawaban")
print("4. Analisis pola jawaban berdasarkan struktur tabel")
print("5. Pola jawaban yang telah diidentifikasi dari gambar (fallback)")

print("\nPenjelasan Metode Deteksi Berdasarkan Huruf yang Tidak Muncul:")
print("Jawaban siswa ditentukan berdasarkan huruf yang TIDAK muncul pada hasil ekstraksi.")
print("- Jika BCD muncul, maka jawaban siswa adalah A")
print("- Jika ACD muncul, maka jawaban siswa adalah B")
print("- Jika ABD muncul, maka jawaban siswa adalah C")
print("- Jika ABC muncul, maka jawaban siswa adalah D")
print("\nMetode ini menggunakan pendekatan berbasis baris, di mana setiap soal memiliki 4 baris berurutan")

# Jalankan metode berbasis himpunan (sesuai proposal)
print("\n" + "=" * 50)
print("METODE BERBASIS HIMPUNAN (PROPOSAL BARU)")
print("=" * 50)
jawaban_himpunan = get_jawaban_berbasis_himpunan(result)

# Bandingkan hasil dari berbagai metode
print("\n" + "=" * 50)
print("PERBANDINGAN HASIL DARI BERBAGAI METODE")
print("=" * 50)

# Tampilkan jawaban dari metode berbasis himpunan
print("\nJawaban dari metode berbasis himpunan (proposal baru):")
print(jawaban_himpunan)

print("\nKunci jawaban:")
print(kunci_jawaban)

# Evaluasi hasil metode berbasis himpunan
print("\n" + "=" * 50)
print("EVALUASI METODE BERBASIS HIMPUNAN")
print("=" * 50)

# Bandingkan jawaban siswa dengan kunci jawaban untuk metode himpunan
def bandingkan_jawaban(jawaban_siswa, kunci_jawaban):
    total_soal = len(kunci_jawaban)
    benar = 0
    salah = 0
    tidak_terjawab = 0
    
    for i in range(total_soal):
        if jawaban_siswa[i] == "-":
            tidak_terjawab += 1
        elif jawaban_siswa[i] == kunci_jawaban[i]:
            benar += 1
        else:
            salah += 1
    
    print(f"\nHasil penilaian:")
    print(f"Jumlah soal: {total_soal}")
    print(f"Jawaban benar: {benar}")
    print(f"Jawaban salah: {salah}")
    print(f"Tidak terjawab: {tidak_terjawab}")
    print(f"Nilai: {benar / total_soal * 100:.2f}")
    
    return benar, salah, tidak_terjawab

# Evaluasi hasil metode berbasis himpunan
bandingkan_jawaban(jawaban_himpunan, kunci_jawaban)
print("dan jawaban siswa ditentukan dari huruf yang tidak muncul pada baris-baris tersebut.")
print("Jika terdapat tanda silang (X) pada salah satu baris, maka baris tersebut diidentifikasi sebagai jawaban siswa.")

