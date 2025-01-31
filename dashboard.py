import pandas as pd
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

import matplotlib.pyplot as plt

sns.set_theme(style="dark")

# Load cleaned data
final_df = pd.read_csv("./dataset/final_dataframe.csv", parse_dates=["order_purchase_timestamp"])


# Helper function to create various dataframes
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_purchase_timestamp").agg(
        {"order_id": "nunique", "payment_value": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True
    )

    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = (
        df.groupby("product_category_df_name_english")
        .order_item_id.sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_order_items_df


def create_bygender_df(df):
    bygender_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bygender_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return bygender_df


def create_byage_df(df):
    byage_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    byage_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return byage_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return bystate_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg(
        {
            "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
            "order_id": "nunique",
            "payment_value": "sum",
        }
    )
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


# Filter data
min_date = final_df["order_purchase_timestamp"].min()
max_date = final_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = final_df[
    (final_df["order_purchase_timestamp"] >= str(start_date))
    & (final_df["order_purchase_timestamp"] <= str(end_date))
]

# st.dataframe(main_df)

# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# plot number of daily orders (2021)
st.header("Proyek Analisis Data: E-Commerce Public Dataset")
st.subheader("Pesanan Harian")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Pesanan", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "AUD", locale="es_CO"
    )
    st.metric("Total Pendapatan", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9",
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)

# Product performance
st.subheader("Produk Terbaik & Terburuk")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="order_item_id",
    y="product_category_df_name_english",
    data=sum_order_items_df.head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[0].set_title("Produk Terbaik", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

sns.barplot(
    x="order_item_id",
    y="product_category_df_name_english",
    data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Terburuk", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=35)
ax[1].tick_params(axis="x", labelsize=30)

st.pyplot(fig)

# customer demographic
st.subheader("Demografi Pelanggan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y="customer_count",
        x="customer_state",
        data=bygender_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax,
    )
    ax.set_title("Jumlah Pelanggan per Negara Bagian", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="customer_count",
        x="customer_city",
        data=byage_df.sort_values(by="customer_city", ascending=False),
        palette=colors,
        ax=ax,
    )
    ax.set_title("Jumlah Pelanggan per Kota", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
colors = [
    "#90CAF9",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax,
)
ax.set_title("Jumlah Pelanggan per Negara Bagian", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)
st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Pelanggan Terbaik Berdasarkan Parameter RFM")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rata-rata Recency (hari)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Rata-rata Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale="es_CO")
    st.metric("Rata-rata Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency",
    x="customer_id",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("Berdasarkan Recency (hari)", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=35)

sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("Berdasarkan Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)

sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("Berdasarkan Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis="y", labelsize=30)
ax[2].tick_params(axis="x", labelsize=35)

st.pyplot(fig)

st.caption("Copyright © Mochamad Nurul Huda 2025")
