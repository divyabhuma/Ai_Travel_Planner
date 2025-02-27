import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# Configure API Key
API_KEY = "AIzaSyDX-UyxgsUZZiVBjfe4GFPxXOXEVjx_igQ"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

def get_travel_recommendations(source, destination, travel_date):
    """
    Fetches travel recommendations using Gemini AI and returns structured JSON data.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    query = f"""
    You are a smart travel assistant. Suggest travel options from {source} to {destination} for {travel_date}.
    Respond ONLY in JSON format as follows:
    {{
        "flights": [{{"airline": "Airline Name", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "trains": [{{"name": "Train Name", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "buses": [{{"operator": "Bus Operator", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "cabs": [{{"cost": Amount, "duration": "Time"}}]
    }}
    """
    try:
        response = model.generate_content(query)
        response_text = response.text.strip() if hasattr(response, 'text') else ""
        
        json_start = response_text.find("{")
        json_end = response_text.rfind("}")
        
        if json_start != -1 and json_end != -1:
            return json.loads(response_text[json_start:json_end+1])
        return {"error": "Invalid AI response format."}
    except json.JSONDecodeError:
        return {"error": "Error processing JSON response."}
    except Exception as e:
        return {"error": str(e)}

def generate_travel_summary(travel_info):
    """
    Generates a summary highlighting the best travel options.
    """
    summary = "### 🔹 Top Travel Options:\n"
    choices = []
    
    for mode in ["flights", "trains", "buses", "cabs"]:
        if mode in travel_info:
            choices.extend([(mode.capitalize(), option["cost"]) for option in travel_info[mode]])
    
    if choices:
        cheapest = min(choices, key=lambda x: x[1])
        summary += f"✔ Most Affordable: {cheapest[0]} at ₹{cheapest[1]}\n"
    
    if "flights" in travel_info:
        summary += "⚡ Fastest: Flights (usually 1-2 hours).\n"
    
    return summary

# Streamlit UI
st.title("🌍 AI Travel Planner")
st.write("Plan your trip efficiently with AI recommendations.")

origin = st.text_input("Enter Departure City")
destination = st.text_input("Enter Destination City")
date = st.date_input("Select Travel Date", min_value=datetime.today())

if st.button("Find Travel Options", use_container_width=True):
    if origin and destination:
        travel_data = get_travel_recommendations(origin, destination, date.strftime("%Y-%m-%d"))
        
        if "error" in travel_data:
            st.error(travel_data["error"])
        else:
            st.write(f"### Travel Options from {origin} to {destination} on {date.strftime('%B %d, %Y')}")
            st.write("---")
            st.markdown(generate_travel_summary(travel_data))
            
            for mode, emoji in zip(["flights", "trains", "buses", "cabs"], ["✈", "🚆", "🚌", "🚖"]):
                if travel_data.get(mode):
                    st.subheader(f"{emoji} {mode.capitalize()}")
                    for option in travel_data[mode]:
                        details = " - ".join([f"{key.capitalize()}: {value}" for key, value in option.items()])
                        st.markdown(f"- {details}")
    else:
        st.error("Please enter both departure and destination cities.")