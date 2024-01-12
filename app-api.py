from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import OrderedDict
import time
import locale

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)


locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

# Function to scrape data from Americanas website
def scrape_americanas(query):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.headless = False

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.americanas.com.br/busca/{query}")

    time.sleep(10)

    items = {}

    search_results = driver.find_elements(By.CSS_SELECTOR, "[class*='product-name']")
    for k, result in enumerate(search_results[2:12], start=1):
        result_html = result.text
        items[k] = [str(result_html)]
        # print(f"Produto: {result_html}")

    product = driver.find_elements(By.CSS_SELECTOR, "[class*='ListPrice']")
    for i, result in enumerate(product[2:12], start=1):
        result_html = result.text
        items[i].append(result_html)
        items[i].append('americanas')
        # print(f"Preço: {result_html}")

    driver.quit()
    return items

# Function to scrape data from Amazon website
def scrape_amazon(query):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.headless = False

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.amazon.com.br/s?k={query}")

    time.sleep(3)

    items = {}

    search_results = driver.find_elements(By.CSS_SELECTOR, "[class*='a-size-base-plus']")
    for k, result in enumerate(search_results[0:10], start=1):
        result_html = result.text
        items[k] = [str(result_html)]
        # print(f"Produto: {result_html}")

    price = driver.find_elements(By.CSS_SELECTOR, "[class*='a-price-whole']")
    decimal = driver.find_elements(By.CSS_SELECTOR, "[class*='a-price-fraction']")
    for i, result in enumerate(price[0:10], start=1):
        result_html = result.text
        decimal_add = decimal[i-1].text
        items[i].append('R$ ' + str(result_html) + ',' + str(decimal_add))
        items[i].append('amazon')
        # print(f"Preço: {result_html}")

    # Add additional logic for scraping other details from Amazon if needed

    driver.quit()
    return items

# Function to combine data from both websites
def combine_data(americanas_data, amazon_data):
    combined_data = {}

    for key, value in americanas_data.items():
        combined_data[key] = value

    for key, value in amazon_data.items():
        combined_data[key + len(americanas_data)] = value

    combined_data_int = {}
    for i in combined_data:
        combined_data_int[i] = [combined_data[i][0], float(combined_data[i][1].replace('R$ ', '').replace('.', '').replace(',', '.')), combined_data[i][2]]

    # Convert to OrderedDict before sorting
    combined_data_ordered = dict(sorted(combined_data_int.items(), key=lambda item: item[1][1]))

    return combined_data_ordered

# Example usage:
@app.route('/api/scrape', methods=['GET'])
def scrape_data():
    query = request.args.get('query')
    americanas_data = scrape_americanas(query)
    amazon_data = scrape_amazon(query)

    combined_data = combine_data(americanas_data, amazon_data)

    return jsonify(combined_data)

if __name__ == '__main__':
    app.run(debug=True)
