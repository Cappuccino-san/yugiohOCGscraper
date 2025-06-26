import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Step 1: Fetch card list from YGOPRODeck API (proxy for Yugipedia bulk data)
YGOPRO_API = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?format=ocg'

print('Fetching card list from YGOPRODeck API...')
resp = requests.get(YGOPRO_API)
data = resp.json()

cards = []
for card in data['data']:
    card_id = card.get('id', '')
    name_en = card.get('name', '')
    name_jp = card.get('ja_name', '')  # Not always present
    sets = ', '.join([s['set_name'] for s in card.get('card_sets', [])])
    rarity = ', '.join([s['set_rarity'] for s in card.get('card_sets', [])])
    cards.append({
        'Card ID': card_id,
        'Name (EN)': name_en,
        'Name (JP)': name_jp,
        'Set(s)': sets,
        'Rarity': rarity,
        'Value (JPY)': '',
        'Value Date': ''
    })

print(f'Total cards fetched: {len(cards)}')

# Step 2: Scrape prices from Yuyu-tei (Japanese card shop)
def get_yuyutei_price(card_name_jp):
    if not card_name_jp:
        return None, None
    search_url = f'https://yuyu-tei.jp/sell/sell_price.php?name={requests.utils.quote(card_name_jp)}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(search_url, headers=headers)
    if resp.status_code != 200:
        return None, None
    soup = BeautifulSoup(resp.text, 'lxml')
    price_tag = soup.find('span', class_='price')
    if price_tag:
        price = price_tag.text.replace('円', '').replace(',', '').strip()
        value_date = time.strftime('%Y-%m-%d')
        return price, value_date
    return None, None

print('Fetching prices from Yuyu-tei (this may take a while)...')
for card in cards:
    name_jp = card['Name (JP)']
    if name_jp:
        price, value_date = get_yuyutei_price(name_jp)
        if price:
            card['Value (JPY)'] = price
            card['Value Date'] = value_date
    time.sleep(0.5)  # Be polite to the server

# Step 3: Output to CSV
print('Saving to yugioh_ocg_cards_with_prices.csv...')
df = pd.DataFrame(cards)
df.to_csv('yugioh_ocg_cards_with_prices.csv', index=False, encoding='utf-8-sig')
print('Done!') 