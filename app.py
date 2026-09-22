import streamlit as st
from utils.gemini import create_travel_plan 




# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


if "generating" not in st.session_state:
    st.session_state.generating = False

if "cancel_requested" not in st.session_state:
    st.session_state.cancel_requested = False

if "travel_plan" not in st.session_state:
    st.session_state.travel_plan = None


# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.block-container {
    max-width: 100%;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 1rem 0 2rem 0;
}

.hero h4 {
    font-size: clamp(2rem, 4vw, 3.5rem);
    margin-bottom: 0.4rem;
}

.hero p {
    font-size: 1.15rem;
    opacity: 0.7;
}

.card {
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 1rem;
}

.trip-stat {
    text-align: center;
    padding: 1rem;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.15);
}

.trip-stat-value {
    font-size: 1.3rem;
    font-weight: 700;
}

.trip-stat-label {
    font-size: 0.85rem;
    opacity: 0.65;
}

.day-card {
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 1rem;
}

.place-card {
    padding: 1.2rem;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 0.8rem;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HERO
# ==================================================

st.markdown("""
<div class="hero">

<h4>✈️ AI Travel Planner</h4>

<p>
Plan smarter. Travel better. Let AI build a trip around your
interests, budget and travel style.
</p>

</div>
""", unsafe_allow_html=True)


# ==================================================
# INPUT SECTION
# ==================================================

left, right = st.columns([1, 1], gap="large")


with left:

    st.subheader("🌍 Tell us about your trip")

    destination = st.text_input(
        "📍 Destination",
        placeholder="e.g. Manali, Goa, Jaipur..."
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("🗓️ Start date")

    with col2:
        end_date = st.date_input("🗓️ End date")

    col1, col2 = st.columns(2)

    with col1:
        travelers = st.number_input(
            "👥 Travelers",
            min_value=1,
            max_value=20,
            value=2
        )

    with col2:
        budget = st.number_input(
            "💰 Budget (₹)",
            min_value=1000,
            max_value=10000000,
            value=30000,
            step=1000
        )

    interests = st.multiselect(
        "❤️ What do you enjoy?",
        [
            "🏔️ Nature",
            "🧗 Adventure",
            "🍴 Food",
            "🏛️ History",
            "🎭 Culture",
            "🛍️ Shopping",
            "🌃 Nightlife",
            "📸 Photography",
            "🧘 Relaxation"
        ],
        placeholder="Choose your interests..."
    )

    travel_style = st.radio(
        "🎒 Travel style",
        [
            "💸 Budget",
            "🧳 Comfortable",
            "✨ Luxury"
        ],
        horizontal=True
    )

    generate = st.button(
        "✨ Generate My Travel Plan",
        type="primary",
        disabled=st.session_state.generating,
        key="generate_travel_plan"
)   
    if st.session_state.generating:
        cancel = st.button(
            "⛔ Cancel Generation",
            key="cancel_generation"
        )

        if cancel:
            st.session_state.cancel_requested = True
            st.session_state.generating = False
            st.warning("Generation cancelled.")
            st.rerun()


# ==================================================
# PREVIEW
# ==================================================

with right:

    st.subheader("🌍 Trip Preview")

    preview_destination = (
        destination
        if destination
        else "Your destination"
    )

    st.markdown(
        f"""
        <div class="card">

        <h2>📍 {preview_destination}</h2>

        <p>
        Your personalized AI travel experience.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "👥 Travelers",
            travelers
        )

    with c2:
        st.metric(
            "💰 Budget",
            f"₹{budget:,}"
        )

    st.write("")

    st.markdown("### ❤️ Interests")

    if interests:
        st.write(" ".join(interests))
    else:
        st.caption("Your interests will appear here.")

    st.markdown("### 🎒 Travel Style")

    st.info(travel_style)


# ==================================================
# GENERATE
# ==================================================

if generate:

    st.session_state.generating = True
    st.session_state.cancel_requested = False

    if not destination.strip():

        st.warning(
            "📍 Please enter a destination."
        )

        st.session_state.generating = False
        st.stop()

    if end_date < start_date:

        st.error(
            "🗓️ End date cannot be before start date."
        )

        st.session_state.generating = False
        st.stop()

    number_of_days = (
        end_date - start_date
    ).days + 1


    # ==================================================
    # GEMINI PROMPT
    # ==================================================

    prompt = f"""
You are an expert travel planner.

Create a personalized travel plan using this information:

Destination: {destination}

Start date: {start_date}

End date: {end_date}

Number of days: {number_of_days}

Number of travelers: {travelers}

Budget: ₹{budget}

Interests:
{", ".join(interests) if interests else "General sightseeing"}

Travel style:
{travel_style}


RETURN ONLY VALID JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations outside the JSON.

Use exactly this structure:

{{
    "summary": "Short description of the trip",

    "itinerary": [
        {{
            "day": 1,
            "title": "Day title",
            "morning": "Morning activities",
            "afternoon": "Afternoon activities",
            "evening": "Evening activities"
        }}
    ],

    "places": [
        {{
            "name": "Place name",
            "description": "Why visit this place",
            "best_time": "Best time to visit"
        }}
    ],

    "food": [
        {{
            "name": "Food or restaurant type",
            "description": "What to try"
        }}
    ],

    "packing": [
        "Item 1",
        "Item 2",
        "Item 3"
    ],

    "travel_advice": [
        "Advice 1",
        "Advice 2",
        "Advice 3"
    ],

    "budget": {{
        "accommodation": 0,
        "food": 0,
        "transport": 0,
        "activities": 0,
        "miscellaneous": 0,
        "total": 0
    }}
}}

Budget values must be approximate estimates in Indian Rupees.
"""


    # ==================================================
    # CALL GEMINI
    # ==================================================

    with st.spinner(
        "✨ Creating your personalized travel plan..."
    ):

        travel_plan = create_travel_plan(prompt)


    if st.session_state.cancel_requested:

        st.session_state.travel_plan = None

        st.info("⛔ Generation cancelled.")

    else:

        st.session_state.travel_plan = travel_plan


    st.session_state.generating = False


    # ==================================================
    # RESULT
    # ==================================================

    st.divider()

    st.header(
        f"✨ Your {destination} Travel Plan"
    )

    st.info(travel_plan["summary"])


    # ==================================================
    # TABS
    # ==================================================

    itinerary_tab, places_tab, food_tab, packing_tab, advice_tab, budget_tab = st.tabs(
        [
            "🗓️ Itinerary",
            "📍 Places",
            "🍴 Food",
            "🎒 Packing",
            "💡 Advice",
            "💰 Budget"
        ]
    )


    # ==================================================
    # ITINERARY
    # ==================================================

    with itinerary_tab:

        st.subheader("🗓️ Your Day-by-Day Itinerary")

        for day in travel_plan["itinerary"]:

            with st.expander(
                f"📅 Day {day['day']} — {day['title']}",
                expanded=(day["day"] == 1)
            ):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("### 🌅 Morning")
                    st.write(day["morning"])

                with col2:
                    st.markdown("### ☀️ Afternoon")
                    st.write(day["afternoon"])

                with col3:
                    st.markdown("### 🌆 Evening")
                    st.write(day["evening"])


    # ==================================================
    # PLACES
    # ==================================================

    with places_tab:

        for place in travel_plan["places"]:

            st.markdown(
                f"""
                <div class="place-card">

                <h3>📍 {place["name"]}</h3>

                <p>{place["description"]}</p>

                <small>
                🕐 Best time: {place["best_time"]}
                </small>

                </div>
                """,
                unsafe_allow_html=True
            )


    # ==================================================
    # FOOD
    # ==================================================

    with food_tab:

        for item in travel_plan["food"]:

            st.markdown(
                f"""
                <div class="place-card">

                <h3>🍴 {item["name"]}</h3>

                <p>{item["description"]}</p>

                </div>
                """,
                unsafe_allow_html=True
            )


    # ==================================================
    # PACKING
    # ==================================================

    with packing_tab:

        st.subheader("🎒 Packing Checklist")

        items = travel_plan["packing"]

        if items:

            st.caption(
                "Check items as you pack them."
            )

            checked_items = []

            for index, item in enumerate(items):

                checked = st.checkbox(
                    item,
                    key=f"packing_{index}"
                )

                if checked:
                    checked_items.append(item)

            total_items = len(items)
            packed_items = len(checked_items)

            progress = packed_items / total_items

            st.progress(
                progress,
                text=f"{packed_items}/{total_items} items packed"
            )

            if packed_items == total_items:
                st.success(
                    "🎉 You're fully packed!"
                )


    # ==================================================
    # TRAVEL ADVICE
    # ==================================================

    with advice_tab:

        st.subheader("💡 Useful Travel Advice")

        for advice in travel_plan["travel_advice"]:

            st.info(advice)


    # ==================================================
    # BUDGET
    # ==================================================

    with budget_tab:

        st.subheader("💰 Estimated Trip Budget")

        budget_data = travel_plan["budget"]

        total = budget_data["total"]

        st.metric(
            "💰 Estimated Total",
            f"₹{total:,}"
        )

        st.divider()

        categories = {
            "🏨 Accommodation": budget_data["accommodation"],
            "🍴 Food": budget_data["food"],
            "🚗 Transport": budget_data["transport"],
            "🎟️ Activities": budget_data["activities"],
            "📦 Miscellaneous": budget_data["miscellaneous"]
        }

        for category, amount in categories.items():

            percentage = (
                amount / total
                if total > 0
                else 0
            )

            st.write(
                f"**{category}** — ₹{amount:,}"
            )

            st.progress(
                percentage
            )

        st.caption(
            "⚠️ These are AI-generated estimates. "
            "Check current prices before booking."
        )

        