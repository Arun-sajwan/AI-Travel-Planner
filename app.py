import streamlit as st
from datetime import date
from utils.gemini import create_travel_plan


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* Budget cards */
    div[data-testid="stMetric"] {
        border: 2px solid #d9d9d9;
        border-radius: 16px;
        padding: 24px 18px;
        min-height: 130px;
        background-color: black;
        color:white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }

    /* Metric label */
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 600;
    }

    /* Metric value */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("✈️ AI Travel Planner")

st.write(
    "Plan smarter. Travel better. "
    "Let AI create a personalized trip for you."
)


# --------------------------------------------------
# TRIP DETAILS
# --------------------------------------------------

st.header("🌍 Trip Details")


destination = st.text_input(
    "📍 Destination",
    placeholder="e.g. Jaipur, Paris, Tokyo"
)

# created tow columns:----------------------------
col1, col2 = st.columns(2)

with col1:

    start_date = st.date_input(
        "🗓️ Start Date",
        value=date.today()
    )
with col2:

    end_date = st.date_input(
        "🗓️ End Date",
        value=date.today()
    )
# created two columns:---------------------------------------------
travelers, budget = st.columns(2)

with travelers:
    travelers = st.number_input(
        "👥 Number of Travelers",
        min_value=1,
        max_value=20,
        value=2
    )

with budget:
    budget = st.selectbox(
        "💰 Budget",
        [
            "Budget",
            "Moderate",
            "Luxury"
        ]
    )


interests = st.multiselect(
    "❤️ What are you interested in?",
    [
        "History",
        "Culture",
        "Food",
        "Nature",
        "Adventure",
        "Shopping",
        "Nightlife",
        "Beaches",
        "Photography",
        "Relaxation"
    ]
)


travel_style = st.selectbox(
    "🎒 Travel Style",
    [
        "Relaxed",
        "Balanced",
        "Packed"
    ]
)


# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------

generate = st.button(
    "✨ Generate My Travel Plan",
    type="primary",
    key="generate_travel_plan"
)


# --------------------------------------------------
# GENERATE TRAVEL PLAN
# --------------------------------------------------

