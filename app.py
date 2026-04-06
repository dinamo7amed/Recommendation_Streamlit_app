import streamlit as st
import pandas as pd

df = pd.read_csv('smart_parking_Data_28k.csv')

rec_df = df.groupby(['day', 'hour']).agg({
    'occupancy': 'mean',
    'price': 'mean'
}).reset_index()

rec_df['score'] = (1 - rec_df['occupancy']) * 0.7 + (1 / rec_df['price']) * 0.3


# 🎯 Recommendation function
def recommend(day, prefer='balanced'):
    data = rec_df[rec_df['day'] == day]
    
    if prefer == 'cheap':
        return data.sort_values(by='price').iloc[0]
    elif prefer == 'less crowded':
        return data.sort_values(by='occupancy').iloc[0]
    else:
        return data.sort_values(by='score', ascending=False).iloc[0]


# 🎨 UI
st.title("🚗 Smart Parking System")

day = st.selectbox("📅 Choose Day", sorted(df['day'].unique()))
preference = st.selectbox("💡 Preference", ["balanced", "cheap", "less crowded"])
user_hour = st.slider("⏰ Choose Your Time", 0, 23)


if st.button("🚀 Get Recommendation"):

    result = recommend(day, prefer=preference)

    st.success(f"Best time is {int(result['hour'])}:00 🕒")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🚗 Occupancy", round(result['occupancy'], 2))

    with col2:
        st.metric("💰 Price", round(result['price'], 2))

    st.progress(int(result['occupancy'] * 100))


    current = rec_df[(rec_df['day'] == day) & (rec_df['hour'] == user_hour)]

    if not current.empty:
        current = current.iloc[0]

        if current['score'] < result['score']:
            st.warning(f"⚠️ Better time is {int(result['hour'])}:00")
        else:
            st.success("✅ Your choice is great!")
st.image("https://images.unsplash.com/photo-1502877338535-766e1452684a")