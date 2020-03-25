import bs4
import requests
import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import relationship
from pymongo import MongoClient


# Дом задание:
# Источник https://habr.com/ru/
#
# задача:
# Обойти ленту популярного за неделю
#
# сохранить данные в базы данных (Mongo, SQL)
# необходимые данные:
# - Загаловок статьи
# - Url статьи
# - количество комментариев в статье
# - дата и время публикации
# - автор (название и url)
# - авторы комментариев (название и url)
#
# для Mongo:
# создать коллекцию и все можно хранить в одной коллекции
#
# для SQL
# создать дополнительную таблицу для автора и автора комментариев и наладить связи

URL = 'https://habr.com/ru/top/weekly'
next_page = URL;
start_URL = 'https://habr.com'
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'}
response = requests.get(URL, headers = headers)
soup = bs4.BeautifulSoup(response.text, 'lxml')


Base = declarative_base()
class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_time = Column(String(50), unique=False, nullable=False)
    post_title = Column(String(300), unique=False, nullable=False)
    post_url = Column(String(300), unique=True, nullable=False)
    comments_count = Column(Integer, unique=False, nullable=True)
    autor_id = Column(Integer, ForeignKey('autor.id'))
    autor = relationship('Autor', back_populates='post')

    def __init__(self, date_time, title, url, comments_count, autor):
        self.date_time = date_time
        self.post_title = title
        self.post_url = url
        self.comments_count = comments_count
        self.autor = autor

class Autor(Base):
    __tablename__ = 'autor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), unique=False, nullable=False)
    url = Column(String(300), unique=True, nullable=False)
    post = relationship('Post', back_populates='autor')

    def get_or_create(name, url):
        exists = session.query(Autor.id).filter_by(name=name).scalar() is not None
        if exists:
            return session.query(Autor).filter_by(name=name).first()
        return Autor(name, url)

    def __init__(self, name, url):
        self.name = name
        self.url = url

def get_next_page_url():
    global soup
    if soup.find('a',{'id':'next_page'})['href']:
        return start_URL + soup.find('a',{'id':'next_page'})['href']
    else: return None

def format(str: str):
    str = str.replace("\n", '')
    return int(str)

posts_mn = {'data_time':'',
         'title':'',
         'url':'',
         'autor_name':'',
         'comments_count':int()}

autors_mn = {'name':'',
             'url':''}

def get_article_items():
    global response
    global soup
    global next_page
    while next_page:
        article_items = soup.find_all('a', {'class': 'post__title_link'})
        try:
            next_page = get_next_page_url()
            response = requests.get(next_page, headers = headers)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            next_page = None
        finally:
            time.sleep(1)
            for art in article_items:
                post_title = art.text
                post_url = art['href']
                post_res = requests.get(post_url, headers = headers)
                post_soup = bs4.BeautifulSoup(post_res.text, 'lxml')
                post_comments_count = format(post_soup.find('span',{'class':'comments-section__head-counter'}).text)
                post_data_time = post_soup.find('span',{'class':'post__time'})['data-time_published']
                post_autor_name = post_soup.header.find('span', {'class': 'user-info__nickname user-info__nickname_small'}).text
                post_autor_url = post_soup.header.find('a',{'class':'post__user-info user-info'})['href']
                print(f'post_title: {post_title} and its url: {post_url} , data_time_utc {post_data_time}')
                print(f'post_autor: {post_autor_name} and his url: {post_autor_url}')
                comments_autors = post_soup.find('ul',{'id':'comments-list'}).find_all('a',{'class':'user-info user-info_inline'})
                print(f'comments_count: {post_comments_count}')
                autor = Autor.get_or_create(post_autor_name,post_autor_url)
                post = Post(post_data_time, post_title, post_url, post_comments_count, autor)
                session.add(post)
                session.commit()
                posts_mn = {'data_time': post_data_time,
                            'title': post_title,
                            'url': post_url,
                            'autor_name': post_autor_name,
                            'comments_count': post_comments_count}
                db_mn['post'].insert_one(posts_mn)
                for comment_autor in comments_autors:
                    comment_autor_name = comment_autor['data-user-login']
                    comment_autor_url = comment_autor['href']
                    print(f'comment_autor_name: {comment_autor_name} and his url: {comment_autor_url}')
                    autor = Autor.get_or_create(comment_autor_name, comment_autor_url)
                    session.add(autor)
                    session.commit()
                    autors_mn = {'name': comment_autor_name,
                                 'url': comment_autor_url}
                    db_mn['autor'].insert_one(autors_mn)

if __name__ == '__main__':
    client_mn = MongoClient('mongodb://db_server:27017')
    db_mn = client_mn['habr_popular_per_week']
    engine = create_engine('mysql+mysqlconnector://root :xHs56XcgEvZQBSgw@db_server/habr_popular_per_week?charset=utf8')
    Base.metadata.create_all(engine)
    session_db = sessionmaker(bind=engine)
    session = session_db()
    get_article_items()
    engine.dispose()

