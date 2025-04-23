import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import re 
import plotly.express as px

# Download required NLTK data (only needs to be done once)
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}

    /* ✅ Ensure the Streamlit Settings Menu is Visible */
    [data-testid="stToolbar"] {{
        visibility: visible !important;
        display: block !important;
    }}
    </style>
    '''
    
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_png_as_page_bg('bg.jpg')

# Function to get image as base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Convert image to base64
img = get_img_as_base64("images1.jpg")

# Define CSS for sidebar background
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

# Sidebar content
with st.sidebar:
    st.image("sidebar.png", use_container_width=True)

# Load the dataset
try:
    df = pd.read_csv('amazon_fashion.csv', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('amazon_fashion.csv', encoding='ISO-8859-1')

# Initialize SentimentIntensityAnalyzer (VADER)
analyzer = SentimentIntensityAnalyzer()

# Function to get sentiment using VADER
def get_sentiment(review):
    vs = analyzer.polarity_scores(review)
    return vs['compound']  # Use compound score for overall sentiment

# Function to classify sentiment based on VADER's compound score
def classify_sentiment(compound_score):
    if compound_score >= 0.05:  # Threshold adjusted for better accuracy
        return 'Positive'
    elif compound_score <= -0.05:  # Threshold adjusted for better accuracy
        return 'Negative'
    else:
        return 'Neutral'

# # Function to scrape reviews and ratings from a given URL for a given number of pages
# def get_reviews(url, num_pages=2):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
#     }
#     all_reviews = []
#     all_ratings = []
#     try:
#         for page_num in range(1, num_pages + 1):
#             # Construct the URL for the current page
#             page_url = f"{url}&pageNumber={page_num}" if '?' in url else f"{url}?pageNumber={page_num}"

#             response = requests.get(page_url, headers=headers)
#             response.raise_for_status()  # Raise HTTPError for bad responses
#             soup = BeautifulSoup(response.content, 'html.parser')

#             # Find all review elements
#             review_elements = soup.find_all('span', {'data-hook': 'review-body'})
#             rating_elements = soup.find_all('i', {'data-hook': 'review-star-rating'})

#             for element, rating in zip(review_elements, rating_elements):
#                 review_text = element.get_text().strip()
#                 # Remove Read more
#                 review_text = review_text.replace("Read more", "").strip()
#                 review_text = review_text.replace("Read More", "").strip()

#                 # Extract rating as float from the text (e.g., "5.0 out of 5 stars")
#                 rating_text = rating.get_text().strip()
#                 rating_value = float(rating_text.split()[0]) if rating_text else None

#                 all_reviews.append(review_text)
#                 all_ratings.append(rating_value)

#             time.sleep(1)  # Add delay to avoid being blocked
#     except requests.exceptions.RequestException as e:
#         st.error(f"Failed to fetch reviews from page {page_num}: {e}")
#     except Exception as e:
#         st.error(f"Error parsing reviews from page {page_num}: {e}")

#     return all_reviews, all_ratings

import requests
from bs4 import BeautifulSoup
import time
#import streamlit as st  # Only if using streamlit


def get_reviews(url, num_pages=2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    all_reviews = []
    all_ratings = []

    for page_num in range(1, num_pages + 1):
        try:
            # Construct the URL for the current page
            page_url = f"{url}&pageNumber={page_num}" if '?' in url else f"{url}?pageNumber={page_num}"

            print(f"Fetching reviews from: {page_url}") #Added for debugging

            response = requests.get(page_url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all review elements
            review_elements = soup.find_all('span', {'data-hook': 'review-body'})
            rating_elements = soup.find_all('i', {'data-hook': 'review-star-rating'})

            # Check if review elements are found
            if not review_elements:
                print(f"No review elements found on page {page_num}.  Check the URL and selectors.") #Added for debugging
                continue # Skip to the next page if no reviews are found
                #break #If you want to stop as soon as you can't find reviews.


            for element, rating in zip(review_elements, rating_elements):
                review_text = element.get_text().strip()
                # Remove Read more
                review_text = review_text.replace("Read more", "").strip()
                review_text = review_text.replace("Read More", "").strip()

                # Extract rating as float from the text (e.g., "5.0 out of 5 stars")
                rating_text = rating.get_text().strip()
                rating_value = float(rating_text.split()[0]) if rating_text else None

                all_reviews.append(review_text)
                all_ratings.append(rating_value)
                
                #print(f"Review: {review_text[:50]}... Rating: {rating_value}") # Added for debugging

            time.sleep(1)  # Add delay to avoid being blocked

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch reviews from page {page_num}: {e}")  # Use print instead of st.error
            #st.error(f"Failed to fetch reviews from page {page_num}: {e}")  # Use print instead of st.error
            break # stop if the connection fails, no point continuing.
        except Exception as e:
            print(f"Error parsing reviews from page {page_num}: {e}") # Use print instead of st.error
            #st.error(f"Error parsing reviews from page {page_num}: {e}")  # Use print instead of st.error
            break # stop if there's a parsing error, no point continuing.

    return all_reviews, all_ratings


# Example usage (replace with your actual URL)
if __name__ == '__main__':
    url = "https://www.amazon.com/product-reviews/B07G15D7XG" #Replace with your URL
    reviews, ratings = get_reviews(url, num_pages=5)  # Fetch 5 pages of reviews

    print(f"Number of reviews: {len(reviews)}")
    print(f"Number of ratings: {len(ratings)}")

    if reviews:
        print("\nSome example reviews:")
        for i in range(min(5, len(reviews))):  # Print the first 5 reviews
            print(f"Review {i+1}: {reviews[i][:100]}...") #Print the first 100 characters
            print(f"Rating {i+1}: {ratings[i]}")
            
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
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['green', 'blue', 'red'])
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(plt)

# Function to create a bar chart from sentiment analysis
def create_bar_chart(sentiments):
    sentiment_counts = sentiments.value_counts()
    sentiment_df = pd.DataFrame({'Sentiment': sentiment_counts.index, 'Count': sentiment_counts.values})
    fig = px.bar(sentiment_df, x='Sentiment', y='Count',
                 color='Sentiment',  # Color bars by sentiment
                 color_discrete_map={'Positive': 'green', 'Neutral': 'blue', 'Negative': 'red'}, # Set bar colors
                 labels={'Count': 'Number of Reviews', 'Sentiment': 'Sentiment Type'},  # Axis labels
                 title='Sentiment Distribution')

    st.plotly_chart(fig, use_container_width=True)

# Function to display star rating
def display_star_rating(rating):
    full_star = '<span style="color: gold;">&#9733;</span>'
    empty_star = '<span style="color: #FFD70040;">&#9733;</span>'  # Light yellow outline for empty stars
    stars = full_star * int(rating) + empty_star * (5 - int(rating))
    st.markdown(f'<div style="font-size: 20px;">{stars}</div>', unsafe_allow_html=True)

# Function to display sentiment in a colored box
def display_sentiment_box(sentiment):
    if sentiment == 'Positive':
        color_code = 'green'
    elif sentiment == 'Negative':
        color_code = 'red'
    else:
        color_code = 'blue'  # Or gray, or another neutral color

    st.markdown(f'<div style="background-color:{color_code}; color:white; padding:5px; border-radius:5px;">{sentiment}</div>', unsafe_allow_html=True)

# Main App
st.title("SentiMart📦: Amazon Sentiment App")

# Initialize session state for expanded reviews
if 'expanded_reviews' not in st.session_state:
    st.session_state.expanded_reviews = {}

# Home Page
def home():
    st.subheader("Welcome to the Product Review and Sentiment Analysis App")
    st.image("image.jpg", use_container_width=True)
    st.write("Use the navigation menu to write a review, search for a product, or enter an Amazon product URL.")

# Write a Review Page
def write_review():
    st.subheader("Write a Review")
    review = st.text_area("Enter your review here:")
    if st.button("Analyze Sentiment"):
        if review:
            compound_score = get_sentiment(review)
            sentiment = classify_sentiment(compound_score)
            st.write(f"Sentiment: {sentiment}")
            st.write(f"Compound Score: {compound_score:.2f}")
        else:
            st.write("Please enter a review to analyze.")

# Search a Product Page
def search_product():
    st.subheader("Search for a Product")
    category = st.selectbox("Select a category:", ['Select Category'] + list(df['Category'].unique())) # Add "Select Category"
    if category != 'Select Category':
        products_in_category = df[df['Category'] == category]['product_name'].unique()
        selected_product = st.selectbox("Select a product:", ['Select Product'] + list(products_in_category))# Add "Select Product"
        if selected_product != 'Select Product':
            product_details = df[(df['Category'] == category) & (df['product_name'] == selected_product)].iloc[0]

            # Display product image with a smaller size
            st.image(product_details['large'], width=300)

            # Display product details
            st.write(f"**Product Name:** {product_details['product_name']}")
            st.write(f"**Rating:** {product_details['rating']}")
            st.write(f"**Price:** {product_details['sales_price']}")

            # Display word cloud of reviews
            reviews, ratings = get_reviews(product_details['product_url']) # Get reviews (default 2 pages)
            if reviews:
                all_reviews_text = " ".join(reviews)
                create_wordcloud(all_reviews_text)

                # Create sentiments
                sentiments = pd.Series([classify_sentiment(get_sentiment(review)) for review in reviews])

                # Display pie chart of sentiments
                create_pie_chart(sentiments)

                # Display bar chart of sentiments
                create_bar_chart(sentiments)

                # Display reviews with sentiment and rating
                st.write("**Reviews:**")
                for review, rating in zip(reviews, ratings):
                    compound_score = get_sentiment(review)
                    sentiment = classify_sentiment(compound_score)

                    st.write(f"**Review:** {review}")
                    display_star_rating(rating)  # Display star rating
                    st.write("**Sentiment:**")
                    display_sentiment_box(sentiment)  # Display sentiment in colored box
                    st.write("---")
                st.write(f"**Total Reviews Found:** {len(reviews)}")
            else:
                st.write("No reviews found.")

# Enter Amazon Product URL Page
def enter_product_url():
    st.subheader("Enter Amazon Product URL")
    product_url = st.text_input("Enter the Amazon product URL:")

    if product_url:
        if st.button("Fetch Reviews"):
            reviews, ratings = get_reviews(product_url) # Get reviews (default 2 pages)
            if reviews:
                all_reviews_text = " ".join(reviews)
                create_wordcloud(all_reviews_text)

                # Create sentiments
                sentiments = pd.Series([classify_sentiment(get_sentiment(review)) for review in reviews])

                # Display pie chart of sentiments
                create_pie_chart(sentiments)

                # Display bar chart of sentiments
                create_bar_chart(sentiments)

                # Display reviews with sentiment and rating
                st.write("**Reviews:**")
                for review, rating in zip(reviews, ratings):
                    compound_score = get_sentiment(review)
                    sentiment = classify_sentiment(compound_score)

                    st.write(f"**Review:** {review}")
                    display_star_rating(rating)  # Display star rating
                    st.write("**Sentiment:**")
                    display_sentiment_box(sentiment)  # Display sentiment in colored box
                    st.write("---")
                st.write(f"**Total Reviews Found:** {len(reviews)}")
            else:
                st.write("No reviews found.")
        else:
            st.write("Please enter a valid Amazon product URL.")

# Import CSV Page
def import_csv():
    st.subheader("Import CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file(should contain review and rating columns)", type="csv")
    
    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            if 'review' not in user_df.columns or 'rating' not in user_df.columns:
                st.error("CSV file must contain 'review' and 'rating' columns.")
                return

            # Perform sentiment analysis
            user_df['compound_score'] = user_df['review'].apply(get_sentiment)
            user_df['sentiment'] = user_df['compound_score'].apply(classify_sentiment)

            # Display word cloud
            all_reviews_text = " ".join(user_df['review'])
            create_wordcloud(all_reviews_text)

            # Display pie chart of sentiments
            create_pie_chart(user_df['sentiment'])

            # Display bar chart of sentiments
            create_bar_chart(user_df['sentiment'])

            # Display reviews with sentiment and rating
            st.write("**Reviews:**")
            for i, row in user_df.iterrows():
                st.write(f"**Review:** {row['review']}")
                display_star_rating(row['rating'])
                st.write("**Sentiment:**")
                display_sentiment_box(row['sentiment']) # Display sentiment in colored box
                st.write("---")
            st.write(f"**Total Reviews Analyzed:** {len(user_df)}")

        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

# Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Go to", ['Home', 'Write a Review', 'Search a Product', 'Enter Amazon Product URL', 'Import CSV'])

if options == 'Home':
    home()
elif options == 'Write a Review':
    write_review()
elif options == 'Search a Product':
    search_product()
elif options == 'Enter Amazon Product URL':
    enter_product_url()
elif options == 'Import CSV':
    import_csv()