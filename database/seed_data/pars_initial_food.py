import requests
from bs4 import BeautifulSoup
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import SEED_FILE


def parce(URL, pages):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    all_products = []

    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1,
                  status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    for page in range(0, pages+1):
        for attempt in range(3):
            try:
                response = session.get(
                    URL + f'?page={page}', headers=headers, timeout=30)
                print(
                    f'Обрабатывается страница {page}. Статус: {response.status_code}')
                break  # Успешно - выходим из цикла попыток
            except requests.exceptions.SSLError as e:
                print(
                    f'Ошибка SSL на странице {page}, попытка {attempt+1}: {e}')
                if attempt == 2:
                    raise
                time.sleep(2)

        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find_all('tr', class_='odd') + \
            soup.find_all('tr', class_='even')
        for row in rows:
            title_cell = row.find('td', class_='views-field-title')
            if title_cell:
                name = title_cell.find('a').text.strip()
            else:
                continue

            protein = row.find('td', class_='views-field-field-protein-value')
            fat = row.find('td', class_='views-field-field-fat-value')
            carbs = row.find(
                'td', class_='views-field-field-carbohydrate-value')
            kcal = row.find('td', class_='views-field-field-kcal-value')

            def safe_float(value):
                if value and value.text:
                    cleaned = value.text.strip()
                    if cleaned and cleaned != '\n':
                        try:
                            return round(float(cleaned), 2)
                        except ValueError:
                            return 0.0
                return 0.0

            product = {
                'name': name,
                'calories': safe_float(kcal),
                'protein': safe_float(protein),
                'fat': safe_float(fat),
                'carbs': safe_float(carbs),
                'barcode': None,
                'is_custom': False,
            }
            print(f'Парсирование: {product}')
            all_products.append(product)
    return all_products


if __name__ == '__main__':
    file_path = SEED_FILE
    URL = 'https://calorizator.ru/product/all'
    foods = parce(URL, 86)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(foods, file, indent=4, ensure_ascii=False)
    print('ДАННЫЕ СОХРАНЕНЫ')
