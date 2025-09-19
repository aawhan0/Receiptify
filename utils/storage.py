import pandas as pd
import os

def save_expense(date, store, amount, category, csv_path="data/expenses.csv"):
    entry = {
        "Date": date,
        "Store": store,
        "Amount": amount,
        "Category": category
    }

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    else:
        df = pd.DataFrame([entry])

    df.to_csv(csv_path, index=False)
