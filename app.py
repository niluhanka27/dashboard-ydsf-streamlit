import streamlit as st
import pandas as pd
import plotly.express as px

# --- Palet Warna Kustom ---
# Palet warna brand YDSF (warna terang dihilangkan agar kontras)
YDSF_PALETTE = ["#0c58a4", "#4ab23a", "#84bd8f", "#84a4cc"]
# Palet warna dengan kontras tinggi untuk grafik yang membandingkan banyak kategori
HIGH_CONTRAST_PALETTE = px.colors.qualitative.Plotly

# Konfigurasi halaman agar menggunakan layout lebar dan sidebar tertutup di awal
st.set_page_config(layout="wide", page_title="Dashboard YDSF Surabaya", initial_sidebar_state="collapsed")

# --- DATA LOADING ---
DATA_FILES = {
    "Dakwah": "data/program_dakwah.csv",
    "Kemanusiaan": "data/program_kemanusiaan.csv",
    "Masjid": "data/program_masjid.csv",
    "Pendidikan": "data/program_pendidikan.csv",
    "Zakat": "data/program_zakat.csv",
    "Yatim": "data/program_yatim.csv",
}

# --- FUNGSI-FUNGSI BANTU ---
try:
    cache_decorator = st.cache_data
except AttributeError:
    cache_decorator = st.cache(allow_output_mutation=True)

@cache_decorator
def load_single_data(program_name):
    """Fungsi untuk memuat data SATU program."""
    df = pd.read_csv(DATA_FILES[program_name], sep=';', encoding='latin1')
    df['Jumlah Bantuan'] = pd.to_numeric(df['Jumlah Bantuan'], errors='coerce')
    df['Durasi Total'] = pd.to_numeric(df['Durasi Total'], errors='coerce')
    return df

@cache_decorator
def load_all_data():
    """Fungsi untuk memuat dan menggabungkan SEMUA data program."""
    list_of_dfs = []
    for program, file_path in DATA_FILES.items():
        try:
            df = pd.read_csv(file_path, sep=';', encoding='latin1')
            df['program_nama'] = program
            list_of_dfs.append(df)
        except FileNotFoundError:
            st.error(f"File tidak ditemukan: {file_path}.")
            return pd.DataFrame()
    
    if not list_of_dfs:
        return pd.DataFrame()

    combined_df = pd.concat(list_of_dfs, ignore_index=True)
    combined_df['Jumlah Bantuan'] = pd.to_numeric(combined_df['Jumlah Bantuan'], errors='coerce')
    combined_df['Durasi Total'] = pd.to_numeric(combined_df['Durasi Total'], errors='coerce')
    return combined_df

def generate_cluster_summary_df(df_cluster):
    """Membuat DataFrame ringkasan statistik untuk satu cluster."""
    if df_cluster.empty:
        return pd.DataFrame()
    median_bantuan = f"Rp {df_cluster['Jumlah Bantuan'].median():,.0f}"
    median_durasi = f"{df_cluster['Durasi Total'].median():.0f} Hari"
    kota_dist = df_cluster['Kota'].value_counts(normalize=True).nlargest(2)
    kota_summary = ", ".join([f"{idx} ({val:.1%})" for idx, val in kota_dist.items()]) if not kota_dist.empty else "N/A"
    sub_dist = df_cluster['Kat. Subprogram'].value_counts(normalize=True).nlargest(2)
    sub_summary = ", ".join([f"{idx} ({val:.1%})" for idx, val in sub_dist.items()]) if not sub_dist.empty else "N/A"
    angg_dist = df_cluster['Sumber Anggaran'].value_counts(normalize=True)
    angg_summary = ", ".join([f"{idx} ({val:.1%})" for idx, val in angg_dist.items()]) if not angg_dist.empty else "N/A"
    summary_data = {
        "Metrik": ["Median Jumlah Bantuan", "Median Durasi Total", "Kota Dominan (Top 2)", "Subprogram Dominan (Top 2)", "Sumber Anggaran Dominan"],
        "Nilai": [median_bantuan, median_durasi, kota_summary, sub_summary, angg_summary]
    }
    return pd.DataFrame(summary_data).set_index('Metrik')


