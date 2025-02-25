import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
from textblob import TextBlob
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Convert image to base64
img = get_img_as_base64("images1.jpg")

# Define CSS for sidebar background only
sidebar_bg_img = f"""
<style>
[data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:images1/jpg;base64,{img}");
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
}}
</style>
"""

# Apply the sidebar background
st.markdown(sidebar_bg_img, unsafe_allow_html=True)
with st.sidebar:
    st.image("sidebar.png", use_container_width=True)

# Load the dataset
try:
    df = pd.read_csv('amazon_fashion.csv', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('amazon_fashion.csv', encoding='ISO-8859-1')

# Function to get sentiment
def get_sentiment(review):
    analysis = TextBlob(review)
    return analysis.sentiment.polarity

# Function to classify sentiment
def classify_sentiment(polarity):
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Function to scrape reviews from a given URL
def get_reviews(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"}
    reviews = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        review_elements = soup.find_all('span', {'data-hook': 'review-body'})
        for element in review_elements:
            reviews.append(element.get_text().strip())
        time.sleep(1)  # Add delay to avoid being blocked by the website
    except Exception as e:
        st.error(f"Failed to fetch reviews from {url}: {e}")
    return reviews

# Function to create a word cloud from text
def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Function to create a pie chart from sentiment analysis
def create_pie_chart(sentiments):
    sentiment_counts = sentiments.value_counts()
    labels = sentiment_counts.index
    sizes = sentiment_counts.values
    plt.figure(figsize=(10, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,colors=['green','blue'])
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(plt)

st.title("SentiMart📦: Amazon Sentiment App")
# Home
def home():
    st.subheader("Welcome to the Product Review and Sentiment Analysis App")
    st.image("image.jpg", use_container_width=True)
    st.write("Use the navigation menu to write a review, search for a product, or enter an Amazon product URL.")

# Write a Review
def write_review():
    st.subheader("Write a Review")
    review = st.text_area("Enter your review here:")
    if st.button("Analyze Sentiment"):
        if review:
            polarity = get_sentiment(review)
            sentiment = classify_sentiment(polarity)
            confidence_score = abs(polarity)
            st.write(f"Sentiment: {sentiment}")
            st.write(f"Confidence Score: {confidence_score:.2f}")
        else:
            st.write("Please enter a review to analyze.")

# Search a Product
def search_product():
    st.subheader("Search for a Product")
    category = st.selectbox("Select a category:", df['Category'].unique())
    if category:
        products_in_category = df[df['Category'] == category]['product_name'].unique()
        selected_product = st.selectbox("Select a product:", products_in_category)
        if selected_product:
            product_details = df[(df['Category'] == category) & (df['product_name'] == selected_product)].iloc[0]

            # Display product image with a smaller size
            st.image(product_details['large'], width=300)

            # Display product details
            st.write(f"**Product Name:** {product_details['product_name']}")
            st.write(f"**Rating:** {product_details['rating']}")
            st.write(f"**Price:** {product_details['sales_price']}")

            # Display word cloud of reviews
            reviews = get_reviews(product_details['product_url'])
            if reviews:
                all_reviews_text = " ".join(reviews)
                create_wordcloud(all_reviews_text)

                # Display pie chart of sentiments
                sentiments = pd.Series([classify_sentiment(get_sentiment(review)) for review in reviews])
                create_pie_chart(sentiments)

                # Display reviews
                st.write(f"**Reviews:**")
                for review in reviews:
                    polarity = get_sentiment(review)
                    sentiment = classify_sentiment(polarity)
                    st.write(f"**Review:** {review}")
                    st.write(f"**Sentiment:** {sentiment}")
                    st.write("---")
            else:
                st.write("No reviews found.")

# Enter Amazon Product URL
def enter_product_url():
    st.subheader("Enter Amazon Product URL")
    product_url = st.text_input("Enter the Amazon product URL:")
    if st.button("Fetch Reviews"):
        if product_url:
            reviews = get_reviews(product_url)
            if reviews:
                all_reviews_text = " ".join(reviews)
                create_wordcloud(all_reviews_text)

                # Display pie chart of sentiments
                sentiments = pd.Series([classify_sentiment(get_sentiment(review)) for review in reviews])
                create_pie_chart(sentiments)

                # Display reviews
                st.write(f"**Reviews:**")
                for review in reviews:
                    polarity = get_sentiment(review)
                    sentiment = classify_sentiment(polarity)
                    st.write(f"**Review:** {review}")
                    st.write(f"**Sentiment:** {sentiment}")
                    st.write("---")
            else:
                st.write("No reviews found.")
        else:
            st.write("Please enter a valid Amazon product URL.")

# Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Go to", ['Home', 'Write a Review', 'Search a Product', 'Enter Amazon Product URL'])

if options == 'Home':
    home()
elif options == 'Write a Review':
    write_review()
elif options == 'Search a Product':
    search_product()
elif options == 'Enter Amazon Product URL':
    enter_product_url()