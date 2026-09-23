import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
def generate_itinerary(
    places,
    location,
    interests,
    company,
    transport
):
    place_details = []
    for place in places:
        place_details.append(
            f"""
Place: {place['name']}
Address: {place['address']}
Distance: {place['distance']:.2f} km
Travel time: {place['travel_time']:.0f} min
Activity cost: ₹{place['estimated_cost']}
Transport cost: ₹{place['transport_cost']:.0f}
Matched interests: {", ".join(place['matched_interests'])}
"""
        )
    place_details = "\n".join(place_details)
    prompt = f"""
You are WanderLite, an AI micro-adventure planner.

Create a short, practical and engaging itinerary using ONLY
the places and information provided below.

User details:
Location: {location}
Interests: {", ".join(interests)}
Company: {company}
Transport: {transport}

Verified places:
{place_details}

Important rules:
- Use ONLY the places provided.
- Do NOT invent places.
- Do NOT invent prices, distances or travel times.
- Do NOT add information that is not provided.
- Keep the itinerary realistic and concise.
- Make it feel personalised and fun.
- Organise the places in a logical order.
- Explain briefly why the suggested places match the user's interests.
"""
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return response.text
if __name__ == "__main__":

    result = generate_itinerary(
        places=[
            "Lumbini Park - 2 km away - 45 min visit - ₹0"
        ],
        location="Hyderabad",
        interests=["Nature", "Photography"],
        company="Friends",
        transport="Walking"
    )

    print("\nWanderLite AI Itinerary\n")
    print(result)