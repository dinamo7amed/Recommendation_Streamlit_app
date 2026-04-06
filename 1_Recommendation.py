import streamlit as st
import pandas as pd

# -----------------------------
# Session State للصفحات
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"

# -----------------------------
# بيانات الريكومنديشن
# -----------------------------
df = pd.read_csv('smart_parking_Data_28k.csv')
rec_df = df.groupby(['day', 'hour']).agg({
    'occupancy': 'mean',
    'price': 'mean'
}).reset_index()
rec_df['score'] = (1 - rec_df['occupancy']) * 0.7 + (1 / rec_df['price']) * 0.3

def recommend(day, prefer='balanced'):
    data = rec_df[rec_df['day'] == day]
    if prefer == 'cheap':
        return data.sort_values(by='price').iloc[0]
    elif prefer == 'less crowded':
        return data.sort_values(by='occupancy').iloc[0]
    else:
        return data.sort_values(by='score', ascending=False).iloc[0]

# -----------------------------
# Full Screen CSS
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 20px !important;
}

/* الصفحة الأولى فول سكرين */
.full-screen-img {
    background-image: url('https://images.unsplash.com/photo-1502877338535-766e1452684a');
    background-size: cover;
    background-position: center;
    height: 100vh;
    width: 100%;
    position: relative;
}

/* نصوص وألوان */
h1 { font-size: 40px !important; color: white !important; text-align: center;}
h2, h3 { font-size: 28px !important; color: white !important;}
p, label, div { font-size: 20px !important; color: white !important;}
[data-testid="stMetricValue"] { font-size: 28px !important; color: white !important;}
[data-testid="stMetric"] { background-color: #132B5E; padding: 15px; border-radius: 12px; color: white !important;}
.stButton>button { background-color: #1E3A8A; color: white; border-radius: 10px; height: 3em; width: 100%; font-size: 20px; border: none;}
.stSlider label, .stSelectbox label { color: white !important; font-size: 20px !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# الصفحة الأولى
# -----------------------------
if st.session_state.page == "intro":
    st.markdown('<div class="full-screen-img"></div>', unsafe_allow_html=True)
    st.title("🚗 Smart Parking System")
    
    # Inputs على الصورة نفسها
    day = st.selectbox("📅 Choose Day", sorted(df['day'].unique()))
    preference = st.selectbox("💡 Preference", ["balanced", "cheap", "less crowded"])
    user_hour = st.slider("⏰ Choose Your Time", 0, 23)

    if st.button("🚀 Go to Recommendation"):
        st.session_state.page = "recommendation"

# -----------------------------
# الصفحة التانية: الريكومنديشن فقط
# -----------------------------
elif st.session_state.page == "recommendation":
    st.title("🚗 Smart Parking Recommendation")
    
    day = st.selectbox("📅 Choose Day", sorted(df['day'].unique()))
    preference = st.selectbox("💡 Preference", ["balanced", "cheap", "less crowded"])
    user_hour = st.slider("⏰ Choose Your Time", 0, 23)

    if st.button("🚀 Get Recommendation"):
        result = recommend(day, prefer=preference)
        st.success(f"✨ Best time is {int(result['hour'])}:00 🕒")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚗 Occupancy", round(result['occupancy'], 2))
        with col2:
            st.metric("💰 Price", round(result['price'], 2))
        st.write("### 🚦 Parking Status")
        st.progress(int(result['occupancy'] * 100))

        current = rec_df[(rec_df['day'] == day) & (rec_df['hour'] == user_hour)]
        if not current.empty:
            current = current.iloc[0]
            if current['score'] < result['score']:
                st.warning(f"⚠️ Better time is {int(result['hour'])}:00")
            else:
                st.success("✅ Your choice is great!")