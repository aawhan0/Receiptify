def categorize(text):
    categories = {
        "Food": ["restaurant", "cafe", "coffee", "burger", "pizza", "food"],
        "Transport": ["uber", "ola", "auto", "bus", "train", "cab"],
        "Shopping": ["amazon", "flipkart", "store", "mall"],
        "Groceries": ["grocery", "supermarket", "mart", "kirana"],
        "Medical": ["pharmacy", "chemist", "hospital", "clinic"],
    }

    text_lower = text.lower()

    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category

    return "Other"
