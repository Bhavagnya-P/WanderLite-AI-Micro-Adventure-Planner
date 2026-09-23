import streamlit as st
if "change_mode" not in st.session_state:
    st.session_state.change_mode = None
if "generate_adventure" not in st.session_state:
    st.session_state.generate_adventure = False
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
def format_time(minutes):
    minutes = round(minutes)
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0 and remaining_minutes > 0:
        return f"{hours} hr {remaining_minutes} min"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{remaining_minutes} min"
def estimate_visit_time(place_type):
    time_map = {
        "park": 45,
        "garden": 30,
        "viewpoint": 30,
        "library": 60,
        "museum": 120,
        "gallery": 60,
        "attraction": 60,
        "cafe": 60,
        "restaurant": 90,
        "bookstore": 60,
        "zoo": 180,
        "theme_park": 240
    }

    return time_map.get(place_type, 45)
def estimate_cost(place_type):
    cost_map = {
        "park": 0,
        "garden": 0,
        "viewpoint": 40,
        "library": 0,
        "museum": 150,
        "gallery": 100,
        "attraction": 150,
        "cafe": 600,
        "restaurant": 400,
        "bookstore": 400,
        "zoo": 400,
        "theme_park": 1000
    }
    return cost_map.get(place_type, 100)
def estimate_transport_cost(distance, transport):
    if transport == "Walking":
        return 0
    elif transport == "Metro":
        return 70
    elif transport == "Bus":
        return 50
    elif transport == "Bike / Car":
        return distance * 8
    elif transport == "Cab":
        return distance * 20
    return 0
from places import search_places, get_location_coordinates, calculate_distance
from llm import generate_itinerary
load_dotenv()
st.set_page_config(
    page_title="WanderLite",
    page_icon="🧭"
)
st.title("🧭 WanderLite")
st.subheader("Turn your free time into a tiny adventure.")
st.write(
    "Tell us what you're looking for, and we'll create "
    "a short adventure around you."
)
location = st.text_input(
    "📍 Where are you?",
    placeholder="e.g., Hyderabad"
)
time_available = st.slider(
    "⏱️ How much time do you have?",
    min_value=1,
    max_value=8,
    value=3,
    step=1
)
start_time = st.time_input(
    "🕐 What time would you like to start?")
budget = st.number_input(
    "💰 What's your budget? (₹)",
    min_value=0,
    value=500,
    step=50
)
interests = st.multiselect(
    "✨ What are you in the mood for?",
    [
        "Nature",
        "Food",
        "Art",
        "History",
        "Books",
        "Photography",
        "Adventure",
        "Quiet",
        "Social"
    ]
)
company = st.selectbox(
    "👥 Who are you going with?",
    [
        "Alone",
        "Friends",
        "Couple",
        "Family"
    ]
)
transport = st.selectbox(
    "🚶 How will you travel?",
    [
        "Walking",
        "Metro",
        "Bus",
        "Bike / Car",
        "Cab"
    ]
)
if st.button("✨ Create My Adventure"):
    st.session_state.generate_adventure = True
    st.session_state.change_mode = None
