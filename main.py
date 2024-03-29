import requests
from bs4 import BeautifulSoup
import constants
import os
import pickle
import time
from io import BytesIO
import datetime

# Set up the bot with the token and chat ID from constants
bot_token = constants.token
chat_id = constants.chat_id

# Check for the existence of a file to store posted news URLs.
# If it exists, load the data; if not, create a new set.
posted_news_file = './data/posted_news.txt'
if os.path.exists(posted_news_file):
    with open(posted_news_file, 'r') as f:
        posted_news = set(f.read().splitlines())
else:
    posted_news = set()

# URL of the news website to be scraped
url = 'https://shega.co/post/category/news/'


def send_telegram_photo(chat_id, photo, caption, token):
    """
    Send a photo to a Telegram chat.
    Args:
        chat_id (str): Telegram chat ID
        photo (BytesIO): Photo to be sent as a BytesIO object
        caption (str): Caption for the photo
        token (str): Telegram bot token
    Returns:
        dict: Response from Telegram API
    """
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    files = {
        'photo': photo.getvalue()
    }
    response = requests.post(url, data=payload, files=files)
    return response.json()


def send_telegram_message(chat_id, text, token):
    """
    Send a text message to a Telegram chat.
    Args:
        chat_id (str): Telegram chat ID
        text (str): Text message to be sent
        token (str): Telegram bot token
    Returns:
        dict: Response from Telegram API
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response.json()

def scrape_news():
    """
    Continuously scrape news from a specified URL and post it to a Telegram chat.
    Only posts from the last week are considered.
    """
    while True:
        try:
            response = requests.get(url, timeout=60)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all news posts on the page
            posts = soup.find_all(lambda tag: tag.name == 'div' and 'post' in tag.get('class', []))

            for post in posts:
                # Extract details from each post
                post_title = post.find('a', class_='entry-title').text.strip()
                post_url = post.find('a', class_='entry-title').get('href').strip()
                post_date = post.find('div', class_='post-metas caption-meta').find_all('li')[1].text.strip().replace('. ', '')
                post_author = post.find('span', class_='author').text.strip()
                post_overview = post.find('p').text.strip() + '...'
                post_tags = [tag.text.strip() for tag in post.find_all('a', class_="post-cat cat-btn")]
                formatted_post_tags = ' '.join([f'#{tag.replace(' ', '')}' for tag in post_tags])
                post_image_url = post.find('img').get('data-src')
                response = requests.get(post_image_url, timeout=60)
                post_photo = BytesIO(response.content)

                # Post the news if it's not already posted and is within the last month
                if post_url not in posted_news:
                    caption = (f"<b>{post_title}</b>\n\n"
                               f"By: {post_author},  {post_date}\n\n"
                               f"{post_overview}\n\n"
                               f"<a href=\"{post_url}\">Read more...</a>\n\n"
                               f"{formatted_post_tags}")
                    if post_photo:
                        send_telegram_photo(chat_id=chat_id, photo=post_photo, caption=caption, token=bot_token)
                    else:
                        send_telegram_message(chat_id=chat_id, text=caption, token=bot_token)

                    # Add the URL to the set of posted news and save it
                    posted_news.add(post_url)
                    with open(posted_news_file, 'a') as f:
                        f.write(post_url + '\n')


                    # Pause between processing each post
                    time.sleep(20)

            # Wait before scraping the page again
            time.sleep(900)

        # Handle exceptions and pause before retrying
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"HTTP Error: {e}")
            time.sleep(90)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(90)

if __name__ == '__main__':
    scrape_news()