# --- KUSTOMISASI UNTUK CLUSTERING ---
CLUSTER_INFO = {
    "Dakwah": { "nama_cluster": {0: "Cluster 0: Dakwah Umum dengan Proses Lambat", 1: "Cluster 1: Dakwah Spesifik dengan Proses Cepat"}, "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."},
    "Kemanusiaan": {"nama_cluster": {0: "Cluster 0: Bantuan Kemanusiaan Responsif dengan Proses Cepat", 1: "Cluster 1: Bantuan Kemanusiaan Produktif dengan Proses Lambat"},"penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."},
    "Masjid": {"nama_cluster": {0: "Cluster 0: Bantuan Infrastruktur Umum dengan Proses Sangat Lambat", 1: "Cluster 1: Pemberdayaan Masjid & Startup dengan Proses Cepat", 2: "Cluster 2: Kemitraan Masjid Spesifik dengan Proses Cepat", 3: "Cluster 3: Bantuan Infrastruktur Lokal dengan Proses Cepat"},"penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."},
    "Pendidikan": {"nama_cluster": {0: "Cluster 0: Bantuan Sarana & Personel dengan Proses Sangat Lambat", 1: "Cluster 1: Bantuan Sarana & Guru Spesifik dengan Proses Kilat", 2: "Cluster 2: Bantuan Pendidikan Umum dengan Proses Cepat", 3: "Cluster 3: Bantuan Insentif Guru dengan Proses Bertahap"}, "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."},
    "Zakat": {"nama_cluster": {0: "Cluster 0: Zakat Kebutuhan Primer dengan Proses Cepat", 1: "Cluster 1: Zakat Kebutuhan Primer dengan Proses Bertahap", 2: "Cluster 2: Zakat Kebutuhan & Relawan dengan Proses Cepat"},"penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."},
    "Yatim": {"nama_cluster": {0: "Cluster 0: Beasiswa Panti Asuhan dengan Penyaluran Kilat", 1: "Cluster 1: Beasiswa Non-Panti dengan Proses Lambat", 2: "Cluster 2: Beasiswa SD Non-Panti dengan Penyaluran Cepat"},"penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan, yaitu **Durasi Total** dan **Kat. Subprogram**."}
}

# --- SIDEBAR ---
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/logo_kampus.png", width=60)
    with col2:
        st.image("assets/logo_stakeholder.png", width=60) 

    st.title("Navigasi & Filter")
    selected_page = st.radio("Pilih Halaman:", options=["Home", "Data Penerima Bantuan", "Analisis Eksploratif (EDA)", "Profiling Cluster"])

    selected_program = None
    if selected_page != "Home":
        selected_program = st.selectbox("Pilih Program untuk Detail:", options=list(DATA_FILES.keys()))
        
    st.markdown("---")
    st.markdown("<p style='font-size:11px; color:grey;'>Dibuat oleh:<br><b>Ni Luh Ayu - Mahasiswa Sains Data Terapan - PENS</b></p>", unsafe_allow_html=True)


# ==================================================================
#                     HALAMAN UTAMA (HOME)
# ==================================================================
# Ganti seluruh blok 'if selected_page == "Home":' Anda dengan ini:

