from bs4 import BeautifulSoup
from random import randint
import pandas as pd
import requests
import time
import os

# Select the city
City = 'Gurgaon'

# Header
headers = {
    'authority': 'www.99acres.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'referer': f'https://www.99acres.com/flats-in-%7BCity%7D-ffid-page',
    'sec-ch-ua': '"Chromium";v="107", "Not;A=Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Select the property name for saving the file
property_type = ['Flats', 'Societies', 'Residential', 'Independent House']

# Create directories and subdirectories for storing different files
project_dir = os.getcwd()  # Creating subdirectories in the current directory
subdirectories = ['Data', f'Data/{City}', f'Data/{City}/{property_type[0]}', f'Data/{City}/{property_type[1]}', f'Data/{City}/{property_type[2]}',
                  f'Data/{City}/{property_type[3]}']

for subdir in subdirectories:
    dir_path = os.path.join(project_dir, subdir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

# Page number range for extracting data
# start = int(input('Page to start: '))
start = int(input('Enter the page number to start: '))
end = start + 2  # Only scraping 10 pages at times as ip address is getting blocked

pageNumber = start
req = 0

# Creating Data Frame to save the info
flats = pd.DataFrame()

try:
    while pageNumber < end:
        i = 1
        url = f"https://www.99acres.com/{property_type[0]}-in-{City}-ffid-page-{pageNumber}"
        page = requests.get(url, headers=headers)
        pageSoup = BeautifulSoup(page.content, 'html.parser')
        req += 1

        time.sleep(int(randint(1, 5)))

        for soup in pageSoup.select_one('div[data-label="SEARCH"]').select('section[data-hydration-on-demand="true"]'):
            # Extract property name and property sub-name

            try:
                property_name = soup.find('h2', {'class': 'tupleNew__propType'}).text.strip()
                # Extract link
                link = soup.find('a', {'class': 'tupleNew__propertyHeading ellipsis'}).get('href')
                society = soup.find('div', {'class': 'tupleNew__locationName ellipsis'}).text.strip()
            except AttributeError:
                continue

            time.sleep(int(randint(1, 5)))

            # Detail Page
            page = requests.get(link, headers=headers)
            d_pageSoup = BeautifulSoup(page.content, 'html.parser')
            req += 1

            try:
                # price Range
                price = d_pageSoup.select_one('#pdPrice2').text.strip()
            except AttributeError:
                price = ''

            # Area
            try:
                area = soup.select_one('#srp_tuple_price_per_unit_area').text.strip()
            except AttributeError:
                area = ''
            # Area with Type
            try:
                areaWithType = d_pageSoup.select_one('#factArea').text.strip()
            except AttributeError:
                areaWithType = ''

            time.sleep(int(randint(1, 5)))

            # Configuration
            try:
                bedRoom = d_pageSoup.select_one('#bedRoomNum').text.strip()
            except AttributeError:
                bedRoom = ''
            try:
                bathroom = d_pageSoup.select_one('#bathroomNum').text.strip()
            except AttributeError:
                bathroom = ''
            try:
                balcony = d_pageSoup.select_one('#balconyNum').text.strip()
            except AttributeError:
                balcony = ''

            try:
                additionalRoom = d_pageSoup.select_one('#additionalRooms').text.strip()
            except AttributeError:
                additionalRoom = ''

            time.sleep(int(randint(1, 5)))

            # Address

            try:
                address = d_pageSoup.select_one('#address').text.strip()
            except AttributeError:
                address = ''
            # Floor Number
            try:
                floorNum = d_pageSoup.select_one('#floorNumLabel').text.strip()
            except AttributeError:
                floorNum = ''

            try:
                facing = d_pageSoup.select_one('#facingLabel').text.strip()
            except AttributeError:
                facing = ''

            try:
                agePossession = d_pageSoup.select_one('#agePossessionLbl').text.strip()
            except AttributeError:
                agePossession = ''

            time.sleep(int(randint(1, 5)))

            # Nearby Locations

            try:
                nearbyLocations = [i.text.strip() for i in d_pageSoup.select_one('div.NearByLocation_tagWrap').select(
                    'span.NearByLocation_infoText')]
            except AttributeError:
                nearbyLocations = ''

            # Descriptions
            try:
                description = d_pageSoup.select_one('#description').text.strip()
            except AttributeError:
                description = ''

            # Furnish Details
            try:
                furnishDetails = [i.text.strip() for i in d_pageSoup.select_one('#FurnishDetails').select('li')]
            except AttributeError:
                furnishDetails = ''

            # Features
            if furnishDetails:
                try:
                    features = [i.text.strip() for i in d_pageSoup.select('#features')[1].select('li')]
                except IndexError:
                    features = ''
            else:
                try:
                    features = [i.text.strip() for i in d_pageSoup.select('#features')[0].select('li')]
                except IndexError:
                    features = ''

            time.sleep(int(randint(1, 5)))

            # Rating by Features
            try:
                rating = [i.text for i in d_pageSoup.select_one('div.review_rightSide>div>ul>li>div').select(
                    'div.ratingByFeature_circleWrap')]
            except AttributeError:
                rating = ''
            # print(top_f)

            try:
                # Property ID
                property_id = d_pageSoup.select_one('#Prop_Id').text.strip()
            except AttributeError:
                property_id = ''

            # Create a Dictionary with the given variables
            property_data = {
                'property_name': property_name,
                'link': link,
                'society': society,
                'price': price,
                'area': area,
                'areaWithType': areaWithType,
                'bedRoom': bedRoom,
                'bathroom': bathroom,
                'balcony': balcony,
                'additionalRoom': additionalRoom,
                'address': address,
                'floorNum': floorNum,
                'facing': facing,
                'agePossession': agePossession,
                'nearbyLocations': nearbyLocations,
                'description': description,
                'furnishDetails': furnishDetails,
                'features': features,
                'rating': rating,
                'property_id': property_id
            }

            temp_df = pd.DataFrame.from_records([property_data])
            flats = pd.concat([flats, temp_df], ignore_index=True)

            # Random wait time to avoid ban
            i += i
            if req % 4 == 0:
                time.sleep(int(randint(5, 10)))
            if req % 15 == 0:
                time.sleep(int(randint(5, 10)))

        print(f"{pageNumber} -> {i}")
        pageNumber += 1

except AttributeError as e:
    print(e)
    print("""Your IP might have blocked. Delete Runtime and reconnect again with updating start page number.""")

    csv_file_path = f"{os.getcwd()}{property_type[0]}_{City}_data-page-{start}-{pageNumber - 1}.csv"
    if os.path.isfile(csv_file_path):
        # Append DataFrame to the existing file without header
        flats.to_csv(csv_file_path, mode='a', header=False, index=False)
    else:
        # Write DataFrame to the file with header - first time write
        flats.to_csv(csv_file_path, mode='a', header=True, index=False)

# Enter file name
file_name = input('Type the file name: ')

# Save the file
flats.to_csv(f'{os.getcwd()}/Data/{City}/{property_type[0]}/{file_name}.csv')