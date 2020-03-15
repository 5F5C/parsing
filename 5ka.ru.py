import requests
import json
import time


CAT_URL = "https://5ka.ru/api/v2/categories/"
OFFERS_URL = "https://5ka.ru/api/v2/special_offers/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}

def run():
    response = requests.get(CAT_URL, headers = HEADERS)
    cat_list = response.json()

    for cat in cat_list:
        cat_name = cat["parent_group_name"]
        cat_code = cat["parent_group_code"]

        data = get_data(OFFERS_URL, {'records_per_page': 20, 'categories': cat_code}, [])
        if len(data):
            with open(str(cat_name), 'w') as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))

def get_data(url, params, results):
    data = requests.get(url, headers = HEADERS, params = params).json()
    next_url = data.get('next')
    res_temp = data.get('results')
    results.extend(res_temp)
    time.sleep(1)
    if (next_url):
        get_data(next_url, params, results)
    return results

if __name__ == '__main__':
    run()

