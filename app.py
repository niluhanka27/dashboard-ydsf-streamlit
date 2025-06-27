import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman agar menggunakan layout lebar
st.set_page_config(layout="wide", page_title="Dashboard YDSF Surabaya")

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

@st.cache_data
def load_single_data(program_name):
    """Fungsi untuk memuat data SATU program."""
    df = pd.read_csv(DATA_FILES[program_name], sep=';', encoding='latin1')
    df['Jumlah Bantuan'] = pd.to_numeric(df['Jumlah Bantuan'], errors='coerce')
    df['Durasi Total'] = pd.to_numeric(df['Durasi Total'], errors='coerce')
    return df

@st.cache_data
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
    "Dakwah": { 
        "nama_cluster": {
            0: "Cluster 0: Dakwah Umum dengan Proses Lambat", 
            1: "Cluster 1: Dakwah Spesifik dengan Proses Cepat"
        }, 
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    },
    "Kemanusiaan": {
        "nama_cluster": {
            0: "Cluster 0: Bantuan Kemanusiaan Umum dengan Respon Cepat",
            1: "Cluster 1: Bantuan Kemanusiaan Produktif dengan Respon Lambat"
        },
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    },
    "Masjid": {
        "nama_cluster": {
            0: "Cluster 0: Pembangunan Masjid Regional dengan Proses Lambat",
            1: "Cluster 1: Startup dan Masjid Regional – Penyaluran Cepat",
            2: "Cluster 2: Kemitraan Masjid & Fasilitas – Penyaluran Cepat",
            3: "Cluster 3: Distribusi Masjid Lokal – Penyaluran Cepat"
        },
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    },
    "Pendidikan": { 
        "nama_cluster": {
            0: "Cluster 0: Pendidikan Fisik & Guru – Proses Lambat",
            1: "Cluster 1: Bantuan Guru dan Sarpras Minor – Proses Kilat",
            2: "Cluster 2: Bantuan Pendidikan Umum – Proses Cepat",
            3: "Cluster 3: Insentif Guru – Penyaluran Bertahap"
        }, 
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    },
    "Zakat": {
        "nama_cluster": {
            0: "Cluster 0: Zakat Hidup & Kesehatan – Penyaluran Cepat",
            1: "Cluster 1: Zakat Kebutuhan Dasar – Penyaluran Bertahap",
            2: "Cluster 2: Zakat Relawan & Kebutuhan Pokok – Proses Cepat"
        },
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    },
    "Yatim": {
        "nama_cluster": {
            0: "Cluster 0: Beasiswa Yatim Panti – Penyaluran Kilat",
            1: "Cluster 1: Beasiswa Non-Panti – Proses Lambat",
            2: "Cluster 2: Beasiswa Non-Panti SD – Penyaluran Cepat"
        },
        "penjelasan": "Penamaan cluster didasarkan pada variabel paling signifikan dan berpengaruh pada pembentukan cluster, yaitu **Durasi Total** dan **Kat. Subprogram**."
    }
}

# --- SIDEBAR (NAVIGASI UTAMA) ---
col1, col2 = st.sidebar.columns(2)
with col1:
    st.image("assets/logo_kampus.png", width=60)
with col2:
    st.image("assets/logo_stakeholder.png", width=60)

st.sidebar.title("Navigasi & Filter")
selected_page = st.sidebar.radio("Pilih Halaman:", options=["Halaman Utama", "Data Penerima Bantuan", "Analisis Eksploratif (EDA)", "Profiling Cluster"])

selected_program = None
if selected_page != "Halaman Utama":
    selected_program = st.sidebar.selectbox("Pilih Program untuk Detail:", options=list(DATA_FILES.keys()))
    
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size:11px; color:grey;'>Dibuat oleh:<br><b>Ni Luh Ayu - Mahasiswa Sains Data Terapan - PENS</b></p>", unsafe_allow_html=True)


