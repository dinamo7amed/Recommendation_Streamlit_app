import streamlit as st
import pandas as pd

# ====== Load Data ======
df = pd.read_csv('smart_parking_Data_28k.csv')

# ====== Aggregate & Score ======
epsilon = 1e-6
rec_df = df.groupby(['day', 'hour']).agg({
    'occupancy': 'mean',
    'price': 'mean'
}).reset_index()

rec_df['score'] = (1 - rec_df['occupancy']) * 0.7 + (1 / (rec_df['price'] + epsilon)) * 0.3

# ====== Recommendation Function ======
def recommend(day, prefer='balanced'):
    data = rec_df[rec_df['day'] == day].copy()
    if prefer == 'cheap':
        return data.sort_values(by='price').iloc[0]
    elif prefer == 'less crowded':
        return data.sort_values(by='occupancy').iloc[0]
    else:
        return data.sort_values(by='score', ascending=False).iloc[0]

# ====== Initialize session state for page ======
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ====== Function to go to Recommendations ======
def go_to_recommendations():
    st.session_state.page = 'recommendations'

# ====== Pages ======
if st.session_state.page == 'home':
    # ====== Home Page ======
    st.title("🚗 Smart Parking System")  # Title above the image
    st.image("https://images.unsplash.com/photo-1502877338535-766e1452684a", use_column_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("➡️ Go to Recommendations", on_click=go_to_recommendations)

else:
    # ====== Recommendation Page ======
    st.title("🚗 Smart Parking System")

    # Labels بولد
    st.markdown("**📅 Choose Day**")
    day = st.selectbox(
        "",
        sorted(df['day'].unique())
    )

    st.markdown("**💡 Preference**")
    preference = st.selectbox(
        "",
        ["balanced", "cheap", "less crowded"]
    )

    st.markdown("**⏰ Choose Your Time**")
    user_hour = st.slider("",
                          0, 23)

    if st.button("🚀 Get Recommendation"):
        result = recommend(day, prefer=preference)
        
        st.success(f"Best time is {int(result['hour'])}:00 🕒")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚗 Occupancy", round(result['occupancy'], 2))
        with col2:
            st.metric("💰 Price", round(result['price'], 2))

        st.progress(min(max(int(result['occupancy'] * 100), 0), 100))

        # Compare with user's choice
        current = rec_df[(rec_df['day'] == day) & (rec_df['hour'] == user_hour)]
        if not current.empty:
            current = current.iloc[0]
            if current['score'] < result['score']:
                st.warning(f"⚠️ Better time is {int(result['hour'])}:00")
            else:
                st.success("✅ Your choice is great!")

# ====== App Theme ======
st.markdown("""
    <style>
    /* Background */
    .stApp {
        background-color: #050e2e;  /* كحلي غامق جدًا */
        color: white;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #0b2545;  /* كحلي sidebar */
        color: white;
    }
    /* Selectbox & Slider Dark Blue + White text */
    div.stSelectbox, div.stSlider {
        background-color: #0b3d91 !important; /* Dark Blue */
        color: white !important;
        font-weight: bold !important;
    }
    /* Buttons */
    .stButton>button {
        background-color: #1e90ff;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)