if selected_page == "Home":
    st.title("Dashboard Penerima Bantuan YDSF Surabaya")
    st.markdown("---")
    st.header("Ringkasan Eksekutif Lintas Program")
    st.write("Halaman ini menyajikan gambaran umum dari seluruh program bantuan YDSF dari tahun 2018 hingga Agustus 2025.")
    
    df_all = load_all_data()

    if not df_all.empty:
        st.subheader("Ringkasan Kinerja Lintas Program")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Total Bantuan yang Disalurkan per Program**")
            total_per_program = df_all.groupby('program_nama')['Jumlah Bantuan'].sum().sort_values(ascending=False)
            avg_bantuan_program = total_per_program.mean()
            # REVISI WARNA: Menggunakan warna spesifik dari palet
            fig1 = px.bar(total_per_program, y='Jumlah Bantuan', text_auto='.2s', labels={'program_nama':'Program', 'y':'Total Bantuan (Rp)'},
                          color_discrete_sequence=[YDSF_PALETTE[0]])
            fig1.add_hline(y=avg_bantuan_program, line_dash="dash", line_color="red", annotation_text="Rata-rata")
            fig1.update_layout(dragmode=False)
            st.plotly_chart(fig1, use_container_width=True)
            program_terbesar = total_per_program.index[0]
            nilai_terbesar = total_per_program.iloc[0]
            st.markdown(f"""
            <div style='text-align: justify; font-size: 14px;'>
            <b>Analisis:</b> Grafik ini menunjukkan fokus alokasi dana YDSF antar program.<br>
            <b>Insight:</b> Program **{program_terbesar}** menyalurkan dana terbesar (Rp {nilai_terbesar:,.0f}), menandakan pilar utama lembaga.
            </div>""", unsafe_allow_html=True)
            
        with col2:
            st.info("**Efisiensi Proses Antar Program**")
            durasi_per_program = df_all.groupby('program_nama')['Durasi Total'].mean().sort_values(ascending=False)
            avg_durasi_all = df_all['Durasi Total'].mean()
            # REVISI WARNA: Menggunakan warna spesifik dari palet
            fig3 = px.bar(durasi_per_program, y='Durasi Total', text_auto='.0f', labels={'program_nama':'Program', 'y':'Rata-rata Durasi (Hari)'},
                          color_discrete_sequence=[YDSF_PALETTE[1]])
            fig3.add_hline(y=avg_durasi_all, line_dash="dash", line_color="red", annotation_text="Rata-rata")
            fig3.update_layout(dragmode=False)
            st.plotly_chart(fig3, use_container_width=True)
            program_terlama = durasi_per_program.index[0]
            program_tercepat = durasi_per_program.index[-1]
            st.markdown(f"""
            <div style='text-align: justify; font-size: 14px;'>
            <b>Analisis:</b> Membandingkan rata-rata kecepatan penyaluran bantuan per program.<br>
            <b>Insight:</b> Program **{program_tercepat}** memiliki proses tercepat. Durasi terlama pada program **{program_terlama}** wajar terjadi karena umumnya memerlukan proses verifikasi yang lebih kompleks.
            </div>""", unsafe_allow_html=True)

        st.info("**Tren Pertumbuhan Penyaluran Bantuan per Program**")
        tren_tahunan_program = df_all.groupby(['Tahun', 'program_nama'])['Jumlah Bantuan'].sum().reset_index()
        # REVISI WARNA: Menggunakan palet kontras tinggi
        fig2 = px.line(tren_tahunan_program, x='Tahun', y='Jumlah Bantuan', color='program_nama', markers=True, 
                       labels={'Tahun':'Tahun', 'Jumlah Bantuan':'Total Bantuan (Rp)', 'program_nama':'Program'},
                       color_discrete_sequence=HIGH_CONTRAST_PALETTE)
        fig2.update_layout(dragmode=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("<div style='text-align: justify; font-size: 14px;'><b>Analisis:</b> Membandingkan pertumbuhan dana setiap program dari tahun ke tahun.<br><b>Insight:</b> Garis yang menanjak tajam menandakan pertumbuhan pesat, sementara garis yang landai menunjukkan program yang stabil atau sudah matang.</div>", unsafe_allow_html=True)
        
# ==================================================================
#            HALAMAN LAIN (Tergantung pada Pilihan Program)
# ==================================================================
elif selected_program:
    st.header(f"{selected_page} - Program {selected_program}")
    
    df_single = load_single_data(selected_program)
    
    # --- HALAMAN DATA PENERIMA BANTUAN ---
    if selected_page == "Data Penerima Bantuan":
        st.info("Gunakan filter di bawah untuk menyeleksi data.")
        all_years = sorted(df_single['Tahun'].dropna().unique().astype(int))
        selected_years = st.multiselect("Filter berdasarkan Tahun:", options=all_years, default=all_years)
        if not selected_years:
            selected_years = all_years
        
        search_query = st.text_input("Pencarian", placeholder="Masukkan Nama Penerima atau KTP/SIM")
        df_filtered_data = df_single[df_single['Tahun'].isin(selected_years)]
        if search_query:
            df_filtered_data = df_filtered_data[
                df_filtered_data['Nama Penerima'].str.contains(search_query, case=False, na=False) |
                df_filtered_data['KTP/SIM'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        st.dataframe(df_filtered_data.drop(columns=['Cluster'], errors='ignore'))
        st.markdown("<p style='font-size:12px; color:grey;'><i><b>Durasi Total:</b> Waktu yang dibutuhkan (dalam hari) dari pengajuan awal hingga bantuan diterima oleh penerima.</i></p>", unsafe_allow_html=True)

    # --- HALAMAN ANALISIS EKSPLORATIF (EDA) ---
    elif selected_page == "Analisis Eksploratif (EDA)":
        st.subheader("Filter Data")
        list_tahun = ["Semua Tahun"] + sorted(df_single['Tahun'].dropna().unique().astype(int), reverse=True)
        tahun_terpilih = st.selectbox("Pilih Tahun Analisis:", options=list_tahun)

        df_filtered_eda = df_single if tahun_terpilih == "Semua Tahun" else df_single[df_single['Tahun'] == tahun_terpilih]

        st.markdown("---")
        st.subheader(f"Ringkasan Umum Program - Periode {tahun_terpilih}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Jumlah Nominal Bantuan yang Disalurkan", f"Rp {df_filtered_eda['Jumlah Bantuan'].sum():,.0f}")
        c2.metric("Jumlah Proses Penyaluran Bantuan", f"{df_filtered_eda.shape[0]} Kali")
        avg_durasi_val = df_filtered_eda['Durasi Total'].mean() if not df_filtered_eda.empty else 0
        c3.metric("Rata-rata Durasi", f"{avg_durasi_val:.0f} Hari")
        
        st.markdown("---")
        st.subheader("Visualisasi Detail Analisis")
        
        # --- REVISI TATA LETAK EDA DIMULAI DARI SINI ---
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.info("**Top 10 Kategori Subprogram**")
            top_sub = df_filtered_eda['Kat. Subprogram'].value_counts().nlargest(10)
            fig_top_sub = px.bar(top_sub, y=top_sub.index, x=top_sub.values, orientation='h', text_auto=True, labels={'y':'', 'x':'Jumlah Transaksi'})
            fig_top_sub.update_layout(yaxis={'categoryorder':'total ascending'}, dragmode=False)
            st.plotly_chart(fig_top_sub, use_container_width=True)
            top_program_nama = top_sub.index[0] if not top_sub.empty else "N/A"
            st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Subprogram **'{top_program_nama}'** adalah aktivitas inti dari program ini pada periode **{tahun_terpilih}**.</div>", unsafe_allow_html=True)
            
            st.info("**Jumlah Bantuan Rata-rata per Subprogram**")
            avg_bantuan_sub = df_filtered_eda.groupby('Kat. Subprogram')['Jumlah Bantuan'].mean().nlargest(10).sort_values()
            fig_v2 = px.bar(avg_bantuan_sub, x='Jumlah Bantuan', orientation='h', text_auto='.2s', labels={'index':'Subprogram', 'Jumlah Bantuan':'Rata-rata Bantuan (Rp)'})
            fig_v2.update_layout(dragmode=False)
            st.plotly_chart(fig_v2, use_container_width=True)
            sub_terbesar = avg_bantuan_sub.index[-1] if not avg_bantuan_sub.empty else "N/A"
            st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Subprogram **'{sub_terbesar}'** secara konsisten memberikan bantuan dengan nominal paling besar, menandakan ini adalah bantuan 'high-value'.</div>", unsafe_allow_html=True)
            
        with vcol2:
            st.info("**Top 10 Kota Penerima Bantuan**")
            top_kota = df_filtered_eda['Kota'].value_counts().nlargest(10)
            fig_top_kota = px.bar(top_kota, y=top_kota.index, x=top_kota.values, orientation='h', text_auto=True, labels={'y':'', 'x':'Jumlah Transaksi'})
            fig_top_kota.update_layout(yaxis={'categoryorder':'total ascending'}, dragmode=False)
            st.plotly_chart(fig_top_kota, use_container_width=True)
            top_kota_nama = top_kota.index[0] if not top_kota.empty else "N/A"
            st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Wilayah **{top_kota_nama}** menjadi fokus utama penyaluran untuk program ini pada periode **{tahun_terpilih}**.</div>", unsafe_allow_html=True)
            
            st.info("**Total Bantuan Berdasarkan Sumber Anggaran**")
            sum_bantuan_sumber = df_filtered_eda.groupby('Sumber Anggaran')['Jumlah Bantuan'].sum().sort_values()
            fig_v4 = px.bar(sum_bantuan_sumber, x=sum_bantuan_sumber.index, y='Jumlah Bantuan', text_auto='.2s', labels={'x':'Sumber Anggaran', 'Jumlah Bantuan':'Total Bantuan (Rp)'})
            fig_v4.update_layout(dragmode=False)
            st.plotly_chart(fig_v4, use_container_width=True)
            sumber_terbesar = sum_bantuan_sumber.index[-1] if not sum_bantuan_sumber.empty else "N/A"
            st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Dana dari **{sumber_terbesar}** menjadi penopang finansial utama untuk program ini pada periode **{tahun_terpilih}**.</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        st.info("**Rata-rata Durasi Total per Tahun**")
        avg_durasi_tahun = df_filtered_eda.groupby('Tahun')['Durasi Total'].mean().reset_index()
        fig_v1 = px.line(avg_durasi_tahun, x='Tahun', y='Durasi Total', markers=True, labels={'Durasi Total': 'Rata-rata Durasi (Hari)'})
        fig_v1.update_layout(dragmode=False)
        st.plotly_chart(fig_v1, use_container_width=True)
        st.markdown("<div style='font-size:14px;'><b>Insight:</b> Jika garis tren menurun, maka proses penyaluran program ini menjadi semakin efisien setiap tahunnya. Sebaliknya, jika menanjak, perlu ada evaluasi proses.</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Analisis Interaktif: Top Subprogram per Kota")
        list_kota = ["Semua Kota"] + sorted(df_filtered_eda['Kota'].dropna().unique())
        kota_terpilih = st.selectbox("Pilih Kota untuk melihat detail Subprogram:", options=list_kota)
        df_kota_filtered = df_filtered_eda if kota_terpilih == "Semua Kota" else df_filtered_eda[df_filtered_eda['Kota'] == kota_terpilih]
        
        st.info(f"**Top 5 Subprogram di {kota_terpilih}**")
        top_sub_kota = df_kota_filtered['Kat. Subprogram'].value_counts().nlargest(5)
        fig_v7 = px.bar(top_sub_kota, y=top_sub_kota.index, x=top_sub_kota.values, orientation='h', text_auto=True, labels={'y':'Subprogram', 'x':'Jumlah Transaksi'})
        fig_v7.update_layout(dragmode=False)
        st.plotly_chart(fig_v7, use_container_width=True)

    # --- BAGIAN UNTUK HALAMAN PROFILING CLUSTER ---
    elif selected_page == "Profiling Cluster":
        info = CLUSTER_INFO.get(selected_program, {})
        if not info or not info.get("nama_cluster"):
            st.warning(f"Informasi cluster untuk '{selected_program}' belum diatur.")
        else:
            nama_cluster_options = ["Pilih cluster..."] + list(info["nama_cluster"].values())
            selected_cluster_nama = st.selectbox("Pilih Cluster untuk Melihat Profil Detail:", options=nama_cluster_options)

            if selected_cluster_nama != "Pilih cluster...":
                st.subheader(selected_cluster_nama)
                st.info(info.get("penjelasan", "Tidak ada penjelasan mengenai dasar penamaan cluster."))
                st.markdown("---")
                
                list_tahun_cluster = ["Semua Tahun"] + sorted(df_single['Tahun'].dropna().unique().astype(int), reverse=True)
                tahun_terpilih_cluster = st.selectbox("Pilih Tahun Analisis:", options=list_tahun_cluster, key="filter_tahun_cluster")
                
                selected_cluster_key = [k for k, v in info["nama_cluster"].items() if v == selected_cluster_nama][0]
                df_cluster_all_years = df_single[df_single['Cluster'] == selected_cluster_key].copy()
                
                df_cluster = df_cluster_all_years if tahun_terpilih_cluster == "Semua Tahun" else df_cluster_all_years[df_cluster_all_years['Tahun'] == tahun_terpilih_cluster]

                if df_cluster.empty:
                    st.warning(f"Tidak ada data untuk cluster ini pada tahun {tahun_terpilih_cluster}.")
                else:
                    st.markdown("#### Ringkasan Statistik Cluster")
                    summary_df = generate_cluster_summary_df(df_cluster)
                    st.table(summary_df)
                    
                    st.markdown("---")
                    st.subheader("Visualisasi Karakteristik Cluster")
                    
                    vcol1, vcol2 = st.columns(2)
                    with vcol1:
                        st.info("**Top 5 Jumlah Bantuan Paling Sering Diberikan**")
                        top_bantuan = df_cluster['Jumlah Bantuan'].value_counts().nlargest(5)
                        fig_bantuan = px.bar(top_bantuan, y=top_bantuan.index, x=top_bantuan.values, orientation='h', text_auto=True, labels={'y':'Jumlah Bantuan (Rp)', 'x':'Frekuensi'})
                        fig_bantuan.update_layout(yaxis={'type': 'category', 'categoryorder':'total ascending'}, dragmode=False)
                        st.plotly_chart(fig_bantuan, use_container_width=True)
                        bantuan_dominan = f"Rp {top_bantuan.index[0]:,.0f}" if not top_bantuan.empty else "N/A"
                        st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Nominal bantuan **{bantuan_dominan}** adalah yang paling sering diberikan untuk segmen ini.</div>", unsafe_allow_html=True)

                        st.info("**Top 5 Kota Paling Dominan**")
                        top_kota = df_cluster['Kota'].value_counts().nlargest(5)
                        fig_kota = px.bar(top_kota, y=top_kota.index, x=top_kota.values, orientation='h', text_auto=True, labels={'y':'Kota', 'x':'Jumlah Penerima'})
                        fig_kota.update_layout(yaxis={'categoryorder':'total ascending'}, dragmode=False)
                        st.plotly_chart(fig_kota, use_container_width=True)
                        kota_dominan = top_kota.index[0] if not top_kota.empty else "N/A"
                        st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Wilayah **{kota_dominan}** menjadi basis utama untuk cluster ini.</div>", unsafe_allow_html=True)
                    
                    with vcol2:
                        st.info("**Top 5 Durasi Tunggu Paling Sering**")
                        top_durasi = df_cluster['Durasi Total'].value_counts().nlargest(5)
                        fig_durasi = px.bar(top_durasi, y=top_durasi.index, x=top_durasi.values, orientation='h', text_auto=True, labels={'y':'Durasi Total (Hari)', 'x':'Frekuensi'})
                        fig_durasi.update_layout(yaxis={'type': 'category', 'categoryorder':'total ascending'}, dragmode=False)
                        st.plotly_chart(fig_durasi, use_container_width=True)
                        durasi_dominan = top_durasi.index[0] if not top_durasi.empty else "N/A"
                        st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Durasi proses yang paling umum untuk cluster ini adalah **{durasi_dominan} hari**.</div>", unsafe_allow_html=True)
                        
                        st.info("**Top 5 Subprogram Paling Dominan**")
                        top_sub = df_cluster['Kat. Subprogram'].value_counts().nlargest(5)
                        fig_sub = px.bar(top_sub, y=top_sub.index, x=top_sub.values, orientation='h', text_auto=True, labels={'y':'', 'x':'Jumlah Penerima'})
                        fig_sub.update_layout(yaxis={'categoryorder':'total ascending'}, dragmode=False)
                        st.plotly_chart(fig_sub, use_container_width=True)
                        sub_dominan = top_sub.index[0] if not top_sub.empty else "N/A"
                        st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Aktivitas utama dalam cluster ini adalah **'{sub_dominan}'**.</div>", unsafe_allow_html=True)
                    
                    st.info("**Distribusi Sumber Anggaran**")
                    sumber_anggaran = df_cluster['Sumber Anggaran'].value_counts()
                    fig_pie = px.pie(sumber_anggaran, names=sumber_anggaran.index, values=sumber_anggaran.values, hole=0.5)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(dragmode=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    sumber_dominan_pie = sumber_anggaran.index[0] if not sumber_anggaran.empty else "N/A"
                    persen_dominan_pie = sumber_anggaran.iloc[0]/sumber_anggaran.sum() if not sumber_anggaran.empty else 0
                    st.markdown(f"<div style='font-size:14px;'><b>Insight:</b> Sumber pendanaan untuk cluster ini didominasi oleh **{sumber_dominan_pie}** ({persen_dominan_pie:.1%}).</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.subheader("Daftar Rinci Penerima Bantuan di Cluster Ini")
                    st.write(f"Menampilkan data untuk **{selected_cluster_nama}** pada periode **{tahun_terpilih_cluster}**.")
                    
                    search_query_cluster = st.text_input("Cari di dalam cluster:", placeholder="Masukkan Nama Penerima atau KTP/SIM", key="search_cluster")
                    
                    df_table_cluster = df_cluster
                    if search_query_cluster:
                        df_table_cluster = df_cluster[
                            df_cluster['Nama Penerima'].str.contains(search_query_cluster, case=False, na=False) |
                            df_cluster['KTP/SIM'].astype(str).str.contains(search_query_cluster, case=False, na=False)
                        ]
                    st.dataframe(df_table_cluster.drop(columns=['Cluster'], errors='ignore'))
else:
    st.info("👈 Silakan pilih program di sidebar untuk melihat detailnya.")