# ==================================================================
#                     HALAMAN UTAMA (WELCOME PAGE)
# ==================================================================
if selected_page == "Halaman Utama":
    st.title("Dashboard Penerima Bantuan Lembaga Yayasan Dana Sosial Al-Falah (YDSF) Surabaya")
    st.markdown("---")
    st.header("Selamat Datang di Dashboard YDSF")
    st.write("Halaman ini menyajikan gambaran umum dari seluruh program bantuan YDSF dari tahun 2018 hingga Agustus 2025.")
    
    df_all = load_all_data()

    if not df_all.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Total Bantuan yang Disalurkan per Program**")
            total_per_program = df_all.groupby('program_nama')['Jumlah Bantuan'].sum().sort_values(ascending=False)
            fig1 = px.bar(total_per_program, y='Jumlah Bantuan', text_auto='.2s', labels={'program_nama':'Program', 'y':'Total Bantuan (Rp)'})
            st.plotly_chart(fig1, use_container_width=True)

            st.info("**Tren Jumlah Bantuan Tahunan per Program**")
            tren_tahunan_program = df_all.groupby(['Tahun', 'program_nama'])['Jumlah Bantuan'].sum().reset_index()
            fig2 = px.line(tren_tahunan_program, x='Tahun', y='Jumlah Bantuan', color='program_nama', markers=True, labels={'Tahun':'Tahun', 'Jumlah Bantuan':'Total Bantuan (Rp)', 'program_nama':'Program'})
            st.plotly_chart(fig2, use_container_width=True)

            st.info("**Distribusi Sumber Anggaran per Program**")
            fig4 = px.histogram(df_all, x='program_nama', color='Sumber Anggaran', barmode='group', text_auto=True, labels={'program_nama':'Program', 'Sumber Anggaran':'Jenis Anggaran'})
            st.plotly_chart(fig4, use_container_width=True)
            
        with col2:
            st.info("**Jumlah Penerima per Tahun (Semua Program)**")
            penerima_per_tahun = df_all.groupby('Tahun').size().reset_index(name='jumlah')
            fig5 = px.line(penerima_per_tahun, x='Tahun', y='jumlah', markers=True, labels={'Tahun':'Tahun', 'jumlah':'Jumlah Penerima'})
            st.plotly_chart(fig5, use_container_width=True)

            st.info("**Rata-Rata Durasi Pencairan per Program**")
            durasi_per_program = df_all.groupby('program_nama')['Durasi Total'].mean().sort_values(ascending=False)
            fig3 = px.bar(durasi_per_program, y='Durasi Total', text_auto='.1f', labels={'program_nama':'Program', 'y':'Rata-rata Durasi (Hari)'})
            st.plotly_chart(fig3, use_container_width=True)
        
            st.info("**Distribusi Jumlah Bantuan (Seluruh Data)**")
            fig6 = px.histogram(df_all, x='Jumlah Bantuan', nbins=50, marginal='box', labels={'Jumlah Bantuan':'Jumlah Bantuan (Rp)'})
            st.plotly_chart(fig6, use_container_width=True)

