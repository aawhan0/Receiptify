import streamlit as st
import os
import re
import pandas as pd
from utils.ocr import extract_text
from utils.categorizer import categorize
from utils.storage import save_expense

st.set_page_config(page_title="Receipt Scanner", layout="wide")

# Sidebar navigation
st.sidebar.header("Receiptify")
section = st.sidebar.radio("Go to", ["Upload Receipt", "Batch Process", "Summary"])

csv_path = "data/receipts.csv"

if section == "Upload Receipt":
    st.title("Upload a New Receipt")
    uploaded_file = st.file_uploader("Upload your receipt", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(file_path, use_container_width=True)
        text = extract_text(file_path)
        st.text_area("Extracted Text", text, height=150)
        amount_match = re.search(r'(\d+[.,]?\d+)', text)
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        amount = amount_match.group(1) if amount_match else "Not Found"
        date = date_match.group(1) if date_match else "Not Found"
        store = text.strip().split("\n")[0]
        category = categorize(text)
        st.markdown(f"**Store:** {store}  \n**Date:** {date}  \n**Amount:** {amount}  \n**Category:** {category}")
        if st.button("Save to Tracker"):
            save_expense(date, store, amount, category)
            st.success("Receipt saved!")

elif section == "Batch Process":
    st.title("Batch Process Receipts")
    upload_images_dir = os.path.join("uploads", "images")
    if st.button("Process All in Uploads/Images"):
        if not os.path.exists(upload_images_dir) or not any(
            f.lower().endswith(('png', 'jpg', 'jpeg')) for f in os.listdir(upload_images_dir)):
            st.warning("No receipt images found.")
        else:
            files = [f for f in os.listdir(upload_images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            progress_bar = st.progress(0)
            results = []
            for idx, filename in enumerate(files):
                file_path = os.path.join(upload_images_dir, filename)
                text = extract_text(file_path)
                amount_match = re.search(r'(\d+[.,]?\d+)', text)
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
                amount = amount_match.group(1) if amount_match else "Not Found"
                date = date_match.group(1) if date_match else "Not Found"
                store = text.strip().split("\n")[0]
                category = categorize(text)
                save_expense(date, store, amount, category)
                results.append({"Filename": filename, "Store": store, "Date": date, "Amount": amount, "Category": category})
                progress_bar.progress((idx + 1) / len(files))
            st.success(f"Processed and saved {len(files)} receipts.")
            st.dataframe(pd.DataFrame(results))

elif section == "Summary":
    st.title("📊 Expense Summary Dashboard")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path)
        st.metric("Total Spent", f"₹{df['Amount'].replace('Not Found', 0).astype(float).sum():.2f}")
        st.metric("Receipts Processed", len(df))
        col1, col2, col3 = st.columns(3)
        col1.metric("Top Category", df['Category'].mode()[0])
        col2.metric("Biggest Store", df['Store'].value_counts().idxmax())
        col3.metric("Avg. Transaction", f"₹{df['Amount'].replace('Not Found', 0).astype(float).mean():.2f}")
        st.bar_chart(df.groupby("Category")["Amount"].apply(
            lambda x: pd.to_numeric(x, errors='coerce').sum()))
        st.dataframe(df)
    else:
        st.warning("No expense data found.")
