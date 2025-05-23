import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import seaborn as sns
import plotly.express as px
import base64
import re 

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
img = get_img_as_base64("images1.jpg")

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
st.markdown(sidebar_bg_img, unsafe_allow_html=True)
with st.sidebar:
    st.image("sidebar.png", use_container_width=True)
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

# Function to get sentiment using VADER
def get_sentiment(review):
    vs = analyzer.polarity_scores(review)
    return vs['compound'] 

def classify_sentiment(compound_score):
    if compound_score >= 0.05: 
        return 'Positive'
    elif compound_score <= -0.05: 
        return 'Negative'
    else:
        return 'Neutral'



def get_reviews(url, num_pages=1):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    all_reviews = []
    all_ratings = []
    for page_num in range(1, num_pages + 1):
        try:
            page_url = f"{url}&pageNumber={page_num}" if '?' in url else f"{url}?pageNumber={page_num}"

            print(f"Fetching reviews from: {page_url}")

            response = requests.get(page_url, headers=headers)
            response.raise_for_status()  
            soup = BeautifulSoup(response.content, 'html.parser')
            review_elements = soup.find_all('span', {'data-hook': 'review-body'})
            rating_elements = soup.find_all('i', {'data-hook': 'review-star-rating'})
            if not review_elements:
                print(f"No review elements found on page {page_num}.  Check the URL and    selectors.") #Added for debugging
                continue 

            for element, rating in zip(review_elements, rating_elements):
                review_text = element.get_text().strip()
                review_text = review_text.replace("Read more", "").strip()

                rating_text = rating.get_text().strip()
                rating_value = float(rating_text.split()[0]) if rating_text else None

                all_reviews.append(review_text)
                all_ratings.append(rating_value)
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch reviews from page {page_num}: {e}") 
            break
        except Exception as e:
            print(f"Error parsing reviews from page {page_num}: {e}") 
            break
    return all_reviews, all_ratings
   
# Function to create a word cloud from text
def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Function to create a pie chart of sentiments
def create_pie_chart(sentiments):
    sentiment_counts = sentiments.value_counts()
    labels = sentiment_counts.index
    sizes = sentiment_counts.values
    palette = {
        'Positive': 'green',
        'Neutral': 'blue',
        'Negative': 'red'
    }
    # Map colors based on the labels
    colors = [palette.get(label, 'grey') for label in labels]
    plt.figure(figsize=(10, 5), frameon=False)
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.axis('equal')  
    st.pyplot(plt)

def create_bar_chart(sentiments):
    sentiment_counts = sentiments.value_counts()
    sentiment_df = pd.DataFrame({'Sentiment': sentiment_counts.index, 'Count': sentiment_counts.values})
    fig, ax = plt.subplots(figsize=(8, 5), frameon=False)
    sns.barplot(data=sentiment_df, x='Sentiment', y='Count',
        palette={'Positive': 'green', 'Neutral': 'blue', 'Negative': 'red'}, ax=ax)
    st.pyplot(fig)

# Function to display star rating
def display_star_rating(rating):
    full_star = '<span style="color: gold;">&#9733;</span>'
    empty_star = '<span style="color: #FFD70040;">&#9733;</span>' 
    stars = full_star * int(rating) + empty_star * (5 - int(rating))
    st.markdown(f'<div style="font-size: 20px;">{stars}</div>', unsafe_allow_html=True)

# Function to display sentiment in a colored box
def display_sentiment_box(sentiment):
    if sentiment == 'Positive':
        color_code = 'green'
    elif sentiment == 'Negative':
        color_code = 'red'
    else:
        color_code = 'blue' 
    st.markdown(f'<div style="background-color:{color_code}; color:white; padding:5px; border-radius:5px;">{sentiment}</div>', unsafe_allow_html=True)

# Main App
st.title(" SentiMart📦: Amazon Sentiment Analysis App")
if 'expanded_reviews' not in st.session_state:
    st.session_state.expanded_reviews = {}

# Home Page
def home():
    st.subheader("Welcome to the Product Review and Sentiment Analysis App")
    st.image("image.jpg", use_container_width=True)
    st.info("💬 Around **88% of consumers trust online reviews as much as personal recommendations.** What are people saying about your favorite products? Find out now!")
    st.write("👉 Choose a feature and start exploring.")
  
# Write a Review Page
def write_review():
    st.subheader("Write a Review")
    review = st.text_area("Enter your review here:")
    if st.button("Analyze Sentiment"):
        if review:
            compound_score = get_sentiment(review)
            sentiment = classify_sentiment(compound_score)
            st.markdown(f"**Sentiment:** {sentiment}")
            st.info(f"Compound Score: {compound_score:.2f}")
        else:
            st.write("Please enter a review to analyze.")


# Search a Product Page
def search_product():
    try:
        df = pd.read_csv('amazon_fashion.csv', encoding='utf-8',low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv('amazon_fashion.csv', encoding='ISO-8859-1',low_memory=False)
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
                    display_star_rating(rating) 
                    st.write("**Sentiment:**")
                    display_sentiment_box(sentiment)  
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
    
            user_df['compound_score'] = user_df['review'].apply(get_sentiment)
            user_df['sentiment'] = user_df['compound_score'].apply(classify_sentiment)

            all_reviews_text = " ".join(user_df['review'])
            create_wordcloud(all_reviews_text)
            create_pie_chart(user_df['sentiment'])
            create_bar_chart(user_df['sentiment'])
            
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

st.sidebar.markdown("---")
st.sidebar.header("About this App ℹ️")
st.sidebar.write("""
This is a **Sentiment Analysis App** built using Natural Language Processing (NLP) techniques to classify Amazon product reviews as **Positive**, **Neutral**, or **Negative**.
It offers real-time scraping, CSV imports, and sentiment breakdown visualizations.
""")
st.sidebar.markdown("---")
st.sidebar.header("Key Features ⚙️")
st.sidebar.write("""
- Write your own review & get instant feedback  
- Search and analyze product reviews  
- Scrape live Amazon product reviews  
- Import CSV files for bulk review analysis  
- Visualize sentiments with charts and word clouds  
""")

st.markdown("""
    <style>
        /* Style the sidebar title */
        .css-1d391kg {
            font-weight: bold;
            color: #ffffff;
            background-color: #333333;
            padding: 10px;
            border-radius: 8px;
        }
        /* Style the tab buttons with bold text */
        .stTabs [data-baseweb="tab"] {
            font-size: 18px;
            font-weight: bold;
            background-color: #f0f0f0;
            color: #000000;
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            margin-right: 4px;
        }
        /* Highlight the selected tab */
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["**Home**", "**Write a Review**", "**Search a Product**", "**Enter URL**", "**Import CSV**"])
with tab1:
    home()
with tab2:
    write_review()
with tab3:
    search_product()
with tab4:
    enter_product_url()
with tab5:
    import_csv()
