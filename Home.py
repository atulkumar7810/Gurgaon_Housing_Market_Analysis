# Import necessary libraries
import streamlit as st
from PIL import Image
import os

# Set Streamlit page configuration
st.set_page_config(page_title="Real Estate Analytics App")

# Home Page
st.title('Real Estate Analytics App')
st.markdown("---")

# Provide a brief description or welcome message
st.write("""
Welcome to the Real Estate Analytics App! This app helps you analyze and explore real estate data for Gurgaon.
Navigate through different pages to predict prices, visualize analytics, and get apartment recommendations.
""")

# -------- IMAGE HANDLING (for WebPage_Development structure) --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, "WebPage_Development", "images", "Real_Estate_Analytics.jpg")

if os.path.exists(image_path):
    image = Image.open(image_path)
    st.image(image, caption="Real Estate Analytics App", use_column_width=True)
else:
    st.warning("⚠️ Image not found. Please check: WebPage_Development/images/Real_Estate_Analytics.jpg")

# Add additional content or links to guide users
st.write("Explore the various functionalities using the sidebar.")

# Create a horizontal line using markdown
st.markdown("---")

# Price Prediction description
st.header("Price Prediction")
st.write(
    "The Gurgaon property price prediction algorithm employs machine learning, leveraging key factors like "
    "location, amenities, and market trends to swiftly estimate property prices with high accuracy"
)
st.markdown("💰 Use sidebar → Price Predictor")

# Analysis App description
st.header("Analysis App")
st.write(
    "Explore Gurgaon properties effortlessly with our data analysis app, powered by machine learning and "
    "advanced Python. Gain insightful perspectives for informed decisions in real estate"
)
st.markdown("🔍 Use sidebar → Analysis App")

# Recommend Apartments description
st.header("Recommend Apartments")
st.write(
    "Discover your ideal Gurgaon property with our ML-driven recommender system. Tailored suggestions based on "
    "location, landmarks, and societies ensure personalized and efficient real estate choices"
)
st.markdown("🤝 Use sidebar → Recommend Apartments")

st.markdown("---")

# Display a support message with an email contact
st.write("For support, contact us at atulkumarsingh7810@gmail.com, amriteshrai7810@gmail.com")