# ==================================================================
#            HALAMAN LAIN (Tergantung pada Pilihan Program)
# ==================================================================
elif selected_program:
    st.header(f"{selected_page} - Program {selected_program}")
    
    df_single = load_single_data(selected_program)
    
    # --- BAGIAN UNTUK HALAMAN DATA PENERIMA BANTUAN ---
    if selected_page == "Data Penerima Bantuan":
        st.info("Gunakan filter di bawah untuk menyeleksi data.")
        all_years = sorted(df_single['Tahun'].dropna().unique().astype(int))
        selected_years = st.multiselect("Filter berdasarkan Tahun:", options=all_years, default=all_years)
        
        search_query = st.text_input("Pencarian", placeholder="Masukkan nama atau NIK/No.KK")

        df_filtered_data = df_single[df_single['Tahun'].isin(selected_years)]
        if search_query:
            df_filtered_data = df_filtered_data[
                df_filtered_data['Nama Penerima'].str.contains(search_query, case=False, na=False) |
                df_filtered_data['KTP/SIM'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        
        st.dataframe(df_filtered_data.drop(columns=['Cluster'], errors='ignore'))

    # --- BAGIAN UNTUK HALAMAN ANALISIS EKSPLORATIF (EDA) ---
    elif selected_page == "Analisis Eksploratif (EDA)":
        st.subheader("Filter Data")
        list_tahun = ["Semua Tahun"] + sorted(df_single['Tahun'].dropna().unique().astype(int), reverse=True)
        tahun_terpilih = st.selectbox("Pilih Tahun Analisis:", options=list_tahun)

        df_filtered_eda = df_single if tahun_terpilih == "Semua Tahun" else df_single[df_single['Tahun'] == tahun_terpilih]

        st.markdown("---")
        st.subheader("Ringkasan Umum Program")
        c1, c2, c3 = st.columns(3)
        c1.metric("Jumlah Nominal Bantuan yang Disalurkan", f"Rp {df_filtered_eda['Jumlah Bantuan'].sum():,.0f}")
        c2.metric("Jumlah Proses Penyaluran Bantuan", f"{df_filtered_eda.shape[0]} Kali")
        avg_durasi_val = df_filtered_eda['Durasi Total'].mean() if not df_filtered_eda.empty else 0
        c3.metric("Rata-rata Durasi", f"{avg_durasi_val:.0f} Hari")
        
        st.markdown("---")
        st.subheader("Visualisasi Detail Analisis")
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.info("**Rata-rata Durasi Total per Tahun**")
            avg_durasi_tahun = df_filtered_eda.groupby('Tahun')['Durasi Total'].mean().reset_index()
            fig_v1 = px.line(avg_durasi_tahun, x='Tahun', y='Durasi Total', markers=True, labels={'Durasi Total': 'Rata-rata Durasi (Hari)'})
            st.plotly_chart(fig_v1, use_container_width=True)

            st.info("**Jumlah Bantuan Rata-rata per Subprogram**")
            avg_bantuan_sub = df_filtered_eda.groupby('Kat. Subprogram')['Jumlah Bantuan'].mean().nlargest(10).sort_values()
            fig_v2 = px.bar(avg_bantuan_sub, x='Jumlah Bantuan', orientation='h', text_auto='.2s', labels={'index':'Subprogram', 'Jumlah Bantuan':'Rata-rata Bantuan (Rp)'})
            st.plotly_chart(fig_v2, use_container_width=True)

            st.info("**Durasi Total Berdasarkan Sumber Anggaran**")
            fig_v3 = px.box(df_filtered_eda, x='Sumber Anggaran', y='Durasi Total', points="all", labels={'Durasi Total':'Durasi Total (Hari)'})
            st.plotly_chart(fig_v3, use_container_width=True)
            
        with vcol2:
            st.info("**Jumlah Bantuan Berdasarkan Sumber Anggaran**")
            sum_bantuan_sumber = df_filtered_eda.groupby('Sumber Anggaran')['Jumlah Bantuan'].sum().sort_values()
            fig_v4 = px.bar(sum_bantuan_sumber, x=sum_bantuan_sumber.index, y='Jumlah Bantuan', text_auto='.2s', labels={'x':'Sumber Anggaran', 'Jumlah Bantuan':'Total Bantuan (Rp)'})
            st.plotly_chart(fig_v4, use_container_width=True)
            
            st.info("**Distribusi Durasi Total**")
            fig_v5 = px.histogram(df_filtered_eda, x='Durasi Total', nbins=30, marginal="box", labels={'Durasi Total':'Durasi Total (Hari)'})
            st.plotly_chart(fig_v5, use_container_width=True)

            st.info("**Distribusi Jumlah Bantuan**")
            fig_v6 = px.histogram(df_filtered_eda, x='Jumlah Bantuan', nbins=30, marginal="box", labels={'Jumlah Bantuan':'Jumlah Bantuan (Rp)'})
            st.plotly_chart(fig_v6, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Analisis Subprogram per Kota")
        list_kota = ["Semua Kota"] + sorted(df_filtered_eda['Kota'].dropna().unique())
        kota_terpilih = st.selectbox("Pilih Kota untuk melihat detail Subprogram:", options=list_kota)

        df_kota_filtered = df_filtered_eda if kota_terpilih == "Semua Kota" else df_filtered_eda[df_filtered_eda['Kota'] == kota_terpilih]
        
        st.info(f"**Top 5 Subprogram di {kota_terpilih}**")
        top_sub_kota = df_kota_filtered['Kat. Subprogram'].value_counts().nlargest(5)
        fig_v7 = px.bar(top_sub_kota, y=top_sub_kota.index, x=top_sub_kota.values, orientation='h', text_auto=True, labels={'y':'Subprogram', 'x':'Jumlah Transaksi'})
        st.plotly_chart(fig_v7, use_container_width=True)

    # --- BAGIAN UNTUK HALAMAN PROFILING CLUSTER ---
    elif selected_page == "Profiling Cluster":
        info = CLUSTER_INFO.get(selected_program, {})
        if not info or not info.get("nama_cluster"):
            st.warning(f"Informasi cluster untuk '{selected_program}' belum diatur.")
        else:
            nama_cluster_options = list(info["nama_cluster"].values())
            if not nama_cluster_options:
                st.warning("Tidak ada nama cluster yang terdefinisi untuk program ini.")
            else:
                selected_cluster_nama = st.selectbox("Pilih Cluster untuk Melihat Profil Detail:", options=nama_cluster_options)

                if selected_cluster_nama:
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
                        st.markdown("**Ringkasan Statistik Cluster**")
                        summary_df = generate_cluster_summary_df(df_cluster)
                        st.table(summary_df)
                        
                        st.markdown("---")
                        st.markdown("**Visualisasi Detail Karakteristik Cluster**")
                        vcol1, vcol2 = st.columns(2)
                        with vcol1:
                            st.info("**Top 5 Jumlah Bantuan Paling Sering Diberikan**")
                            top_bantuan = df_cluster['Jumlah Bantuan'].value_counts().nlargest(5)
                            st.bar_chart(top_bantuan)

                            st.info("**Top 5 Kota Paling Dominan**")
                            top_kota = df_cluster['Kota'].value_counts().nlargest(5)
                            st.bar_chart(top_kota)

                        with vcol2:
                            st.info("**Top 5 Durasi Tunggu Paling Sering**")
                            top_durasi = df_cluster['Durasi Total'].value_counts().nlargest(5)
                            st.bar_chart(top_durasi)
                            
                            st.info("**Top 5 Subprogram Paling Dominan**")
                            top_sub = df_cluster['Kat. Subprogram'].value_counts().nlargest(5)
                            if not top_sub.empty:
                                fig_v5 = px.bar(top_sub, y=top_sub.index, x=top_sub.values, orientation='h', text_auto=True, labels={'y':'Kategori Subprogram', 'x':'Jumlah Penerima'})
                                fig_v5.update_layout(yaxis={'categoryorder':'total ascending'})
                                st.plotly_chart(fig_v5, use_container_width=True)
                            else:
                                st.warning("Tidak ada data subprogram untuk ditampilkan pada filter ini.")

                        st.info("**Distribusi Sumber Anggaran**")
                        fig_pie = px.pie(df_cluster, names='Sumber Anggaran', hole=0.4)
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        st.markdown("---")
                        st.markdown("**Daftar Rinci Penerima Bantuan di Cluster Ini**")
                        
                        search_query_cluster = st.text_input("Cari di dalam cluster:", placeholder="Masukkan nama atau NIK/No.KK", key="search_cluster")
                        
                        df_table_cluster = df_cluster
                        if search_query_cluster:
                            df_table_cluster = df_cluster[
                                df_cluster['Nama Penerima'].str.contains(search_query_cluster, case=False, na=False) |
                                df_cluster['KTP/SIM'].astype(str).str.contains(search_query_cluster, case=False, na=False)
                            ]
                        st.dataframe(df_table_cluster)

else:
    # Kondisi jika pengguna berada di halaman detail tapi belum memilih program
    st.info("👈 Silakan pilih program di sidebar untuk melihat detailnya.")