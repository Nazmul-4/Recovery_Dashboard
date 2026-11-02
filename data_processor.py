import pandas as pd

# -------------------------------------------------------------
# PASTE YOUR PUBLISHED CSV URL HERE:
# -------------------------------------------------------------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQjudyA04X-lQ2V-H2UB_AjdhAO2oPxqhC5FXEU7Yx5dT_7ks7AeNa8-vS8WWgc8tUo7rB0IKBXokl1/pub?gid=305238043&single=true&output=csv"


def load_and_clean_data(url: str) -> pd.DataFrame:
    """Fetch raw data from Google Sheets and clean whitespace/dates."""
    df = pd.read_csv(url)

    # Clean leading/trailing spaces from text columns
    string_cols = df.select_dtypes(include="object").columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()

    # Convert Follow Up Date to standard Date format (YYYY-MM-DD)
    df["Follow Up Date"] = pd.to_datetime(
        df["Follow Up Date"], errors="coerce"
    )

    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate the primary dashboard headline numbers."""
    total_cases = len(df)

    # A call is scheduled if 'Follow Up Date' is not blank/NaT
    scheduled_calls = df["Follow Up Date"].notna().sum()
    remaining_calls = total_cases - scheduled_calls

    # Locked vs Unlocked devices
    locked_count = (df["Lock Status"].str.lower() == "locked").sum()
    unlocked_count = (df["Lock Status"].str.lower() == "unlocked").sum()

    # Accounts with 3 or more EMIs paid
    target_emi_list = [
        "3 EMI Paid",
        "4 EMI Paid",
        "5 EMI Paid",
        "6 EMI Paid",
        "3 emi paid",
        "4 emi paid",
        "5 emi paid",
        "6 emi paid",
    ]
    late_stage_emi_count = df["EMI Status"].isin(target_emi_list).sum()

    return {
        "Total Cases": total_cases,
        "Total Scheduled Calls": scheduled_calls,
        "Remaining Calls": remaining_calls,
        "Locked Devices": locked_count,
        "Unlocked Devices": unlocked_count,
        "Total 3-6 EMI Paid": late_stage_emi_count,
    }


def get_agent_schedule_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Recreate the date-by-agent schedule grid from the original Excel sheet."""
    # Filter rows that have both a valid date and assigned person
    valid_data = df.dropna(subset=["Follow Up Date", "Assign Person"]).copy()
    valid_data = valid_data[valid_data["Assign Person"] != "nan"]

    # Pivot table / crosstab: Dates as rows, Agents as columns
    matrix = pd.crosstab(
        index=valid_data["Follow Up Date"].dt.strftime("%Y-%m-%d"),
        columns=valid_data["Assign Person"],
        margins=True,  # Adds 'Total' row and column automatically
        margins_name="Total",
    )

    return matrix


def get_emi_status_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count of accounts in each EMI bucket."""
    summary = (
        df["EMI Status"].value_counts(dropna=False).reset_index()
    )
    summary.columns = ["EMI Status", "Count"]
    return summary


# -------------------------------------------------------------
# Test the computations directly in the terminal
# -------------------------------------------------------------
if __name__ == "__main__":
    print("Fetching and processing sheet data...\n")
    data = load_and_clean_data(CSV_URL)

    # 1. Headline KPIs
    kpis = calculate_kpis(data)
    print("=" * 45)
    print("                 PORTFOLIO KPIS              ")
    print("=" * 45)
    for metric, value in kpis.items():
        print(f" {metric:<25} : {value:>6}")
    print("=" * 45 + "\n")

    # 2. EMI Distribution
    print("--- EMI Distribution ---")
    emi_summary = get_emi_status_summary(data)
    print(emi_summary.to_string(index=False))
    print("\n")

    # 3. Agent Schedule Grid
    print("--- Officer Follow-Up Schedule (First 8 Dates) ---")
    schedule = get_agent_schedule_matrix(data)
    print(schedule.head(8))