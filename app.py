import streamlit as st
import os
import re
from utils.ocr import extract_text
from utils.categorizer import categorize
from utils.storage import save_expense

st.set_page_config(page_title="Receipt Scanner", layout="centered")

st.title("🧾 Receipt Scanner with Expense Categorizer")

uploaded_file = st.file_uploader("Upload your receipt image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(file_path, caption="Uploaded Receipt", use_column_width=True)

    st.subheader("🔍 Extracting Information...")
    text = extract_text(file_path)
    st.text_area("Extracted Text", text, height=200)

    amount_match = re.search(r'(\d+[.,]?\d+)', text)
    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)

    amount = amount_match.group(1) if amount_match else "Not Found"
    date = date_match.group(1) if date_match else "Not Found"
    store = text.strip().split("\n")[0]

    category = categorize(text)

    st.markdown(f"""
    **🛒 Store:** {store}  
    **📅 Date:** {date}  
    **💰 Amount:** {amount}  
    **🏷️ Category:** {category}
    """)

    if st.button("💾 Save to Tracker"):
        save_expense(date, store, amount, category)
        st.success("Receipt saved to tracker!")

# New batch processing section with uploads/images path
st.markdown("---")
st.header("📂 Batch Process Receipts from Uploads Folder")

if st.button("⚡ Process All Receipts in Uploads Folder"):
    upload_images_dir = os.path.join("uploads", "images")
    if not os.path.exists(upload_images_dir) or len(os.listdir(upload_images_dir)) == 0:
        st.warning(f"No files found in {upload_images_dir}.")
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
        st.dataframe(results)

# Show expense summary as before
st.markdown("---")
if st.button("📊 Show Expense Summary"):
    import pandas as pd
    csv_path = "data/expenses.csv"
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path)
        st.dataframe(df)
        st.bar_chart(df.groupby("Category")["Amount"].sum())
    else:
        st.warning("No expense data found or file is empty.")
