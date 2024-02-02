# Telegram News Scraper

## License

This project is licensed under the [MIT License](LICENSE).

## Description

The Telegram News Scraper is a Python script that scrapes news articles from a specified website and posts them to a Telegram chat. It checks for new articles and only posts those published within the last week.



## Install requirements
run in terminal

```bash
    pip install -r requirements.txt
```

## Usage
1. Make sure you have installed the required dependencies as mentioned above.
2. Configure your Telegram bot token and chat ID in the constants.py file.
3. Run the script using the following command:
```bash Copy code
    python main.py
```

## Notice

posted_news.pkl keeps a track of already sent messages to avoid duplicate news, delete it to restart