import bcchapi
import logging

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

print("Initializing BCCH API client...")
# Incluyendo credenciales explícitamente
siete = bcchapi.Siete("ben.clark@palace.cl", "Baby3conny")
# O bien llamando a un archivo
# siete = bcchapi.Siete(file="credenciales.txt")

print("\nSearching for 'Dólar observado'...")
# Search returns results - let's capture them
search_results = siete.buscar("Dólar observado")

# Print search results to understand the structure
print(f"\nSearch results type: {type(search_results)}")
if search_results:
    print(f"Number of results: {len(search_results) if hasattr(search_results, '__len__') else 'N/A'}")
    print(f"Search results: {search_results}")

    # If search_results is a DataFrame or has series codes, extract them
    if hasattr(search_results, 'index'):
        print("\nAvailable series codes:")
        for idx in search_results.index:
            print(f"  - {idx}")

        # Try to get the first series code
        if len(search_results) > 0:
            first_series = search_results.index[0]
            print(f"\nUsing series: {first_series}")

            # Now call cuadro with the series
            print("\nFetching data for the series...")
            data = siete.cuadro(series=first_series)
            print(f"\nData retrieved: {data}")
    else:
        print("Search results don't have expected structure")
else:
    print("No results found")