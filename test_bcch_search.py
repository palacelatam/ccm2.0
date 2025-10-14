import bcchapi
import pandas as pd

print("=" * 60)
print("BCCH API Test - Search Functionality")
print("=" * 60)

try:
    # Initialize client
    print("\n1. Initializing BCCH API client...")
    siete = bcchapi.Siete("ben.clark@palace.cl", "Baby3conny")
    print("   ✓ Client initialized")

    # Search for USD related series
    search_term = "Dólar observado"
    print(f"\n2. Searching for: '{search_term}'...")

    # The buscar method should return available series
    results = siete.buscar(search_term)

    print(f"\n3. Search results analysis:")
    print(f"   - Type: {type(results)}")

    if results is None:
        print("   ⚠️  No results returned")
    elif isinstance(results, pd.DataFrame):
        print(f"   - Shape: {results.shape}")
        print(f"   - Columns: {list(results.columns)}")
        print("\n   Results:")
        print(results)

        # If DataFrame has series codes as index or in a column
        if not results.empty:
            print("\n4. Available series codes:")

            # Check if index contains series codes
            if results.index.name and 'serie' in results.index.name.lower():
                for code in results.index:
                    print(f"   - {code}")

                # Try to fetch data for the first series
                first_code = results.index[0]
                print(f"\n5. Attempting to fetch data for: {first_code}")

                data = siete.cuadro(series=first_code)
                if data is not None:
                    print(f"   ✓ Data retrieved: {data.shape}")
                    print("\n   Sample data:")
                    print(data.head())

            # Check columns for series codes
            elif 'codigo' in [col.lower() for col in results.columns]:
                col_name = [col for col in results.columns if 'codigo' in col.lower()][0]
                for code in results[col_name]:
                    print(f"   - {code}")

            elif 'serie' in [col.lower() for col in results.columns]:
                col_name = [col for col in results.columns if 'serie' in col.lower()][0]
                for code in results[col_name]:
                    print(f"   - {code}")

    elif isinstance(results, list):
        print(f"   - Length: {len(results)}")
        print("\n   Results:")
        for i, item in enumerate(results[:5]):  # Show first 5 items
            print(f"   {i+1}. {item}")

    elif isinstance(results, dict):
        print(f"   - Keys: {list(results.keys())}")
        print("\n   Results:")
        for key, value in list(results.items())[:5]:  # Show first 5 items
            print(f"   {key}: {value}")

    else:
        print(f"   - Unexpected type: {type(results)}")
        print(f"   - String representation: {str(results)[:200]}")

    # Alternative: Try known series codes directly
    print("\n" + "=" * 60)
    print("Alternative: Using known series codes")
    print("=" * 60)

    known_codes = {
        "F073.TCO.PRE.Z.D": "Dólar observado (diario)",
        "F073.TCO.PRE.Z.M": "Dólar observado (mensual)",
        "F072.CLP.USD.N.O.D": "Tipo de cambio CLP/USD"
    }

    print("\nTrying known series codes:")
    for code, description in known_codes.items():
        print(f"\n   {code}: {description}")
        try:
            # Try to get just the latest value
            data = siete.cuadro(series=code, desde='2024-01-01', hasta='2024-01-31')
            if data is not None and not data.empty:
                print(f"      ✓ Data available - Shape: {data.shape}")
                if not data.empty:
                    latest = data.iloc[-1, 0] if len(data.columns) > 0 else 'N/A'
                    print(f"      Latest value: {latest}")
            else:
                print(f"      ⚠️  No data returned")
        except Exception as e:
            print(f"      ❌ Error: {e}")

except Exception as e:
    print(f"\n❌ Error occurred: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)