import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Data Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# Memuat dataset bersih dari folder yang sama dengan dashboard.py
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    return df

all_df = load_data(data_path)

# ==============================================================================
# SIDEBAR FILTER
# ==============================================================================
st.sidebar.header("Filter Analisis")

available_years = sorted(all_df["order_year"].dropna().unique().tolist())
year_options = ["Semua Tahun"] + available_years
default_idx = year_options.index(2018) if 2018 in year_options else 0

selected_year = st.sidebar.selectbox(
    "Pilih Tahun Transaksi:",
    options=year_options,
    index=default_idx
)

available_statuses = sorted(all_df["order_status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Filter Status Pesanan:",
    options=available_statuses,
    default=available_statuses
)

# Terapkan filter
filtered_df = all_df[all_df["order_status"].isin(selected_statuses)].copy()
if selected_year != "Semua Tahun":
    filtered_df = filtered_df[filtered_df["order_year"] == selected_year]

period_label = f"Tahun {selected_year}" if selected_year != "Semua Tahun" else "Seluruh Periode (2016–2018)"

# ==============================================================================
# HEADER & KPI METRICS
# ==============================================================================
st.title("📊 E-Commerce Business Performance Dashboard")
st.markdown(f"Menampilkan hasil analisis performa penjualan, persebaran pelanggan, dan segmentasi RFM untuk periode **{period_label}**.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan Unik", f"{filtered_df['order_id'].nunique():,}")
with col2:
    st.metric("Total Pendapatan (Revenue)", f"BRL {filtered_df['price'].sum():,.2f}")
with col3:
    st.metric("Total Pelanggan Unik", f"{filtered_df['customer_unique_id'].nunique():,}")

st.divider()

if filtered_df.empty:
    st.warning("Tidak ada data transaksi untuk kombinasi filter yang dipilih.")
    st.stop()

# ==============================================================================
# VISUALISASI 1: KATEGORI PRODUK PENDAPATAN TERTINGGI & TERENDAH
# ==============================================================================
st.subheader(f"1. Kategori Produk dengan Pendapatan Tertinggi & Terendah ({period_label})")

revenue_by_cat = (
    filtered_df.groupby("product_category_name_english", as_index=False)
    .agg(total_revenue=("price", "sum"))
    .sort_values(by="total_revenue", ascending=False)
    .reset_index(drop=True)
)

total_rev = revenue_by_cat["total_revenue"].sum()
revenue_by_cat["share (%)"] = (revenue_by_cat["total_revenue"] / total_rev * 100).round(2)

fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(16, 5.5))

top_5_cat = revenue_by_cat.head(5).reset_index(drop=True)
bottom_5_cat = revenue_by_cat.tail(5).sort_values(by="total_revenue", ascending=True).reset_index(drop=True)

colors_top = ["#1f77b4", "#aec7e8", "#aec7e8", "#aec7e8", "#aec7e8"]
colors_bottom = ["#d62728", "#ff9896", "#ff9896", "#ff9896", "#ff9896"]

sns.barplot(
    x="total_revenue",
    y="product_category_name_english",
    data=top_5_cat,
    palette=colors_top,
    hue="product_category_name_english",
    legend=False,
    ax=ax1[0]
)
ax1[0].set_title("5 Kategori Pendapatan Tertinggi", fontsize=13, fontweight="bold")
ax1[0].set_xlabel("Total Pendapatan (BRL)")
ax1[0].set_ylabel(None)
ax1[0].set_xlim(0, top_5_cat["total_revenue"].max() * 1.30)

for idx, row in top_5_cat.iterrows():
    ax1[0].text(
        row["total_revenue"] + (top_5_cat["total_revenue"].max() * 0.02),
        idx,
        f"BRL {row['total_revenue']:,.0f} ({row['share (%)']}%)",
        va="center",
        fontsize=9.5
    )

sns.barplot(
    x="total_revenue",
    y="product_category_name_english",
    data=bottom_5_cat,
    palette=colors_bottom,
    hue="product_category_name_english",
    legend=False,
    ax=ax1[1]
)
ax1[1].set_title("5 Kategori Pendapatan Terendah", fontsize=13, fontweight="bold")
ax1[1].set_xlabel("Total Pendapatan (BRL)")
ax1[1].set_ylabel(None)
ax1[1].invert_xaxis()
ax1[1].yaxis.set_label_position("right")
ax1[1].yaxis.tick_right()
ax1[1].set_xlim(bottom_5_cat["total_revenue"].max() * 1.35, 0)

for idx, row in bottom_5_cat.iterrows():
    ax1[1].text(
        row["total_revenue"] + (bottom_5_cat["total_revenue"].max() * 0.03),
        idx,
        f"BRL {row['total_revenue']:,.2f}",
        va="center",
        ha="right",
        fontsize=9.5
    )

sns.despine(ax=ax1[0], top=True, right=True)
sns.despine(ax=ax1[1], top=True, left=True)
plt.tight_layout()
st.pyplot(fig1)

st.divider()

# ==============================================================================
# VISUALISASI 2: NEGARA BAGIAN TERBANYAK & PERSEBARAN PELANGGAN PER STATE
# ==============================================================================
st.subheader(f"2. Persebaran Jumlah Pelanggan per Negara Bagian ({period_label})")

cust_by_state = (
    filtered_df.groupby("customer_state", as_index=False)
    .agg(unique_customers=("customer_unique_id", "nunique"))
    .sort_values(by="unique_customers", ascending=False)
    .reset_index(drop=True)
)

total_cust = cust_by_state["unique_customers"].sum()
cust_by_state["share (%)"] = (cust_by_state["unique_customers"] / total_cust * 100).round(2)

fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

