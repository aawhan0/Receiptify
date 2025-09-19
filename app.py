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

    # Regex for amount and date
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

    if st.button("📊 Show Expense Summary"):
        import pandas as pd
        if os.path.exists("data/expenses.csv"):
            df = pd.read_csv("data/expenses.csv")
            st.dataframe(df)
            st.bar_chart(df.groupby("Category")["Amount"].sum())
        else:
            st.warning("No expense data found.")
