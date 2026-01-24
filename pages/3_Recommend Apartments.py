# Import necessary libraries
import requests
import streamlit as st
from bs4 import BeautifulSoup
from retrying import retry
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(page_title="Recommend Apartments")

# Load data Using Pickle
location_df = pd.read_pickle(open('WebPage_Development/pickles/location_distance.pkl', 'rb'))
cosine_sim1 = pd.read_pickle(open('WebPage_Development/pickles/cosine_sim1.pkl', 'rb'))
cosine_sim2 = pd.read_pickle(open('WebPage_Development/pickles/cosine_sim2.pkl', 'rb'))
cosine_sim3 = pd.read_pickle(open('WebPage_Development/pickles/cosine_sim3.pkl', 'rb'))
link_loc = pd.read_pickle(open('WebPage_Development/pickles/link_loc.pkl', 'rb'))

# Constants for weighting in the similarity matrix
weight_1 = 30
weight_2 = 20
weight_3 = 8

def recommend_properties_with_scores(property_name, top_n=5):
    # Combine similarity matrices with weights
    cosine_sim_matrix = weight_1 * cosine_sim1 + weight_2 * cosine_sim2 + weight_3 * cosine_sim3
    # Get the similarity scores for the property using its name as the index
    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))

    # Sort properties based on the similarity scores
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices and scores of the top_n most similar properties
    top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]

    # Retrieve the names of the top properties using the indices
    top_properties = location_df.index[top_indices].tolist()

    # Create a dataframe with the results
    recommendations_df = pd.DataFrame({
        'PropertyName': top_properties,
        'SimilarityScore': top_scores
    })
    return recommendations_df

@st.cache_data
def get_apartments_list(location_df, selected_location, radius):
    result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()

    if len(result_ser) == 0:
        st.warning("No Property Found!")
        st.stop()
        return []

    return result_ser.index.to_list()

@st.cache_data
def get_recommendation_df(selected_apartment):
    return recommend_properties_with_scores(selected_apartment, 5)

# Recommend properties based on location
st.title('Select Location and Radius')
selected_location = st.selectbox('Location', sorted(location_df.columns.to_list()), index=21)
radius = st.number_input('Radius in Kms', min_value=0, max_value=330, value=10, step=5)

# Cache the apartments_list
apartments_list = get_apartments_list(location_df, selected_location, radius)

if st.button('Search'):
    for key in apartments_list:
        st.write(f'{key} :  {round(location_df.at[key, selected_location] / 1000, 1)} Kms')


headers = {
    'authority': 'www.99acres.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    # 'referer': f'https://www.99acres.com/flats-in-gurgaon-ffid-page',
    'sec-ch-ua': '"Chromium";v="107", "Not;A=Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# Retry decorator configuration
@retry(stop_max_attempt_number=3, wait_fixed=2000)  # Retry 3 times with a 2-second delay between retries
def fetch_url(url):
    return requests.get(url, headers=headers, timeout=30, allow_redirects=True)

def image_scrap(row):
    # Fetch and display the property image
            session = requests.Session()
            url = row["Link"]
            try:
                # Fetch the URL and handle any exceptions
                response = fetch_url(url)
                response.raise_for_status()
                # Parse the HTML content of the fetched URL
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find the div with the class 'PhotonCard__photonDisp' to locate the image
                img_tags = soup.find('div', class_="PhotonCard__photonDisp")
                text_data = soup.find("h1",class_="ProjectInfo__imgBox1 title_bold")
                try:
                    text_data_data = text_data.find("span")
                    img_tags_img = img_tags.find("img").get("src")
                    st.markdown(f"Location : {text_data_data.text}")
                    st.image(img_tags_img, caption=f'{row["PropertyName"]}', use_column_width=True)
                except:
                    # If image source is not available, display a placeholder image
                    st.image('images/No_images.jpg', caption="", use_column_width=True)
            except requests.exceptions.RequestException as e:
                # Handle any errors during URL fetching
                print(f"Failed to fetch the URL. Error: {e}")
                session.close()

# Recommendation section
st.title('Recommend Apartments')
selected_apartment = st.selectbox('Select an Apartment', apartments_list,index=None)
# Button to trigger the recommendation process
if st.button('Recommend'):
    # Get and display property recommendations based on similarity scores
    recommendation_df = get_recommendation_df(selected_apartment)
    # Adding property links to the recommendation DataFrame
    recommendation_df['Link'] = [link_loc[key].values[0] for key in recommendation_df['PropertyName'] if
                                 key in link_loc]
    # Check if there are any recommendations
    if recommendation_df.empty:
        st.warning(f'No Recommendations found!')
    else:
        # Display success message and recommended apartments
        st.success("### Recommended Apartments:")
        # Iterate through each recommended property and display its details
        for index, row in recommendation_df.iterrows():
            # Display property name with a link to its details
            st.markdown("---")
            st.markdown(f"**{row['PropertyName']}** : [Link]({row['Link']})")
            image_scrap(row)
