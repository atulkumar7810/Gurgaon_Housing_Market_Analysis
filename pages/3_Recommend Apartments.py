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

# Reset index safely and store property names in a column
location_df = location_df.reset_index().rename(columns={'index': 'PropertyName'})

# Constants for weighting in the similarity matrix
weight_1 = 30
weight_2 = 20
weight_3 = 8


def recommend_properties_with_scores(property_name, top_n=5):
    cosine_sim_matrix = weight_1 * cosine_sim1 + weight_2 * cosine_sim2 + weight_3 * cosine_sim3

    try:
        idx = location_df[location_df["PropertyName"] == property_name].index[0]
    except IndexError:
        st.error("Selected apartment not found in dataset.")
        st.stop()

    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]

    top_properties = location_df.loc[top_indices, "PropertyName"].tolist()

    recommendations_df = pd.DataFrame({
        'PropertyName': top_properties,
        'SimilarityScore': top_scores
    })

    return recommendations_df


@st.cache_data
def get_apartments_list(location_df, selected_location, radius):
    result_df = location_df[location_df[selected_location] < radius * 1000].sort_values(selected_location)

    if len(result_df) == 0:
        st.warning("No Property Found!")
        st.stop()

    return result_df["PropertyName"].to_list()


@st.cache_data
def get_recommendation_df(selected_apartment):
    return recommend_properties_with_scores(selected_apartment, 5)


# Recommend properties based on location
st.title('Select Location and Radius')
selected_location = st.selectbox('Location', sorted(location_df.columns.to_list()[1:]), index=0)
radius = st.number_input('Radius in Kms', min_value=0, max_value=330, value=10, step=5)

# Cache the apartments_list
apartments_list = get_apartments_list(location_df, selected_location, radius)

if st.button('Search'):
    for key in apartments_list:
        dist = location_df.loc[location_df["PropertyName"] == key, selected_location].values[0]
        st.write(f'{key} : {round(dist / 1000, 1)} Kms')


headers = {
    'authority': 'www.99acres.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'user-agent': 'Mozilla/5.0'
}

# Retry decorator configuration
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def fetch_url(url):
    return requests.get(url, headers=headers, timeout=30, allow_redirects=True)


def image_scrap(row):
    url = row["Link"]
    try:
        response = fetch_url(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tags = soup.find('div', class_="PhotonCard__photonDisp")
        text_data = soup.find("h1", class_="ProjectInfo__imgBox1 title_bold")

        try:
            text_data_data = text_data.find("span")
            img_tags_img = img_tags.find("img").get("src")
            st.markdown(f"Location : {text_data_data.text}")
            st.image(img_tags_img, caption=f'{row["PropertyName"]}', use_column_width=True)
        except:
            st.image('images/No_images.jpg', caption="", use_column_width=True)

    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch image: {e}")


# Recommendation section
st.title('Recommend Apartments')
selected_apartment = st.selectbox('Select an Apartment', apartments_list)

if st.button('Recommend'):
    recommendation_df = get_recommendation_df(selected_apartment)

    # Safe link mapping
    recommendation_df["Link"] = recommendation_df["PropertyName"].map(
        lambda x: link_loc[x].values[0] if x in link_loc else None
    )

    if recommendation_df.empty:
        st.warning(f'No Recommendations found!')
    else:
        st.success("### Recommended Apartments:")
        for index, row in recommendation_df.iterrows():
            st.markdown("---")
            st.markdown(f"**{row['PropertyName']}** : [Link]({row['Link']})")
            image_scrap(row)
