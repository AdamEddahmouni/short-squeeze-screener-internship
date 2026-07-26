import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.finviz_api import fetch_finviz_data
from core.filters import apply_filters

def main():
    print("Fetching Finviz data...")
    try:
        df = fetch_finviz_data()
        print(f"✅ Pulled {len(df)} rows from Finviz Elite")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return

    print("Applying short squeeze filters...")
    filtered = apply_filters(df)

    if filtered.empty:
        print("⚠️ No stocks matched your short squeeze criteria.")
    else:
        print(f"✅ {len(filtered)} stock(s) passed the filter:")
        print(filtered[["Ticker", "Price", "Change", "Rel Volume", "Float", "Short Float"]].head())

if __name__ == "__main__":
    main()