top_10_states = cust_by_state.head(10).reset_index(drop=True)
top_state_name = top_10_states.iloc[0]["customer_state"]
colors_top_state = ["#1f77b4" if st_name == top_state_name else "#aec7e8" for st_name in top_10_states["customer_state"]]

sns.barplot(
    x="unique_customers",
    y="customer_state",
    data=top_10_states,
    palette=colors_top_state,
    hue="customer_state",
    legend=False,
    ax=ax2[0]
)
ax2[0].set_title("Top 10 Negara Bagian dengan Pelanggan Terbanyak", fontsize=13, fontweight="bold")
ax2[0].set_xlabel("Jumlah Pelanggan Unik")
ax2[0].set_ylabel("Negara Bagian (State)")
ax2[0].set_xlim(0, top_10_states["unique_customers"].max() * 1.30)

for idx, row in top_10_states.iterrows():
    ax2[0].text(
        row["unique_customers"] + (top_10_states["unique_customers"].max() * 0.02),
        idx,
        f"{row['unique_customers']:,} ({row['share (%)']}%)",
        va="center",
        fontsize=9.5
    )

all_state_colors = ["#1f77b4" if st_name == top_state_name else "#7f9eb2" for st_name in cust_by_state["customer_state"]]
sns.barplot(
    x="customer_state",
    y="unique_customers",
    data=cust_by_state,
    palette=all_state_colors,
    hue="customer_state",
    legend=False,
    ax=ax2[1]
)
ax2[1].set_title("Persebaran Pelanggan di Seluruh Negara Bagian", fontsize=13, fontweight="bold")
ax2[1].set_xlabel("Negara Bagian (State)")
ax2[1].set_ylabel("Jumlah Pelanggan Unik")
ax2[1].tick_params(axis="x", rotation=45)

sns.despine(ax=ax2[0], top=True, right=True)
sns.despine(ax=ax2[1], top=True, right=True)
plt.tight_layout()
st.pyplot(fig2)

st.divider()

# ==============================================================================
# VISUALISASI 3: ANALISIS LANJUTAN (RFM SEGMENTATION)
# ==============================================================================
st.subheader(f"3. Analisis Lanjutan: Segmentasi Pelanggan RFM ({period_label})")

recent_date = filtered_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm_df = filtered_df.groupby("customer_unique_id", as_index=False).agg(
    recency=("order_purchase_timestamp", lambda x: (recent_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
)

rfm_df["r_score"] = pd.qcut(rfm_df["recency"].rank(method="first"), q=4, labels=[4, 3, 2, 1]).astype(int)
rfm_df["f_score"] = rfm_df["frequency"].apply(lambda x: 4 if x >= 3 else (3 if x == 2 else 1))
rfm_df["m_score"] = pd.qcut(rfm_df["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)

def categorize_rfm(row):
    if row["r_score"] >= 3 and row["f_score"] >= 3 and row["m_score"] >= 3:
        return "Champions"
    elif row["f_score"] >= 3:
        return "Loyal Customers"
    elif row["r_score"] >= 3 and row["m_score"] >= 3:
        return "Potential Loyalists"
    elif row["r_score"] >= 3:
        return "Recent Customers"
    else:
        return "At Risk / Hibernating"

rfm_df["segment"] = rfm_df.apply(categorize_rfm, axis=1)

rfm_summary = (
    rfm_df.groupby("segment", as_index=False)
    .agg(
        customer_count=("customer_unique_id", "count"),
        avg_monetary=("monetary", "mean")
    )
    .sort_values(by="customer_count", ascending=False)
    .reset_index(drop=True)
)
rfm_summary["share (%)"] = (rfm_summary["customer_count"] / rfm_summary["customer_count"].sum() * 100).round(2)

fig3, ax3 = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))
seg_colors = ["#1f77b4" if i == 0 else "#aec7e8" for i in range(len(rfm_summary))]

sns.barplot(
    x="customer_count",
    y="segment",
    data=rfm_summary,
    palette=seg_colors,
    hue="segment",
    legend=False,
    ax=ax3[0]
)
ax3[0].set_title("Jumlah Pelanggan per Segmen RFM", fontsize=13, fontweight="bold")
ax3[0].set_xlabel("Jumlah Pelanggan Unik")
ax3[0].set_ylabel(None)
ax3[0].set_xlim(0, rfm_summary["customer_count"].max() * 1.30)

for idx, row in rfm_summary.iterrows():
    ax3[0].text(
        row["customer_count"] + (rfm_summary["customer_count"].max() * 0.02),
        idx,
        f"{row['customer_count']:,} ({row['share (%)']}%)",
        va="center",
        fontsize=9.5
    )

rfm_mon_sorted = rfm_summary.sort_values(by="avg_monetary", ascending=False).reset_index(drop=True)
sns.barplot(
    x="avg_monetary",
    y="segment",
    data=rfm_mon_sorted,
    palette="Blues_r",
    hue="segment",
    legend=False,
    ax=ax3[1]
)
ax3[1].set_title("Rata-Rata Pengeluaran (Monetary) per Segmen RFM", fontsize=13, fontweight="bold")
ax3[1].set_xlabel("Rata-Rata Monetary (BRL)")
ax3[1].set_ylabel(None)
ax3[1].set_xlim(0, rfm_mon_sorted["avg_monetary"].max() * 1.28)

for idx, row in rfm_mon_sorted.iterrows():
    ax3[1].text(
        row["avg_monetary"] + (rfm_mon_sorted["avg_monetary"].max() * 0.02),
        idx,
        f"BRL {row['avg_monetary']:,.2f}",
        va="center",
        fontsize=9.5
    )

sns.despine(ax=ax3[0], top=True, right=True)
sns.despine(ax=ax3[1], top=True, right=True)
plt.tight_layout()
st.pyplot(fig3)