if generate:

    # Validate destination
    if not destination.strip():

        st.warning(
            "📍 Please enter a destination."
        )

        st.stop()


    # Validate dates
    if end_date < start_date:

        st.error(
            "🗓️ End date cannot be before start date."
        )

        st.stop()


    # Calculate number of days
    number_of_days = (
        end_date - start_date
    ).days + 1


    # --------------------------------------------------
    # CREATE GEMINI PROMPT
    # --------------------------------------------------

    prompt = f"""
You are an expert travel planner.

Create a personalized travel plan using these details:

Destination:
{destination}

Start date:
{start_date}

End date:
{end_date}

Number of days:
{number_of_days}

Number of travelers:
{travelers}

Budget:
{budget}

Interests:
{", ".join(interests) if interests else "General sightseeing"}

Travel style:
{travel_style}


Return ONLY valid JSON.

Use exactly this structure:

{{
    "destination": "{destination}",
    "summary": "Short description of the trip",

    "itinerary": [
        {{
            "day": 1,
            "title": "Day title",
            "activities": [
                "Activity 1",
                "Activity 2",
                "Activity 3"
            ]
        }}
    ],

    "places": [
        "Place 1",
        "Place 2",
        "Place 3"
    ],

    "food": [
        "Food recommendation 1",
        "Food recommendation 2",
        "Food recommendation 3"
    ],

    "packing": [
        "Essential item 1",
        "Essential item 2",
        "Essential item 3"
    ],

    "advice": [
        "Travel advice 1",
        "Travel advice 2",
        "Travel advice 3"
    ],

    "budget": {{
        "accommodation": "Estimated amount",
        "food": "Estimated amount",
        "transport": "Estimated amount",
        "activities": "Estimated amount",
        "total": "Estimated total"
    }}
}}

Make the itinerary appropriate for the number of days.
Do not include Markdown.
Return only JSON.
"""


    # --------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------

    try:

        with st.spinner(
            "✨ Creating your personalized travel plan..."
        ):

            plan = create_travel_plan(prompt)


        # Clear any previous error after successful run
        if "last_error" in st.session_state:
            del st.session_state["last_error"]

        # --------------------------------------------------
        # DISPLAY RESULT
        # --------------------------------------------------

        st.success(
            "🎉 Your travel plan is ready!"
        )


        st.header(
            print(f"🌍 {plan['destination']}")
        )


        st.write(
            plan["summary"]
        )


        # --------------------------------------------------
        # ITINERARY
        # --------------------------------------------------

        st.subheader("🗓️ Itinerary")


        for day in plan["itinerary"]:

            with st.expander(
                f"Day {day['day']} — {day['title']}",
                expanded=True
            ):

                for activity in day["activities"]:

                    st.write(
                        f"• {activity}"
                    )


        # --------------------------------------------------
        # PLACES
        # --------------------------------------------------

        st.subheader("📍 Places to Visit")

        for place in plan["places"]:

            st.write(
                f"• {place}"
            )


        # --------------------------------------------------
        # FOOD
        # --------------------------------------------------

        st.subheader("🍜 Food Recommendations")

        for food in plan["food"]:

            st.write(
                f"• {food}"
            )


        # --------------------------------------------------
        # PACKING
        # --------------------------------------------------

        st.subheader("🎒 Things to Carry")

        for item in plan["packing"]:

            st.write(
                f"☐ {item}"
            )


        # --------------------------------------------------
        # TRAVEL ADVICE
        # --------------------------------------------------

        st.subheader("💡 Travel Advice")

        for advice in plan["advice"]:

            st.write(
                f"• {advice}"
            )


        # --------------------------------------------------
        # BUDGET
        # --------------------------------------------------

        st.subheader("💰 Estimated Budget")


        budget_data = plan["budget"]


        col1, col2, col3, col4 = st.columns(4, gap="large")

        with col1:
            st.metric(
                "Accommodation",
                budget_data["accommodation"]
            )

        with col2:
            st.metric(
                "Food",
                budget_data["food"]
            )

        with col3:
            st.metric(
                "Transport",
                budget_data["transport"]
            )

        with col4:
            st.metric(
                "Activities",
                budget_data["activities"]
            )

        st.markdown("<br>", unsafe_allow_html=True)

        total_col = st.container()

        with total_col:
            st.metric(
                "💰 Total Estimated Budget",
                budget_data["total"]
            )


    except Exception as e:

        # Save the error so it survives Streamlit reruns
        st.session_state["last_error"] = e

        error_text = str(e).lower()

        if (
            "429" in error_text
            or "quota" in error_text
            or "rate limit" in error_text
        ):
            st.error(
                "⚠️ Gemini usage limit reached. "
                "Please try again later."
            )

        elif (
            "503" in error_text
            or "temporarily busy" in error_text
            or "service unavailable" in error_text
        ):
            st.error(
                "⏳ Gemini is temporarily busy. "
                "Please wait a moment and try again."
            )

        elif (
            "401" in error_text
            or "invalid credentials" in error_text
            or "unauthenticated" in error_text
        ):
            st.error(
                "🔐 There is a problem with the Gemini API key."
            )

        elif (
            "400" in error_text
            or "invalid_argument" in error_text
            or "api key not valid" in error_text
        ):
            st.error(
                "🔑 The Gemini API key is  invalid."
                ""
            )

        else:
            st.error(
                "❌ Something went wrong while creating your travel plan."
            )


# Show the stored exception outside the try/except body so it persists across reruns
if "last_error" in st.session_state:
    if st.button("✨ Show Error", key="show_error"):
        st.exception(st.session_state["last_error"])


    