import requests
from bs4 import BeautifulSoup
import csv

def fetch_page_reviews(url):
    """Fetch reviews from a given page URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def extract_reviews(soup):
    """Extract review data from a BeautifulSoup object."""
    review_cards = soup.select('div.styles_cardWrapper__LcCPA')
    reviews = []

    for card in review_cards:
        name_tag = card.select_one('a.link_internal__7XN06 span.typography_heading-xxs__QKBS8')
        customer_name = name_tag.get_text(strip=True) if name_tag else 'N/A'

        reviews_count_tag = card.select_one('div.styles_consumerExtraDetails__fxS4S span.typography_body-m__xgxZ_')
        reviews_count = reviews_count_tag.get_text(strip=True) if reviews_count_tag else 'N/A'

        review_text_tag = card.select_one('section.styles_reviewContentwrapper__zH_9M div.styles_reviewContent__0Q2Tg p.typography_body-l__KUYFJ')
        review_text = review_text_tag.get_text(strip=True) if review_text_tag else 'N/A'

        rating_img = card.select_one('div.star-rating_starRating__4rrcf img')
        if rating_img:
            alt_text = rating_img.get('alt', '')
            if 'Rated' in alt_text:
                rating = alt_text.split()[1]
            else:
                rating = 'N/A'
        else:
            rating = 'N/A'

        date_tag = card.select_one('section.styles_reviewContentwrapper__zH_9M div.typography_body-m__xgxZ_ time')
        review_date = date_tag.get_text(strip=True) if date_tag else 'N/A'
        
        experience_date_tag = card.select_one('p.typography_body-m__xgxZ_ typography_appearance-default__AAY17')
        experience_date = experience_date_tag.get_text(strip=True).split(':')[-1].strip() if experience_date_tag else 'N/A'

        reviews.append({
            'Customer Name': customer_name,
            'Number of Reviews': reviews_count,
            'Review Text': review_text,
            'Rating': f"{rating} out of 5 stars",
            'Review Date': review_date,
        })

    return reviews

def main(start_url, max_pages=90):
    """Main function to handle pagination and review extraction."""
    all_reviews = []
    current_page = 1

    while current_page <= max_pages:
        page_url = f"{start_url}?page={current_page}" if current_page > 1 else start_url
        print(f"Fetching reviews from {page_url}...")
        soup = fetch_page_reviews(page_url)
        if soup:
            reviews = extract_reviews(soup)
            all_reviews.extend(reviews)

            next_page_link = soup.select_one('a.pagination-link_next__SDNU4')
            if next_page_link:
                current_page += 1
            else:
                break 
        else:
            break  

    
    with open('reviews_data1.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Customer Name', 'Number of Reviews', 'Review Text', 'Rating', 'Review Date',
        ])
        writer.writeheader()
        for review in all_reviews:
            writer.writerow(review)

    print("Data has been extracted and saved to 'reviews_data.csv'")


start_url = "https://www.trustpilot.com/review/heightsfinance.com"
main(start_url)
