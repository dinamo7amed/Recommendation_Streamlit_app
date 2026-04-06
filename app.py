import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ====== Load Data ======
df = pd.read_csv('smart_parking_Data_28k.csv')

# ====== Aggregate & Score ======
epsilon = 1e-6
rec_df = df.groupby(['day', 'hour']).agg({
    'occupancy': 'mean',
    'price': 'mean'
}).reset_index()

rec_df['score'] = (1 - rec_df['occupancy']) * 0.7 + (1 / (rec_df['price'] + epsilon)) * 0.3

# ====== Dynamic Pricing ======
rec_df['dynamic_price'] = rec_df['price'] * (
    1 + 0.5 * rec_df['occupancy'] + 0.2 * (rec_df['hour'] / 23)
)

# ====== Recommendation Function ======
def recommend(day, prefer='balanced', budget=None):
    data = rec_df[rec_df['day'] == day].copy()

    if budget is not None:
        data = data[data['dynamic_price'] <= budget]
        if data.empty:
            return None

    if prefer == 'cheap':
        return data.sort_values(by='dynamic_price').iloc[0]
    elif prefer == 'less crowded':
        return data.sort_values(by='occupancy').iloc[0]
    else:
        return data.sort_values(by='score', ascending=False).iloc[0]

# ====== Nearest Best Time ======
def nearest_best_time(day, user_hour, prefer='balanced', budget=None):
    data = rec_df[rec_df['day'] == day].copy()

    if budget is not None:
        data = data[data['dynamic_price'] <= budget]
        if data.empty:
            return None

    if prefer == 'cheap':
        data = data.sort_values(by='dynamic_price')
    elif prefer == 'less crowded':
        data = data.sort_values(by='occupancy')
    else:
        data = data.sort_values(by='score', ascending=False)

    top_times = data.head(5).copy()
    top_times['distance'] = abs(top_times['hour'] - user_hour)

    return top_times.sort_values(by='distance').iloc[0]

# ====== Session State ======
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to_recommendations():
    st.session_state.page = 'recommendations'

# ====== Home Page ======
if st.session_state.page == 'home':
    st.title("🚗 Smart Parking System")
    st.image("https://images.unsplash.com/photo-1502877338535-766e1452684a", use_column_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("➡️ Go to Recommendations", on_click=go_to_recommendations)

# ====== Recommendation Page ======
else:
    st.title("🚗 Smart Parking System")

    st.markdown("**📅 Choose Day**")
    day = st.selectbox("", sorted(df['day'].unique()))

    st.markdown("**💡 Preference**")
    preference = st.selectbox("", ["balanced", "cheap", "less crowded"])

    st.markdown("**⏰ Choose Your Time**")
    user_hour = st.slider("", 0, 23, 12)

    st.markdown("**💸 Your Budget**")
    budget = st.slider(
        "",
        int(rec_df['dynamic_price'].min()),
        int(rec_df['dynamic_price'].max()),
        int(rec_df['dynamic_price'].mean())
    )

    if st.button("🚀 Get Recommendation"):
        result = recommend(day, prefer=preference, budget=budget)

        if result is None:
            st.error("❌ No available time within your budget")
        else:
            # Best Time
            st.markdown(
                f"<h2 style='color:white; font-weight:bold;'>Best time is {int(result['hour'])}:00 🕒</h2>",
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🚗 Occupancy", f"{round(result['occupancy'],2)}")
            with col2:
                st.metric("💰 Dynamic Price", f"{round(result['dynamic_price'],2)}")

            st.progress(min(max(int(result['occupancy'] * 100), 0), 100))

            # مقارنة مع اختيار المستخدم
            current = rec_df[(rec_df['day'] == day) & (rec_df['hour'] == user_hour)]
            nearest = nearest_best_time(day, user_hour, preference, budget)

            if not current.empty and nearest is not None:
                current = current.iloc[0]

                if int(nearest['hour']) != user_hour:
                    st.warning(f"⚠️ Closest better time is {int(nearest['hour'])}:00")

                    st.info(f"""
🔍 Your choice: {user_hour}:00  
⚡ Better nearby time: {int(nearest['hour'])}:00  
💰 You save: {round(current['dynamic_price'] - nearest['dynamic_price'],2)}
""")
                else:
                    st.success("✅ Your choice is already optimal!")

    # ====== Chart ======
    st.subheader("📊 Dynamic Price vs Occupancy")

    fig, ax = plt.subplots()
    ax.scatter(rec_df['occupancy'], rec_df['dynamic_price'])
    ax.set_xlabel("Occupancy")
    ax.set_ylabel("Dynamic Price")

    st.pyplot(fig)

# ====== Styling ======
st.markdown("""
<style>
.stApp {
    background-color: #050e2e;
    color: white;
}
.css-1d391kg {
    background-color: #0b2545;
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