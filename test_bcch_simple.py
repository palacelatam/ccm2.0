import bcchapi
import pandas as pd
from datetime import datetime, timedelta

print("=" * 60)
print("BCCH API Test - Fetching USD Exchange Rate")
print("=" * 60)

try:
    # Initialize client
    print("\n1. Initializing BCCH API client...")
    siete = bcchapi.Siete("ben.clark@palace.cl", "Baby3conny")
    print("   ✓ Client initialized")

    # The series code for "Dólar observado" is typically F073.TCO.PRE.Z.D
    # This is the official USD/CLP exchange rate published by Chile's Central Bank
    series_code = "F073.TCO.PRE.Z.D"
    #series_code = "F073.PTC.PON.GBR.A"

    print(f"\n2. Fetching data for series: {series_code}")
    print("   (Dólar observado - USD/CLP exchange rate)")

    # Set date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print(f"\n3. Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Fetch the data using cuadro
    print("\n4. Fetching exchange rate data...")
    data = siete.cuadro(
        series=series_code,
        desde=start_date.strftime('%Y-%m-%d'),
        hasta=end_date.strftime('%Y-%m-%d')
    )

    print("\n5. Data retrieved successfully!")

    if data is not None and not data.empty:
        print(f"\n   Shape: {data.shape}")
        print(f"   Columns: {list(data.columns)}")
        print("\n   Last 5 exchange rates:")
        print(data.tail())

        # Get the most recent exchange rate
        latest_rate = data.iloc[-1, 0] if not data.empty else None
        if latest_rate:
            print(f"\n   Latest USD/CLP rate: {latest_rate}")
    else:
        print("\n   ⚠️  No data returned")

except Exception as e:
    print(f"\n❌ Error occurred: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)