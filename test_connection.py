import pandas as pd

# -------------------------------------------------------------
# PASTE YOUR PUBLISHED CSV URL INSIDE THE QUOTES BELOW:
# -------------------------------------------------------------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQjudyA04X-lQ2V-H2UB_AjdhAO2oPxqhC5FXEU7Yx5dT_7ks7AeNa8-vS8WWgc8tUo7rB0IKBXokl1/pub?gid=305238043&single=true&output=csv"


def test_sheet_connection():
    print("Connecting to Google Sheets via live link...")

    try:
        # pd.read_csv downloads the live spreadsheet data directly into a table
        df = pd.read_csv(CSV_URL)

        print("\n Connection Successful!")
        print("--------------------------------------------------")
        print(f"Total records (rows) found: {len(df)}")
        print(f"Total columns found: {len(df.columns)}")
        print("--------------------------------------------------")

        # Show the column names
        print("\nColumns detected in your sheet:")
        for col in df.columns:
            print(f" - {col}")

        # Show the first 5 customer rows
        print("\nPreview of first 5 rows:")
        sample_cols = [
            col
            for col in [
                "Assign Person",
                "Follow Up Date",
                "Cust Name",
                "EMI Status",
                "Lock Status",
            ]
            if col in df.columns
        ]
        if sample_cols:
            print(df[sample_cols].head(5))
        else:
            print(df.head(5))

    except Exception as error:
        print("\n Connection Failed!")
        print("Error details:", error)


if __name__ == "__main__":
    test_sheet_connection()