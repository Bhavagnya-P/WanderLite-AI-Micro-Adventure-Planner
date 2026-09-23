import requests
import math
import time
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "WanderLite/1.0"
}
def get_location_coordinates(location):
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            results = response.json()
            if results:
                return (
                    float(results[0]["lat"]),
                    float(results[0]["lon"])
                )
        print("Location search error:", response.status_code)
    except requests.RequestException as e:
        print("Location request failed:", e)
    return None, None
def search_places(queries, city=None):
    all_results = []
    for query in queries:
        if city:
            search_query = f"{query} in {city}"
        else:
            search_query = query
        params = {
            "q": search_query,
            "format": "json",
            "limit": 10,
            "addressdetails": 1
        }
        try:
            response = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=HEADERS,
                timeout=10
            )
            print(
                "Searching:",
                search_query,
                "| Status:",
                response.status_code
            )
            if response.status_code == 200:
                results = response.json()
                excluded_words = [
                    "ward",
                    "neighbourhood",
                    "neighborhood"
                ]
                for place in results:
                    all_results.append(place)                    
                    #display_name = place.get(
                    #    "display_name",
                    #    ""
                    #).lower()
                    #if any(
                    #    word in display_name
                    #    for word in excluded_words
                    #):
                    #    continue
            else:
                print(
                    "Place search error:",
                    response.status_code
                )
        except requests.RequestException as e:
            print(
                "Place request failed:",
                repr(e)
            )
        time.sleep(1)
    return all_results
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )
    return R * c
if __name__ == "__main__":
    print("Testing WanderLite location search...\n")
    city = input(
        "Enter a city to test: "
    ).strip()
    latitude, longitude = get_location_coordinates(city)
    print("\nLocation:", city)
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    if latitude is not None and longitude is not None:
        print("\nSearching for parks...\n")
        places = search_places(
            ["parks", "gardens", "viewpoints"],
            city
        )
        print(
            "Places found:",
            len(places)
        )
        for place in places:
            name = place.get(
                "display_name",
                "Unnamed place"
            )
            place_lat = float(
                place["lat"]
            )
            place_lon = float(
                place["lon"]
            )
            distance = calculate_distance(
                latitude,
                longitude,
                place_lat,
                place_lon
            )
            print(
                f"- {name} "
                f"({distance:.2f} km away)"
            )
            time.sleep(1)