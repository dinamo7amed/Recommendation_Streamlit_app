import streamlit as st
import pandas as pd

# ====== Load Data ======
try:
    df = pd.read_csv("smart_parking_Data_28k.csv")
except Exception as e:
    st.error(f"Error loading CSV: {e}")

# ====== Aggregate & Score ======
epsilon = 1e-6
rec_df = df.groupby(['day', 'hour']).agg({
    'occupancy': 'mean',
    'price': 'mean'
}).reset_index()

rec_df['score'] = (1 - rec_df['occupancy']) * 0.7 + (1 / (rec_df['price'] + epsilon)) * 0.3

# Dynamic Price
rec_df['dynamic_price'] = rec_df['price'] * (
    1 + 0.5 * rec_df['occupancy'] + 0.2 * (rec_df['hour'] / 23)
)

# ====== Recommendation Function ======
def recommend_dynamic(day, user_hour, prefer='balanced'):
    data = rec_df[rec_df['day'] == day].copy()

    if prefer == 'cheap':
        return data.sort_values(by='dynamic_price').iloc[0]
    elif prefer == 'less crowded':
        return data.sort_values(by='occupancy').iloc[0]
    else:
        data['score'] = (1 - data['occupancy']) * 0.7 + (1 / (data['dynamic_price'] + 1e-6)) * 0.3
        return data.sort_values(by='score', ascending=False).iloc[0]

# ====== Nearest Best Time Function ======
def nearest_best_time(day, user_hour, prefer='balanced'):
    data = rec_df[rec_df['day'] == day].copy()

    if prefer == 'cheap':
        data = data.sort_values(by='dynamic_price')
    elif prefer == 'less crowded':
        data = data.sort_values(by='occupancy')
    else:
        data['score'] = (1 - data['occupancy']) * 0.7 + (1 / (data['dynamic_price'] + 1e-6)) * 0.3
        data = data.sort_values(by='score', ascending=False)

    top_times = data.head(5).copy()
    top_times['distance'] = abs(top_times['hour'] - user_hour)
    return top_times.sort_values(by='distance').iloc[0]

# ====== Session State ======
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to_recommendations():
    st.session_state.page = 'recommendations'

def go_to_home():
    st.session_state.page = 'home'

# ====== Home Page ======
if st.session_state.page == 'home':
    st.title("🚗 Smart Parking System")
    st.image("https://images.unsplash.com/photo-1502877338535-766e1452684a", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("➡️ Go to Recommendations", on_click=go_to_recommendations)

# ====== Recommendations Page ======
else:
    st.title("🚗 Smart Parking System")
    st.button("⬅️ Back to Home", on_click=go_to_home)

    st.markdown("**📅 Choose Day**")
    day = st.selectbox("", sorted(df['day'].unique()))

    st.markdown("**💡 Preference**")
    preference = st.selectbox("", ["balanced", "cheap", "less crowded"])

    st.markdown("**⏰ Choose Your Time**")
    user_hour = st.slider("", 0, 23, 12)

    if st.button("🚀 Get Recommendation"):

        # ===== Best Recommendation =====
        best = recommend_dynamic(day, user_hour, prefer=preference)
        nearest = nearest_best_time(day, user_hour, prefer=preference)

        # ===== Selected Time Data =====
        selected = rec_df[
            (rec_df['day'] == day) & (rec_df['hour'] == user_hour)
        ].iloc[0]

        # ===== Best Time Display =====
        st.markdown(
            f"<h2 style='color:white; font-weight:bold; font-size:30px;'>Best time: {int(best['hour'])}:00 🕒</h2>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚗 Occupancy (Best)", round(best['occupancy'], 2))
        with col2:
            st.metric("💰 Price (Best)", round(best['dynamic_price'], 2))

        st.markdown("---")

        # ===== User Selected Time =====
        st.markdown(
            f"<h3 style='color:white;'>⏰ Your Time: {user_hour}:00</h3>",
            unsafe_allow_html=True
        )

        col3, col4 = st.columns(2)
        with col3:
            st.metric("🚗 Occupancy (Your Time)", round(selected['occupancy'], 2))
        with col4:
            st.metric("💵 Price (Your Time)", round(selected['dynamic_price'], 2))

        # ===== Smart Hint =====
        if selected['dynamic_price'] > best['dynamic_price']:
            st.info("💡 You can save money by choosing the recommended time!")

        # ===== Nearest Suggestion =====
        if int(nearest['hour']) != user_hour:
            st.warning(f"⚠️ Closest better time to your choice ({user_hour}:00) is {int(nearest['hour'])}:00")
        else:
            st.success("✅ Your choice is already optimal!")

# ====== Styling ======
st.markdown("""
<style>
.stApp {
    background-color: #050e2e;
    color: white;
}
div.stSelectbox {
    background-color: #0b3d91 !important;
    color: white !important;
    font-weight: bold !important;
}
input[type="range"] {
    accent-color: #1e90ff;
}
.stButton>button {
    background-color: #1e90ff;
    color: white;
    font-weight: bold;
}
label {
    font-weight: bold !important;
    color: white !important;
}
.stMetricValue, .stMetricLabel {
    color: white !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)
