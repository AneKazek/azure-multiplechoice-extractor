def get_jawaban_berbasis_himpunan(result):
    """
    Fungsi untuk mendapatkan jawaban siswa berdasarkan pendekatan himpunan.
    Algoritma:
    1. Baca semua baris hasil API ke dalam list Python
    2. Buang baris-baris yang bukan berarti nomor soal atau pilihan
    3. Kelompokkan setiap 4 baris jadi satu blok
    4. Hitung himpunan penuh {'A','B','C','D'}, lalu cari elemen yang hilang
    5. Simpan hasilnya dalam struktur data
    """
    print("\nMenggunakan metode deteksi jawaban berbasis himpunan...")
    
    # Inisialisasi array jawaban
    jawaban_siswa = ["-"] * 40
    
    # Pilihan jawaban yang tersedia
    pilihan_lengkap = set(["A", "B", "C", "D"])
    
    # 1. Baca semua baris hasil API ke dalam list Python
    lines = []
    for page in result.pages:
        for line in page.lines:
            content = line.content.strip().upper()
            lines.append(content)
    
    # 2. Buang baris-baris yang bukan berarti nomor soal atau pilihan
    filtered_lines = []
    for line in lines:
        # Simpan hanya baris yang berisi pilihan jawaban atau nomor soal
        if line in ["A", "B", "C", "D"] or line.isdigit() or (len(line) > 1 and line[0].isdigit() and line[1] == "."):
            # Jika format "1." atau "1)", ambil hanya angkanya
            if len(line) > 1 and line[0].isdigit():
                if line[1] == "." or line[1] == ")":
                    line = line[0]
            filtered_lines.append(line)
    
    print(f"Total baris setelah filtering: {len(filtered_lines)}")
    
    # 3. Kelompokkan setiap 4 baris jadi satu blok
    # Cari pola nomor soal diikuti oleh 3 pilihan (yang muncul)
    i = 0
    while i < len(filtered_lines):
        # Cek apakah baris saat ini adalah nomor soal
        if filtered_lines[i].isdigit():
            nomor_soal = int(filtered_lines[i])
            
            # Pastikan nomor soal valid (1-40)
            if 1 <= nomor_soal <= 40:
                # Kumpulkan pilihan yang muncul (maksimal 3 pilihan)
                pilihan_muncul = set()
                j = i + 1
                while j < len(filtered_lines) and j < i + 4 and not filtered_lines[j].isdigit():
                    if filtered_lines[j] in ["A", "B", "C", "D"]:
                        pilihan_muncul.add(filtered_lines[j])
                    j += 1
                
                # 4. Hitung himpunan penuh {'A','B','C','D'}, lalu cari elemen yang hilang
                if len(pilihan_muncul) > 0:
                    pilihan_tidak_muncul = pilihan_lengkap - pilihan_muncul
                    
                    # Jika hanya ada satu pilihan yang tidak muncul, itu adalah jawaban siswa
                    if len(pilihan_tidak_muncul) == 1:
                        jawaban = list(pilihan_tidak_muncul)[0]
                        jawaban_siswa[nomor_soal-1] = jawaban
                        print(f"Soal {nomor_soal}: Pilihan yang muncul {pilihan_muncul}, jawaban siswa adalah {jawaban}")
                    else:
                        print(f"Soal {nomor_soal}: Tidak dapat menentukan jawaban dengan pasti. Pilihan yang muncul: {pilihan_muncul}")
                
                # Lompat ke nomor soal berikutnya
                i = j
            else:
                i += 1
        else:
            i += 1
    
    # Jika metode di atas tidak berhasil mendeteksi banyak jawaban, coba pendekatan alternatif
    # dengan menggunakan tabel
    if jawaban_siswa.count("-") > 30:  # Jika lebih dari 30 soal belum terdeteksi
        print("\nMencoba pendekatan alternatif dengan analisis tabel...")
        
        # Ekstrak teks dari semua sel dalam tabel jawaban
        for table in result.tables:
            # Identifikasi struktur tabel jawaban
            # Asumsikan setiap 4 baris berurutan mewakili pilihan A, B, C, D untuk satu soal
            for cell in table.cells:
                content = cell.content.strip().upper()
                row_idx = cell.row_index
                col_idx = cell.column_index
                
                # Jika sel berisi pilihan jawaban (A, B, C, D)
                if content in ["A", "B", "C", "D"]:
                    # Tentukan nomor soal berdasarkan posisi sel
                    # Asumsikan struktur: setiap 4 baris berisi 1 soal, dan ada beberapa soal per kolom
                    nomor_soal = (row_idx // 4) * table.column_count + col_idx + 1
                    
                    # Pastikan nomor soal valid (1-40)
                    if 1 <= nomor_soal <= 40:
                        # Jika jawaban untuk soal ini belum terdeteksi
                        if jawaban_siswa[nomor_soal-1] == "-":
                            # Kumpulkan semua pilihan yang muncul untuk soal ini
                            pilihan_muncul = set()
                            for r in range(row_idx // 4 * 4, (row_idx // 4 + 1) * 4):
                                for c in range(table.column_count):
                                    for cell2 in table.cells:
                                        if cell2.row_index == r and cell2.column_index == c:
                                            content2 = cell2.content.strip().upper()
                                            if content2 in ["A", "B", "C", "D"]:
                                                pilihan_muncul.add(content2)
                            
                            # Cari pilihan yang tidak muncul
                            pilihan_tidak_muncul = pilihan_lengkap - pilihan_muncul
                            
                            # Jika hanya ada satu pilihan yang tidak muncul, itu adalah jawaban siswa
                            if len(pilihan_tidak_muncul) == 1:
                                jawaban = list(pilihan_tidak_muncul)[0]
                                jawaban_siswa[nomor_soal-1] = jawaban
                                print(f"Soal {nomor_soal}: Pilihan yang muncul {pilihan_muncul}, jawaban siswa adalah {jawaban}")
    
    return jawaban_siswa