if st.session_state.generate_adventure:    
    if not location:
        st.warning("Please enter a location first.")
    elif not interests:
        st.warning("Please select at least one interest.")
    else:
        if st.session_state.change_mode == "cheaper":
            budget = budget * 0.80
        elif st.session_state.change_mode == "less_time":
            time_available = max(1, time_available - 0.5)
        elif st.session_state.change_mode == "nature":
            if "Nature" not in interests:
                interests = interests + ["Nature"]
        elif st.session_state.change_mode == "food":
            if "Food" not in interests:
                interests = interests + ["Food"]
        start_lat, start_lon = get_location_coordinates(location)
        if start_lat is None or start_lon is None:
            st.error("Could not find the starting location. Please try another location.")
            st.stop()
        total_minutes = time_available * 60
        travel_time_limit = total_minutes * 0.40
        interest_text = " and ".join(interests)
        interest_categories = {
            "Nature": ["parks", "gardens", "viewpoints"],
            "Food": ["cafes", "restaurants"],
            "Art": ["art galleries", "museums"],
            "History": ["museums", "historic sites"],
            "Books": ["libraries", "bookstores"],
            "Photography": ["viewpoints", "tourist attractions"],
            "Adventure": ["tourist attractions", "recreation"],
            "Quiet": ["parks", "gardens", "libraries"],
            "Social": ["cafes", "restaurants"]
        }
        queries = []
        for interest in interests:
            if interest in interest_categories:
                queries.extend(
                    interest_categories[interest]
                )
        queries = list(set(queries))
        results = []
        for query in queries:
            places = search_places(
                [query],
                location
            )
            results.extend(places)
        st.subheader("🗺️ Your Micro-Adventure")
        if results:
            st.write(
                f"We found {len(results)} places and built "
                f"a plan around your available time and budget."
            )
            nearby_places = []
            for place in results:
                place_type = place.get("type", "")
                place_class = place.get("class", "")
                allowed_types = []
                for interest in interests:
                    if interest == "Nature":
                        allowed_types.extend([
                            "park",
                            "garden",
                            "viewpoint"
                        ])
                    elif interest == "Food":
                        allowed_types.extend([
                            "cafe",
                            "restaurant"
                        ])
                    elif interest == "Art":
                        allowed_types.extend([
                            "museum",
                            "gallery"
                        ])
                    elif interest == "History":
                        allowed_types.extend([
                            "museum",
                            "attraction"
                        ])
                    elif interest == "Books":
                        allowed_types.extend([
                            "library",
                            "bookstore"
                        ])
                    elif interest == "Photography":
                        allowed_types.extend([
                            "viewpoint",
                            "attraction"
                        ])
                    elif interest == "Adventure":
                        allowed_types.extend([
                            "attraction",
                            "theme_park",
                            "zoo"
                        ])
                    elif interest == "Quiet":
                            allowed_types.extend([
                            "park",
                            "garden",
                            "library"
                        ])
                    elif interest == "Social":
                        allowed_types.extend([
                            "cafe",
                            "restaurant"
                        ])
                if place_type not in allowed_types:
                    continue
                name = place.get(
                    "display_name",
                    "Unknown place"
                )
                place_type = place.get("type", "")
                estimated_cost = estimate_cost(place_type)
                visit_time = estimate_visit_time(place_type)
                matched_interests = []
                for interest in interests:
                    if interest == "Nature" and place_type in [
                        "park", "garden", "viewpoint"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Food" and place_type in [
                        "cafe", "restaurant"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Art" and place_type in [
                        "museum", "gallery"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "History" and place_type in [
                        "museum", "attraction"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Books" and place_type in [
                        "library", "bookstore"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Photography" and place_type in [
                        "viewpoint", "attraction"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Adventure" and place_type in [
                        "attraction", "theme_park", "zoo"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Quiet" and place_type in [
                        "park", "garden", "library"
                    ]:
                        matched_interests.append(interest)
                    elif interest == "Social" and place_type in [
                        "cafe", "restaurant"
                    ]:
                        matched_interests.append(interest)
                    address = place.get(
                    "display_name",
                    "Address unavailable"
                )
                latitude = place.get("lat")
                longitude = place.get("lon")
                if latitude is not None:
                    latitude = float(latitude)
                if longitude is not None:
                    longitude = float(longitude)
                if latitude is None or longitude is None:
                    continue
                distance = calculate_distance(
                    start_lat,
                    start_lon,
                    latitude,
                    longitude
                )
                transport_cost = estimate_transport_cost(
                    distance,
                    transport
                )
                if transport == "Walking":
                    speed = 4
                elif transport == "Metro":
                    speed = 20
                elif transport == "Bus":
                    speed = 15
                elif transport == "Bike / Car":
                    speed = 25
                else:
                    speed = 25
                travel_time = (distance / speed) * 60
                if travel_time > travel_time_limit:
                    continue
                nearby_places.append({
                "name": name,
                "address": address,
                "distance": distance,
                "travel_time": travel_time,
                "estimated_cost": estimated_cost,
                "transport_cost": transport_cost,
                "visit_time": visit_time,
                "matched_interests": matched_interests,
                "latitude": latitude,
                "longitude": longitude
            })
            nearby_places.sort(key=lambda place: place["distance"])
            selected_places = []
            current_itinerary_minutes = 0
            current_cost = 0
            covered_interests = set()
            previous_lat = start_lat
            previous_lon = start_lon
            for interest in interests:
                for place in nearby_places:
                    if interest not in place["matched_interests"]:
                        continue
                    if place in selected_places:
                        continue
                    route_distance = calculate_distance(
                        previous_lat,
                        previous_lon,
                        place["latitude"],
                        place["longitude"]
                    )
                    route_time = (route_distance / speed) * 60
                    transport_cost = estimate_transport_cost(
                        route_distance,
                        transport
                    )
                    return_distance = calculate_distance(
                        place["latitude"],
                        place["longitude"],
                        start_lat,
                        start_lon
                    )
                    return_time = (return_distance / speed) * 60
                    visit_time = place["visit_time"]
                    estimated_total_time = (current_itinerary_minutes + route_time + visit_time + return_time)
                    transport_cost = estimate_transport_cost(
                        route_distance,
                        transport
                    )
                    return_transport_cost = estimate_transport_cost(
                        return_distance,
                        transport
                    )
                    estimated_total_cost = (current_cost + place["estimated_cost"] + transport_cost + return_transport_cost)
                    if estimated_total_time > total_minutes:
                        continue
                    if estimated_total_cost > budget:
                        continue
                    selected_places.append(place)
                    current_itinerary_minutes += (
                        route_time + visit_time
                    )
                    current_cost += (place["estimated_cost"] + transport_cost)
                    covered_interests.add(interest)
                    previous_lat = place["latitude"]
                    previous_lon = place["longitude"]
                    break
            for place in nearby_places:
                if place in selected_places:
                    continue
                route_distance = calculate_distance(
                    previous_lat,
                    previous_lon,
                    place["latitude"],
                    place["longitude"]
                )
                route_time = (route_distance / speed) * 60
                transport_cost = estimate_transport_cost(
                    route_distance,
                    transport
                )
                return_distance = calculate_distance(
                    place["latitude"],
                    place["longitude"],
                    start_lat,
                    start_lon
                )
                return_time = (return_distance / speed) * 60
                visit_time = place["visit_time"]
                transport_cost = estimate_transport_cost(
                    route_distance,
                    transport
                )
                return_transport_cost = estimate_transport_cost(
                    return_distance,
                    transport
                )
                estimated_total_time = (current_itinerary_minutes + route_time + visit_time + return_time)
                estimated_total_cost = (current_cost + place["estimated_cost"] + transport_cost + return_transport_cost)
                if estimated_total_time > total_minutes:
                    continue
                if estimated_total_cost > budget:
                    continue
                selected_places.append(place)
                current_itinerary_minutes += (route_time + visit_time)
                current_cost += (place["estimated_cost"] + transport_cost)
                previous_lat = place["latitude"]
                previous_lon = place["longitude"]
            total_adventure_time = 0
            total_adventure_cost = 0
            previous_lat = start_lat
            previous_lon = start_lon
            current_time = datetime.combine(
                datetime.today(),
                start_time
            )
            for place in selected_places:
                route_distance = calculate_distance(
                    previous_lat,
                    previous_lon,
                    place["latitude"],
                    place["longitude"]
                )
                route_time = (route_distance / speed) * 60
                transport_cost = estimate_transport_cost(
                    route_distance,
                    transport
                )
                arrival_time = current_time + timedelta(minutes=route_time)
                departure_time = arrival_time + timedelta(minutes=place["visit_time"])
                total_adventure_time += route_time
                total_adventure_time += place["visit_time"]
                total_adventure_cost += (place["estimated_cost"] + transport_cost)
                st.markdown(
                    f"""
                    ### 📍 {place['name']}
                    🕐 **Arrive:** {arrival_time.strftime("%I:%M %p")}  
                    ⏳ **Explore for:** {place['visit_time']} min  
                    🕑 **Leave:** {departure_time.strftime("%I:%M %p")}  
                    📏 **Distance:** {route_distance:.2f} km  
                    💰 **Activity:** ₹{place['estimated_cost']}  
                    🚗 **Transport:** ₹{transport_cost:.0f}
                    """ 
                )
                st.markdown("---")
                current_time = departure_time
                previous_lat = place["latitude"]
                previous_lon = place["longitude"]
            if selected_places:
                return_distance = calculate_distance(
                    previous_lat,
                    previous_lon,
                    start_lat,
                    start_lon
                )
                return_time = (return_distance / speed) * 60
                total_adventure_time += return_time
                return_transport_cost = estimate_transport_cost(
                    return_distance, 
                    transport
                )
                total_adventure_cost += return_transport_cost
                if (total_adventure_time <= total_minutes and total_adventure_cost <= budget):
                    st.markdown("---")
                    st.subheader("🤖 Your AI-Planned Adventure")
                    itinerary = generate_itinerary(
                        places=selected_places,
                        location=location,
                        interests=interests,
                        company=company,
                        transport=transport
                    )
                    st.markdown(itinerary)
                    st.markdown("---")
                    st.write("---")
                    st.write(
                        f"🕒 **Estimated total adventure time: "
                        f"{format_time(total_adventure_time)}**"
                    )
                    st.write(f"💰 **Estimated total cost: ₹{total_adventure_cost:.0f}**")
                    st.success(
                        f"✨ Your adventure fits within your "
                        f"{time_available}-hour time limit and ₹{budget} budget!"
                    )
                    st.markdown("---")
                    st.subheader("🔄 Change My Adventure")
                    st.write("Want to tweak your adventure? Choose an option below.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💰 Make it cheaper"):
                            st.session_state.change_mode = "cheaper"
                            st.rerun()
                        if st.button("🌿 More nature"):
                            st.session_state.change_mode = "nature"
                            st.rerun()
                    with col2:
                        if st.button("⏱️ I have less time"):
                            st.session_state.change_mode = "less_time"
                            st.rerun()
                        if st.button("🍴 More food"):
                            st.session_state.change_mode = "food"
                            st.rerun()
        else:
            st.info("No places found.")