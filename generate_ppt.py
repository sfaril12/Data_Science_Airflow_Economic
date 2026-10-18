import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # -------------------------------------------------------------------------
    # PALET WARNA ESTETIK - "MIDNIGHT CYBER-EXECUTIVE"
    # -------------------------------------------------------------------------
    BG_COLOR = RGBColor(8, 13, 26)           # Deep Midnight Obsidian (#080D1A)
    CARD_BG = RGBColor(16, 25, 45)           # Elevated Card Surface (#10192D)
    CARD_BORDER = RGBColor(31, 46, 77)       # Subtle Border Stroke (#1F2E4D)
    CARD_BORDER_GLOW = RGBColor(56, 189, 248)# Glowing Accent Border
    
    TEAL_CYAN = RGBColor(0, 229, 255)        # Electric Cyan (#00E5FF)
    SKY_BLUE = RGBColor(56, 189, 248)        # Sky Blue (#38BDF8)
    EMERALD_GREEN = RGBColor(16, 185, 129)   # Vibrant Emerald (#10B981)
    AMBER_GOLD = RGBColor(245, 158, 11)      # Warm Amber (#F59E0B)
    ROSE_CORAL = RGBColor(244, 63, 94)       # Radiant Coral (#F43F5E)
    PURPLE_ACCENT = RGBColor(168, 85, 247)   # Neon Purple (#A855F7)
    
    TEXT_WHITE = RGBColor(248, 250, 252)     # Soft Platinum White (#F8FAFC)
    TEXT_MUTED = RGBColor(148, 163, 184)     # Slate Gray (#94A3B8)
    TEXT_SUBTLE = RGBColor(100, 116, 139)    # Muted Gray

    CHARTS_DIR = "dashboard/charts"
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, category_num=""):
        # Decorative top accent pill
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = f"✦  {category_num}  |  {tag_text}".upper() if category_num else f"✦  {tag_text}".upper()
        p_tag.font.name = "Arial"
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = TEAL_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.75))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, subtitle=None, border_color=CARD_BORDER, fill_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = "Arial"
            p_sub.font.size = Pt(9.5)
            p_sub.font.color.rgb = SKY_BLUE
            p_sub.space_after = Pt(6)

        return tf

    def add_chart_image(slide, image_filename, left, top, width, height, title_label=None, accent_color=SKY_BLUE):
        img_path = os.path.join(CHARTS_DIR, image_filename)
        # Card container for graphic
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        if title_label:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.08), width - Inches(0.4), Inches(0.32))
            tf = tb.text_frame
            p = tf.paragraphs[0]
            p.text = title_label
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = accent_color

        if os.path.exists(img_path):
            img_top = top + Inches(0.38) if title_label else top + Inches(0.12)
            img_height = height - Inches(0.50) if title_label else height - Inches(0.24)
            slide.shapes.add_picture(img_path, left + Inches(0.12), img_top, width - Inches(0.24), img_height)

    # =========================================================================
    # SLIDE 1: COVER SLIDE (ESTETIK HERO)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Vertical glowing accent line
    bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.2))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL_CYAN
    bar.line.fill.background()

    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11.2), Inches(3.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "END-TO-END DATA SCIENCE & MACHINE LEARNING PIPELINE"
    p_badge.font.name = "Arial"
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = TEAL_CYAN
    p_badge.space_after = Pt(8)

    p_main = tf1.add_paragraph()
    p_main.text = "Southeast Asia Economic Intelligence"
    p_main.font.name = "Arial"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_WHITE

    p_sub = tf1.add_paragraph()
    p_sub.text = "Pipeline Analisis Lengkap: Data Gathering, Assessing, Cleaning, EDA (Heatmap), Pemodelan ML, & Visualisasi Streamlit"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(8)

    # 3 Pill Cards at bottom
    tf_f1 = add_card(s1, Inches(1.2), Inches(5.4), Inches(3.5), Inches(1.3), "Arsitektur ETL & DB", "Apache Airflow & MySQL 8.0")
    p1 = tf_f1.add_paragraph()
    p1.text = "Orkestrasi DAG & integrasi relasional 3 indikator"
    p1.font.size = Pt(9.5)
    p1.font.color.rgb = TEXT_MUTED

    tf_f2 = add_card(s1, Inches(5.0), Inches(5.4), Inches(3.5), Inches(1.3), "Pipeline Engine", "process.py (Data Science Core)")
    p2 = tf_f2.add_paragraph()
    p2.text = "6 tahapan modular, fail-safe & reproducible"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    tf_f3 = add_card(s1, Inches(8.8), Inches(5.4), Inches(3.5), Inches(1.3), "Interactive Dashboard", "Streamlit & Plotly (5 Visual)")
    p3 = tf_f3.add_paragraph()
    p3.text = "Visualisasi analitik real-time & evaluasi model"
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 2: LATAR BELAKANG & URGENSI KASUS (MENGAPA MEMILIH KASUS INI?)
    # =========================================================================
    s_bg = prs.slides.add_slide(blank_layout)
    set_slide_background(s_bg)
    add_header(s_bg, "Latar Belakang Proyek", "Urgensi Analisis & Pemodelan Ekonomi Kawasan ASEAN", "LATAR BELAKANG")

    # 3 Pillar Containers
    tf_bg1 = add_card(s_bg, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.3), "1. Dinamika & Disparitas ASEAN", "Episentrum Pertumbuhan Global", border_color=SKY_BLUE)
    bg1_points = [
        ("Pertumbuhan Pesat Regional", "Kawasan ASEAN (khususnya 6 negara utama: Indonesia, Malaysia, Singapura, Thailand, Filipina, Vietnam) merupakan salah satu motor penggerak ekonomi tercepat di dunia dalam dua dekade terakhir."),
        ("Disparitas Karakteristik", "Terdapat variasi struktural yang sangat tajam: Indonesia memimpin skala pasar domestik raksasa (> 275 juta jiwa), Singapura mendominasi nilai tambah per kapita dan jasa finansial, sedangkan Vietnam & Thailand menjadi hub manufaktur rantai pasok global."),
        ("Kebutuhan Komparasi Holistik", "Diperlukan analisis terintegrasi untuk melihat bagaimana populasi dan pasar tenaga kerja (pengangguran) saling mempengaruhi skala output ekonomi nasional.")
    ]
    for lbl, desc in bg1_points:
        p = tf_bg1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_bg1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    tf_bg2 = add_card(s_bg, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.3), "2. Kebutuhan Otomasi ETL", "Modernisasi Data Engineering", border_color=AMBER_GOLD)
    bg2_points = [
        ("Kelemahan Analisis Manual", "Pengambilan data makroekonomi secara konvensional (download manual file spreadsheet World Bank) lambat, terfragmentasi, dan rentan terhadap inkonsistensi format."),
        ("Orkestrasi Apache Airflow", "Proyek ini membuktikan implementasi data pipeline modern: Apache Airflow secara otomatis menjadwalkan penarikan data berkala tanpa intervensi manusia (hands-off operation)."),
        ("Tata Kelola MySQL Terpusat", "Data dinormalisasi ke dalam skema basis data relasional (tabel gdp, population, unemployment), menjamin integritas data historis."),
        ("Resiliensi Arsitektur", "Membangun sistem dengan fallback otomatis langsung ke API resmi jika koneksi database mengalami gangguan.")
    ]
    for lbl, desc in bg2_points:
        p = tf_bg2.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = AMBER_GOLD
        p_sub = tf_bg2.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    tf_bg3 = add_card(s_bg, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.3), "3. Proyeksi ML Bebas Bias", "Sains Data & Decision Support", border_color=EMERALD_GREEN)
    bg3_points = [
        ("Keterbatasan Model Klasik", "Analisis regresi konvensional sering gagal menangkap pola non-linear dan korelasi silang multivariat antar negara berkembang."),
        ("Mencegah Data Leakage", "Data ekonomi deret waktu memiliki tantangan kausalitas temporal. Kasus ini menerapkan validasi berbasis waktu (Time-Based Split) untuk menjamin pengujian realistis."),
        ("Prediksi Berakurasi Tinggi", "Random Forest Regressor berhasil mencapai akurasi R² = 92.7% dalam memproyeksikan GDP out-of-time."),
        ("Dukungan Keputusan Nyata", "Hasil pipeline divisualisasikan interaktif melalui Streamlit untuk membantu analis dan pengambil kebijakan merumuskan strategi ekonomi berbasis bukti.")
    ]
    for lbl, desc in bg3_points:
        p = tf_bg3.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = EMERALD_GREEN
        p_sub = tf_bg3.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    # =========================================================================
    # SLIDE 3: RUMUSAN MASALAH / PERTANYAAN PENELITIAN
    # =========================================================================
    s_rq = prs.slides.add_slide(blank_layout)
    set_slide_background(s_rq)
    add_header(s_rq, "Rumusan Masalah", "Pertanyaan Penelitian & Metode Analisis", "RESEARCH QUESTIONS")

    questions = [
        {
            "no": "1",
            "question": "Bagaimana perkembangan GDP dari waktu ke waktu?",
            "method": "Analisis Tren + Line Chart",
            "answer": "GDP keenam negara ASEAN menunjukkan tren pertumbuhan eksponensial yang konsisten sejak awal tahun 2000-an. Indonesia memimpin dengan GDP nominal melampaui $1.3 Triliun USD, diikuti Thailand dan Singapura. Terdapat kontraksi sementara pada krisis 1997–1998 dan pandemi 2020 yang segera pulih (V-shaped recovery).",
            "color": SKY_BLUE
        },
        {
            "no": "2",
            "question": "Bagaimana hubungan Population dengan GDP?",
            "method": "Pearson Correlation + Scatter Plot",
            "answer": "Korelasi Pearson antara populasi dan GDP bernilai +0.605 (korelasi positif kuat). Negara dengan jumlah penduduk lebih besar cenderung memiliki output ekonomi lebih tinggi karena skala pasar domestik dan kapasitas tenaga kerja yang lebih luas.",
            "color": EMERALD_GREEN
        },
        {
            "no": "3",
            "question": "Bagaimana hubungan Unemployment dengan GDP?",
            "method": "Pearson Correlation + Scatter Plot",
            "answer": "Korelasi Pearson antara tingkat pengangguran dan GDP bernilai +0.118 (korelasi lemah/non-linear). Hal ini disebabkan oleh dominannya sektor informal di negara-negara berkembang ASEAN, sehingga perubahan angka pengangguran terbuka tidak selalu mencerminkan perubahan output ekonomi secara langsung.",
            "color": AMBER_GOLD
        },
        {
            "no": "4",
            "question": "Dapatkah Random Forest memprediksi GDP berdasarkan indikator ekonomi?",
            "method": "Random Forest + MAE, RMSE, R²",
            "answer": "Ya. Model Random Forest Regressor berhasil mencapai skor R² = 0.927 (akurasi 92.7%) dengan MAE = $75.59 Miliar dan RMSE = $118.42 Miliar. Pendekatan Time-Based Split menjamin evaluasi realistis tanpa data leakage, membuktikan bahwa kombinasi populasi, tahun, pengangguran, dan identitas negara sudah cukup informatif untuk memproyeksikan skala GDP.",
            "color": ROSE_CORAL
        }
    ]

    for idx, q in enumerate(questions):
        row = idx // 2
        col = idx % 2
        c_left = Inches(0.8 + col * 6.0)
        c_top = Inches(1.6 + row * 2.8)
        c_width = Inches(5.7)
        c_height = Inches(2.55)

        tf_q = add_card(s_rq, c_left, c_top, c_width, c_height,
                        f"Pertanyaan {q['no']}: {q['question']}",
                        f"Metode: {q['method']}",
                        border_color=q["color"])

        p_ans_label = tf_q.add_paragraph()
        p_ans_label.text = "Jawaban:"
        p_ans_label.font.size = Pt(10)
        p_ans_label.font.bold = True
        p_ans_label.font.color.rgb = q["color"]
        p_ans_label.space_before = Pt(4)

        p_ans = tf_q.add_paragraph()
        p_ans.text = q["answer"]
        p_ans.font.size = Pt(9.5)
        p_ans.font.color.rgb = TEXT_MUTED
        p_ans.space_after = Pt(4)

    # =========================================================================
    # SLIDE 4: OVERVIEW WORKFLOW 6 TAHAP
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Workflow Pipeline", "Alur Kerja End-to-End Analisis Data Ekonomi", "OVERVIEW")

    stages = [
        ("1. Data Gathering", "Ekstraksi multi-negara dari MySQL & World Bank API.", TEAL_CYAN),
        ("2. Data Assessing", "Audit kualitas, missing values, duplikasi & integritas.", AMBER_GOLD),
        ("3. Data Cleaning", "Imputasi deret waktu linear per negara & mapping ISO3.", EMERALD_GREEN),
        ("4. EDA & Heatmap", "Analisis statistik deskriptif & matriks korelasi Pearson.", SKY_BLUE),
        ("5. Pemodelan", "Random Forest Regressor dengan Time-Based Validation.", ROSE_CORAL),
        ("6. Kesimpulan", "Sintesis temuan analitis otomatis & rekomendasi nyata.", EMERALD_GREEN),
    ]

    for idx, (st_title, st_desc, col) in enumerate(stages):
        row = idx // 3
        c_idx = idx % 3
        tf_st = add_card(s2, Inches(0.8 + c_idx * 4.0), Inches(1.6 + row * 2.6), Inches(3.7), Inches(2.3), st_title, "Tahapan Komputasi Terstruktur", border_color=col)
        p = tf_st.add_paragraph()
        p.text = st_desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)
        p_info = tf_st.add_paragraph()
        p_info.text = "Engine: process.py  •  Output: Siap Visualisasi"
        p_info.font.size = Pt(9)
        p_info.font.color.rgb = col


    # =========================================================================
    # SLIDE 3: TAHAP 1 - DATA GATHERING (DENGAN VISUAL INGESTI)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Tahap 1", "Data Gathering: Penarikan Data dari Database & API", "TAHAP 01")

    # Left: Explanation
    tf_g1 = add_card(s3, Inches(0.8), Inches(1.6), Inches(4.7), Inches(5.3), "Arsitektur Penarikan Data", "MySQL & API Fallback")
    items_g1 = [
        ("Koneksi Database Utama", "MySQL port 3308 & 3306 (user root), database `economic_db`."),
        ("Dukungan Schema SQL", "Mendukung tabel tunggal `economic_combined` maupun query SQL JOIN relasional antar tabel: `gdp`, `population`, dan `unemployment`."),
        ("Dukungan AllowNoPassword", "Adaptif mencoba password 'root' dan password kosong ('')."),
        ("Fallback World Bank API", "Menarik 3 indikator (GDP, Populasi, Pengangguran) untuk 6 negara ASEAN secara otomatis jika database belum aktif.")
    ]
    for lbl, desc in items_g1:
        p = tf_g1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEAL_CYAN
        p_sub = tf_g1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    # Right: Chart Gathering
    add_chart_image(s3, "diagram_gathering_ingestion.png", Inches(5.8), Inches(1.6), Inches(6.7), Inches(5.3), "📦 VISUALISASI INGESTI DATA: VOLUME OBSERVASI PER NEGARA", TEAL_CYAN)


    # =========================================================================
    # SLIDE: DOKUMENTASI ORKESTRASI APACHE AIRFLOW
    # =========================================================================
    s_air = prs.slides.add_slide(blank_layout)
    set_slide_background(s_air)
    add_header(s_air, "Dokumentasi Orkestrasi", "Monitoring & Eksekusi Pipeline pada Apache Airflow Web UI", "APACHE AIRFLOW")

    # Left: Main visual screenshot container (prominent display, preserving aspect ratio)
    c_img_left = Inches(0.8)
    c_img_top = Inches(1.55)
    c_img_w = Inches(8.5)
    c_img_h = Inches(5.35)

    card_air = s_air.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_img_left, c_img_top, c_img_w, c_img_h)
    card_air.fill.solid()
    card_air.fill.fore_color.rgb = CARD_BG
    card_air.line.color.rgb = TEAL_CYAN
    card_air.line.width = Pt(1.2)

    # Title label inside card
    tb_air_lbl = s_air.shapes.add_textbox(c_img_left + Inches(0.25), c_img_top + Inches(0.12), c_img_w - Inches(0.5), Inches(0.35))
    p_air_lbl = tb_air_lbl.text_frame.paragraphs[0]
    p_air_lbl.text = "⚡ APACHE AIRFLOW WEB CONSOLE • MONITORING EKSEKUSI DAG & TASK DURATION"
    p_air_lbl.font.name = "Arial"
    p_air_lbl.font.size = Pt(10)
    p_air_lbl.font.bold = True
    p_air_lbl.font.color.rgb = TEAL_CYAN

    # Picture with true aspect ratio (736x388)
    img_air_path = os.path.join(CHARTS_DIR, "airflow_documentation.png")
    if os.path.exists(img_air_path):
        p_w = Inches(8.0)
        p_h = Inches(8.0 / (736.0 / 388.0))
        p_top = c_img_top + Inches(0.52)
        p_left = c_img_left + Inches(0.25)
        s_air.shapes.add_picture(img_air_path, p_left, p_top, p_w, p_h)

    # Status pill bottom badge inside card
    tb_badge = s_air.shapes.add_textbox(c_img_left + Inches(0.25), c_img_top + Inches(4.85), c_img_w - Inches(0.5), Inches(0.35))
    p_b = tb_badge.text_frame.paragraphs[0]
    p_b.text = "Status: Web UI Connected  •  Time Range: Last 24 Hours  •  Metrics: Last 9 DAG Runs & Task Logs"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(9)
    p_b.font.color.rgb = TEXT_MUTED

    # Right: Operational documentation card
    tf_air = add_card(s_air, Inches(9.5), Inches(1.55), Inches(3.0), Inches(5.35), "Observabilitas Pipeline", "Catatan Eksekusi DAG Airflow", border_color=SKY_BLUE)

    air_points = [
        ("Penjadwalan Otomatis", "DAG dijadwalkan secara periodik untuk mengeksekusi penarikan data ekonomi dari MySQL dan API World Bank secara konsisten."),
        ("Monitoring Durasi Run", "Panel Last 9 DAG Runs memvisualisasikan Queued vs Run Duration untuk evaluasi latensi komputasi tiap interval penarikan."),
        ("Inspeksi Status Task", "Indikator Failed Task & Failed Run mendeteksi anomali kegagalan task secara cepat untuk mitigasi proaktif."),
        ("Akses Log Terintegrasi", "Fitur Recent Failed Task Logs memfasilitasi penelusuran akar masalah (debugging) tanpa perlu membuka server backend manual.")
    ]
    for lbl, desc in air_points:
        p = tf_air.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_air.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)


    # =========================================================================
    # SLIDE 4: TAHAP 2 - DATA ASSESSING (DENGAN VISUAL AUDIT MISSING VALUE)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Tahap 2", "Data Assessing: Audit Integritas & Nilai Hilang", "TAHAP 02")

    # Left: Explanation
    tf_a1 = add_card(s4, Inches(0.8), Inches(1.6), Inches(4.7), Inches(5.3), "Audit Kualitas Dataset", "Diagnosis Masalah Data Raw", border_color=AMBER_GOLD)
    a_items = [
        ("Audit Missing Values", "Data historis indikator pengangguran memiliki kekosongan signifikan pada era 1960–1990 karena sistem pelaporan statistik belum seragam."),
        ("Verifikasi Duplikasi Kunci", "Audit kunci komposit `(country_code, year)` untuk memastikan tidak ada redundansi observasi ganda."),
        ("Validasi Tipe & Range Data", "Memastikan tipe numerik valid (GDP & pengangguran sebagai float, year sebagai int) dan mendeteksi anomali nilai negatif.")
    ]
    for lbl, desc in a_items:
        p = tf_a1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = AMBER_GOLD
        p_sub = tf_a1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(6)

    # Right: Chart Assessing Missing
    add_chart_image(s4, "diagram_assessing_missing.png", Inches(5.8), Inches(1.6), Inches(6.7), Inches(5.3), "🔍 AUDIT KELENGKAPAN: PERSENTASE VALID VS MISSING VALUES", AMBER_GOLD)


    # =========================================================================
    # SLIDE 5: TAHAP 3 - DATA CLEANING (DENGAN VISUAL BEFORE VS AFTER)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Tahap 3", "Data Cleaning: Sanitasi & Imputasi Deret Waktu", "TAHAP 03")

    # Left: Explanation
    tf_c1 = add_card(s5, Inches(0.8), Inches(1.6), Inches(4.7), Inches(5.3), "Metodologi Pembersihan Data", "Imputasi Berbasis Time-Series", border_color=EMERALD_GREEN)
    c_items = [
        ("Bahaya DropNA Sembarangan", "Menghapus baris kosong secara langsung akan memotong kesinambungan data deret waktu dan merusak tren historis."),
        ("Interpolasi Linear per Negara", "Nilai hilang diimputasi secara mulus menggunakan linear interpolation khusus per kelompok negara untuk menjaga karakteristik lokal."),
        ("Boundary Fill (ffill/bfill)", "Ujung awal dan akhir deret diisi dengan forward/backward fill untuk stabilitas tanpa menimbulkan distorsi outlier."),
        ("Mapping ISO3 & Standardisasi", "Menambahkan nama resmi negara dan mengurutkan secara kronologis (country_code, year).")
    ]
    for lbl, desc in c_items:
        p = tf_c1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = EMERALD_GREEN
        p_sub = tf_c1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    # Right: Chart Cleaning Before vs After
    add_chart_image(s5, "diagram_cleaning_imputation.png", Inches(5.8), Inches(1.6), Inches(6.7), Inches(5.3), "✨ VISUALISASI IMPUTASI: SEBELUM VS SESUDAH CLEANING", EMERALD_GREEN)


    # =========================================================================
    # SLIDE 6: TAHAP 4 - EDA (HEATMAP KORELASI PEARSON ESTETIK)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Tahap 4 • EDA (Heatmap)", "Matriks Korelasi Pearson Antar Variabel Makroekonomi", "TAHAP 04")

    # Left: Chart Heatmap
    add_chart_image(s6, "diagram_eda_heatmap.png", Inches(0.8), Inches(1.6), Inches(6.7), Inches(5.3), "🔥 HEATMAP KORELASI PEARSON (GDP, POPULASI, PENGANGGURAN, TAHUN)", PURPLE_ACCENT)

    # Right: Insight Explanation
    tf_h_desc = add_card(s6, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.3), "Interpretasi Matriks Korelasi", "Analisis Hubungan Antar Indikator", border_color=PURPLE_ACCENT)
    h_items = [
        ("Populasi vs GDP (+0.605)", "Korelasi positif kuat. Skala jumlah penduduk berkontribusi langsung pada ukuran output ekonomi dan pasar domestik negara ASEAN."),
        ("Tahun vs GDP (+0.548)", "Pertumbuhan ekonomi kumulatif jangka panjang konsisten meningkat tajam seiring modernisasi teknologi dan perdagangan."),
        ("Pengangguran vs GDP (+0.118)", "Korelasi lemah/non-linear menunjukkan bahwa di negara berkembang, sebagian besar tenaga kerja terserap di sektor informal saat sektor formal menurun."),
        ("Implikasi Pemodelan ML", "Populasi dan tren tahunan menjadi fitur paling informatif dalam memproyeksikan skala GDP.")
    ]
    for lbl, desc in h_items:
        p = tf_h_desc.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_h_desc.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)


    # =========================================================================
    # SLIDE 7: TAHAP 4 - EDA (DIAGRAM 1: TREN PERTUMBUHAN GDP HISTORIS)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Tahap 4 • EDA (Diagram 1)", "Tren Pertumbuhan GDP Negara dari Tahun ke Tahun", "TAHAP 04")

    # Left: Explanation card
    tf_e1 = add_card(s7, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3), "Dinamika Trajektori Historis", "Visualisasi Multi-Line Plot")
    e1_points = [
        ("Lonjakan Pasca-2000", "GDP kawasan mengalami akselerasi eksponensial sejak awal tahun 2000-an didorong oleh integrasi rantai pasok global dan manufaktur regional."),
        ("Resiliensi Krisis Finansial", "Terlihat guncangan tajam saat krisis 1997–1998 dan pandemi 2020 yang cepat mengalami pemulihan berbentuk V-shaped recovery."),
        ("Skala Ekonomi Terbesar", "Indonesia menduduki posisi GDP nominal tertinggi di ASEAN (> $1.37 Triliun USD), diikuti oleh Thailand, Singapura, dan Malaysia.")
    ]
    for lbl, desc in e1_points:
        p = tf_e1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_e1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(6)

    # Right: Chart Image 1
    add_chart_image(s7, "diagram_1_gdp_trend.png", Inches(5.6), Inches(1.6), Inches(6.9), Inches(5.3), "📈 DIAGRAM 1: LINE CHART TREN GDP PER NEGARA (USD)", SKY_BLUE)


    # =========================================================================
    # SLIDE 8: TAHAP 4 - EDA (DIAGRAM 2 & 3: POPULASI & PENGANGGURAN)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Tahap 4 • EDA (Diagram 2 & 3)", "Analisis Hubungan: Populasi & Pengangguran vs GDP", "TAHAP 04")

    # Left: Diagram 2 (Populasi vs GDP)
    add_chart_image(s8, "diagram_2_pop_vs_gdp.png", Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.2), "👥 DIAGRAM 2: SCATTER PLOT POPULASI VS GDP", SKY_BLUE)
    tf_c_pop = add_card(s8, Inches(0.8), Inches(5.95), Inches(5.7), Inches(0.95), "Insight Populasi (r = +0.605)")
    p = tf_c_pop.add_paragraph()
    p.text = "Korelasi positif membuktikan ukuran populasi memperluas pasar domestik dan output ekonomi total."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MUTED

    # Right: Diagram 3 (Pengangguran vs GDP)
    add_chart_image(s8, "diagram_3_unemp_vs_gdp.png", Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2), "📉 DIAGRAM 3: BUBBLE PLOT PENGANGGURAN VS GDP (UKURAN: POPULASI)", AMBER_GOLD)
    tf_c_unemp = add_card(s8, Inches(6.8), Inches(5.95), Inches(5.7), Inches(0.95), "Insight Pengangguran (r = +0.118)")
    p = tf_c_unemp.add_paragraph()
    p.text = "Sektor informal yang dominan membuat fluktuasi pengangguran tidak selalu berbanding lurus dengan GDP."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 9: TAHAP 4 - EDA (DIAGRAM 4: KOMPARASI RATA-RATA GDP ASEAN)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Tahap 4 • EDA (Diagram 4)", "Perbandingan Rata-rata GDP Antar Negara di ASEAN", "TAHAP 04")

    # Left: Chart Image 4
    add_chart_image(s9, "diagram_4_gdp_comparison.png", Inches(0.8), Inches(1.6), Inches(6.9), Inches(5.3), "📊 DIAGRAM 4: BAR CHART KOMPARASI RATA-RATA GDP (TRILIUN USD)", EMERALD_GREEN)

    # Right: Analytical Breakdown
    tf_e4 = add_card(s9, Inches(8.0), Inches(1.6), Inches(4.5), Inches(5.3), "Struktur Perekonomian Regional", "Disparitas & Produktivitas")
    e4_points = [
        ("Disparitas Kapasitas Output", "Terdapat selisih skala output yang lebar antara negara berpopulasi besar (Indonesia) dengan basis populasi menengah."),
        ("Produktivitas per Kapita", "Meskipun total GDP Indonesia paling masif, Singapura mencatatkan nilai tambah per kapita tertinggi di kawasan berkat hub finansial dan logistik dunia."),
        ("Konsistensi Industri Vietnam", "Vietnam memperlihatkan laju ekspansi manufaktur paling konsisten dalam dua dekade terakhir.")
    ]
    for lbl, desc in e4_points:
        p = tf_e4.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = EMERALD_GREEN
        p_sub = tf_e4.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(6)


    # =========================================================================
    # SLIDE 10: TAHAP 5 - PEMODELAN MACHINE LEARNING
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Tahap 5", "Pemodelan Machine Learning: Random Forest Regressor", "TAHAP 05")

    tf_m1 = add_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3), "Konfigurasi Algoritma & Fitur", "Arsitektur Ensemble Regression")
    m1_points = [
        ("Algoritma Terpilih", "Random Forest Regressor (300 estimator pohon, random_state=42, n_jobs=-1)."),
        ("Target Prediksi (y)", "GDP nominal tahunan dalam USD."),
        ("Fitur Prediktor (X)", "Tahun (tren waktu), Populasi (skala demografi), Tingkat Pengangguran (pasar tenaga kerja)."),
        ("One-Hot Encoding", "Kategori kode negara (`country_code`) diubah menjadi variabel dummy biner untuk membedakan karakteristik bawaan negara."),
        ("Ketahanan Non-Linear", "Mampu menangkap interaksi kompleks tanpa resiko overfitting berlebih.")
    ]
    for lbl, desc in m1_points:
        p = tf_m1.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_m1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)

    tf_m2 = add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Validasi Out-of-Time", "Mencegah Data Leakage Deret Waktu")
    m2_points = [
        ("Bahaya Random K-Fold Split", "Pemisahan acak pada data deret waktu akan menyebabkan data masa depan bocor ke masa lalu, menghasilkan akurasi palsu."),
        ("Time-Based Split Approach", "Dataset dibagi secara temporal: data historis awal dialokasikan sebagai Training Set, sedangkan 3 tahun terakhir dialokasikan murni sebagai Testing Set."),
        ("Simulasi Kondisi Riil", "Pendekatan ini menguji kemampuan model untuk memproyeksikan GDP pada periode masa depan yang belum pernah dilihat sebelumnya secara realistis.")
    ]
    for lbl, desc in m2_points:
        p = tf_m2.add_paragraph()
        p.text = f"• {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = ROSE_CORAL
        p_sub = tf_m2.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(4)


    # =========================================================================
    # SLIDE 11: TAHAP 5 - EVALUASI MODEL (DIAGRAM 5 & 6)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Tahap 5 • Evaluasi (Diagram 5 & 6)", "Kinerja Model: Aktual vs Prediksi & Feature Importance", "EVALUASI")

    # Left: Diagram 5 (Actual vs Predicted)
    add_chart_image(s11, "diagram_5_model_actual_vs_pred.png", Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.0), "🎯 DIAGRAM 5: AKTUAL VS PREDIKSI GDP (GARIS PUTUS-PUTUS = IDEAL)", ROSE_CORAL)
    
    # Left Bottom: Metric Cards
    tf_ev1 = add_card(s11, Inches(0.8), Inches(5.75), Inches(1.8), Inches(1.15), "R² Score", "0.927", border_color=EMERALD_GREEN)
    p = tf_ev1.add_paragraph()
    p.text = "Akurasi 92.7%"
    p.font.size = Pt(9)
    p.font.color.rgb = TEXT_MUTED

    tf_ev2 = add_card(s11, Inches(2.75), Inches(5.75), Inches(1.8), Inches(1.15), "MAE", "$75.59 B", border_color=SKY_BLUE)
    p = tf_ev2.add_paragraph()
    p.text = "Mean Absolute Err"
    p.font.size = Pt(9)
    p.font.color.rgb = TEXT_MUTED

    tf_ev3 = add_card(s11, Inches(4.7), Inches(5.75), Inches(1.8), Inches(1.15), "RMSE", "$118.42 B", border_color=AMBER_GOLD)
    p = tf_ev3.add_paragraph()
    p.text = "Root Mean Squared"
    p.font.size = Pt(9)
    p.font.color.rgb = TEXT_MUTED

    # Right: Diagram 6 (Feature Importance)
    add_chart_image(s11, "diagram_6_feature_importance.png", Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.0), "⭐ FEATURE IMPORTANCE (KONTRIBUSI PREDIKTOR UTAMA)", SKY_BLUE)
    
    tf_feat_desc = add_card(s11, Inches(6.8), Inches(5.75), Inches(5.7), Inches(1.15), "Interpretasi Prediktor Utama")
    p = tf_feat_desc.add_paragraph()
    p.text = "Populasi (~48%) dan Tahun (~24%) mendominasi proyeksi GDP nominal, disusul oleh efek spesifik negara (~18%) dan tingkat pengangguran (~10%)."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 12: ANTARMUKA DASHBOARD STREAMLIT (app.py)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Antarmuka Dashboard", "Implementasi 5 Visual Diagram pada Streamlit (app.py)", "DASHBOARD")

    dash_features = [
        ("Diagram 1 (Multi-Line)", "Perkembangan Tren GDP Historis", "Memetakan pertumbuhan tahunan antar negara dengan hover tooltip interaktif."),
        ("Diagram 2 (Scatter Plot)", "Korelasi Populasi vs GDP", "Menampilkan sebaran hubungan positif linear antara jumlah penduduk dan output."),
        ("Diagram 3 (Bubble Chart)", "Tingkat Pengangguran vs GDP", "Visualisasi multivariat dengan ukuran bubble proporsional terhadap populasi."),
        ("Diagram 4 (Bar Chart)", "Komparasi Rata-rata GDP ASEAN", "Perbandingan skala rata-rata ekonomi triliun USD yang terurut secara informatif."),
        ("Diagram 5 (Scatter Evaluasi)", "Uji Aktual vs Prediksi Model", "Evaluasi out-of-time model Random Forest terhadap garis referensi diagonal ideal.")
    ]

    for idx, (d_title, d_sub, d_desc) in enumerate(dash_features):
        c_left = Inches(0.8 + (idx % 3) * 4.0) if idx < 3 else Inches(1.8 + (idx - 3) * 5.0)
        c_top = Inches(1.6) if idx < 3 else Inches(4.4)
        c_width = Inches(3.7) if idx < 3 else Inches(4.7)
        c_height = Inches(2.4)

        tf_d = add_card(s12, c_left, c_top, c_width, c_height, d_title, d_sub, border_color=SKY_BLUE)
        p = tf_d.add_paragraph()
        p.text = d_desc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)
        p_sub = tf_d.add_paragraph()
        p_sub.text = "Engine: Plotly Interactive • Cached: @st.cache_data"
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = EMERALD_GREEN


    # =========================================================================
    # SLIDE 13: TAHAP 6 - KESIMPULAN & REKOMENDASI STRATEGIS
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Tahap 6", "Kesimpulan Analitis & Rekomendasi Strategis", "TAHAP 06")

    tf_con1 = add_card(s13, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3), "Temuan Kunci Sains Data", "Kesimpulan Analitik Pipeline", border_color=EMERALD_GREEN)
    c_finds = [
        ("Integritas Data Pipeline", "Pipeline berhasil menyatukan data Airflow/MySQL dan API dengan teknik sanitasi deret waktu tanpa distorsi."),
        ("Skala Demografi Menentukan Output", "Korelasi kuat antara populasi dan GDP membuktikan pasar domestik yang besar di kawasan adalah motor penggerak utama pertumbuhan."),
        ("Akurasi Model Sangat Tinggi", "Skor R² sebesar 92.7% membuktikan Random Forest andal dalam memproyeksikan skala makroekonomi jangka panjang."),
        ("Arsitektur Decoupled Teruji", "Pemisahan process.py dan app.py menghasilkan kode yang bersih, mudah di-maintenance, dan tahan terhadap kegagalan jaringan.")
    ]
    for lbl, desc in c_finds:
        p = tf_con1.add_paragraph()
        p.text = f"✔ {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = EMERALD_GREEN
        p_sub = tf_con1.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(6)

    tf_con2 = add_card(s13, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Rekomendasi Kebijakan & Implementasi", "Aksi Strategis Berbasis Data", border_color=SKY_BLUE)
    c_recs = [
        ("Peningkatan Kualitas Tenaga Kerja", "Karena populasi adalah prediktor dominan, investasi pada pendidikan dan pelatihan vokasi akan melipatgandakan output GDP per kapita."),
        ("Penambahan Fitur Makroekonomi", "Pengembangan model selanjutnya dapat menambahkan variabel inflasi tahunan, suku bunga bank sentral, dan arus FDI."),
        ("Automasi Retraining Airflow", "Mengatur DAG Airflow untuk menjalankan retraining model secara terjadwal setiap kuartal guna mendeteksi pergeseran pola ekonomi (data drift).")
    ]
    for lbl, desc in c_recs:
        p = tf_con2.add_paragraph()
        p.text = f"➔ {lbl}:"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SKY_BLUE
        p_sub = tf_con2.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(6)

    # Save logic with robust fallback if file is locked
    filenames_to_try = [
        "Economic_Intelligence_Pipeline_Aesthetic.pptx",
        "Economic_Intelligence_Pipeline_Final.pptx",
        "Economic_Intelligence_Pipeline_Visual.pptx",
        "Economic_Intelligence_Pipeline.pptx"
    ]
    saved_name = None
    for fname in filenames_to_try:
        try:
            prs.save(fname)
            saved_name = fname
            print(f"Presentation saved successfully as '{fname}'!")
            break
        except PermissionError:
            continue

    if not saved_name:
        import time
        ts_name = f"Economic_Intelligence_Pipeline_{int(time.time())}.pptx"
        prs.save(ts_name)
        print(f"Presentation saved as timestamped file '{ts_name}'!")

if __name__ == "__main__":
    create_presentation()
