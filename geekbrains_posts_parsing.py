import json
import requests
import bs4
import time

URL = "https://geekbrains.ru/posts"
start_URL = "https://geekbrains.ru"
tags_set = {
    "tag_name": {'url': "", 'posts': ['url_post', ]}
}
articles_set = {
    'url': 'post_url',
    'title': 'Загаловок',
    'writer': {'name': 'wrater_name',
               'url': 'full_writer_url'
               },
    'tags': [{'tag_name':'tag_url'}, ]
}

response = requests.get(URL)
soup = bs4.BeautifulSoup(response.text, 'lxml')

def clear_file_name(url: str):
    return url.replace('/', '_')

def get_next_page(soup: bs4):
    next = soup.body.find('ul', {'class': 'gb__pagination'})
    try:
        next = next.find(lambda tag: tag.name == 'a' and tag.text == '›')['href']
    except: return None
    return start_URL + next

def get_articles():
    return soup.body.find_all('a', {'class': 'post-item__title h3 search_text'})

if __name__ == '__main__':
    while get_next_page(soup):
        next_page = get_next_page(soup)
        time.sleep(1)
        articles = get_articles()
        response = requests.get(next_page)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        for art in articles:
            post_url = start_URL + art.get('href')
            post_title = art.text
            print(f'{post_title}: {post_url}')
            res = requests.get(post_url)
            post_soup = bs4.BeautifulSoup(res.text, 'lxml')
            post_tags = post_soup.find_all('a',{'class':'small'})
            writer_name = post_soup.find('div', {'itemprop': 'author'}).text
            writer_url = f"{start_URL}{post_soup.find('div',{'itemprop': 'author'}).parent['href']}"
            tags = {}
            for tag in post_tags:
                tags.update({tag.text:start_URL + tag['href']})
                if not tags_set.get(tag.text):
                    tags_set.update({tag.text: {'url': tag['href'], 'posts': [post_url]}})
                else:
                    tags_set[tag.text]['posts'].append(post_url)
            articles_set = {'url': post_url, 'title': post_title, 'writer': {'name': writer_name, 'url': writer_url},
                                 'tags': tags}
            with open(f'{clear_file_name(post_url)}.json', 'w') as file:
                file.write(json.dumps(articles_set))
    with open('tags.json', 'w') as file:
        file.write(json.dumps(tags_set))



