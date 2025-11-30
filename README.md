# Levitt Pavilion

Automated concert notification system that scrapes Levitt Pavilion Denver's schedule and sends email alerts for upcoming free concerts.

## Overview

[Levitt Pavilion Denver](https://levittdenver.org/) hosts free outdoor concerts throughout the summer. This project automatically:

1. Scrapes the concert schedule from the Levitt Pavilion website
2. Identifies upcoming concerts
3. Sends email notifications via Gmail API

## Features

- **Web Scraping** - Uses Selenium to extract concert information
- **Gmail Integration** - Sends automated email notifications via Google Gmail API
- **Concert Tracking** - Maintains CSV of concerts with dates, artists, and details
- **Riverfront Concerts** - Also tracks Denver Riverfront concerts

## Data Collected

| Field | Description |
|-------|-------------|
| Date | Concert date |
| Artist | Performing artist/band |
| Genre | Music genre |
| Time | Show time |
| Venue | Location details |

## Setup

### Prerequisites

- Python 3.x
- Chrome browser
- Google Cloud project with Gmail API enabled

### Installation

```bash
pip install pandas selenium webdriver-manager google-api-python-client oauth2client pyyaml httplib2
```

### Gmail API Setup

1. Create a Google Cloud project
2. Enable the Gmail API
3. Create OAuth 2.0 credentials
4. Download `client_secret.json`
5. Configure `email_information_retrieval.yml` with your settings

## Usage

```python
# Run the main script
python levitt_pavilion_code.py

# This will:
# 1. Scrape current concert schedule
# 2. Compare with previously known concerts
# 3. Send email for any new concerts
```

## Files

| File | Description |
|------|-------------|
| `levitt_pavilion_code.py` | Main scraping and notification script |
| `concert_info_list_detailed_df.csv` | Detailed concert information |
| `riverfront_concerts_df.csv` | Riverfront concert data |

## Data Sources

- [Levitt Pavilion Denver](https://levittdenver.org/)
- Denver Riverfront concerts

## License

MIT
