from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def fetch_prices(product_name):
    prices = []
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://www.google.com/search?sca_esv=&q={product_name}&tbm=shop"

    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for item in soup.find_all('div', {'class': 'sh-dgr__grid-result'}):
            store_element = item.find('div', {'class': 'aULzUe IuHnof'})
            if store_element:
                store = store_element.text
            else:
                store = 'Unknown Store'
            
            title_element = item.find('h3', {'class': 'tAxDx'})
            if title_element:
                title = title_element.text
            else:
                title = 'Unknown Product'

            link_element = item.find('a', {'class': 'shntl'})
            if link_element:
                link = "https://www.google.com" + link_element['href']
            else:
                link = '#'

            if product_name.lower() in title.lower():
                price_text = item.find('span', {'class': 'a8Pemb'}).text
                price = extract_price(price_text)
                if price:
                    prices.append((store, title, price, link))
    except Exception as e:
        print(f"Error fetching prices from {url}: {e}")

    driver.quit()
    return prices

def extract_price(price_text):
    try:
        price_text = price_text.replace('₽', '').replace('руб.', '').replace(',', '').replace('\xa0', '').strip()
        return float(price_text)
    except ValueError:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['product_name']
        prices = fetch_prices(product_name)
        if prices:
            min_price, min_store, min_link = min(prices, key=lambda x: x[2])[2], min(prices, key=lambda x: x[2])[0], min(prices, key=lambda x: x[2])[3]
            max_price, max_store, max_link = max(prices, key=lambda x: x[2])[2], max(prices, key=lambda x: x[2])[0], max(prices, key=lambda x: x[2])[3]
            avg_price = sum(price[2] for price in prices) / len(prices)
        else:
            min_price = max_price = avg_price = min_store = max_store = min_link = max_link = 'Не найдено'
        return render_template('index.html', product_name=product_name, prices=prices, 
                               min_price=min_price, min_store=min_store, min_link=min_link, 
                               max_price=max_price, max_store=max_store, max_link=max_link, 
                               avg_price=avg_price)
    
    return render_template('index.html', prices=[])

if __name__ == '__main__':
    app.run(debug=True)
