from os import environ, mkdir, path
import re

from bs4 import BeautifulSoup
import requests

from .slack import SlackNotification


class FreePacktBook(object):

    base_url = 'https://www.packtpub.com'
    download_url = base_url + '/ebook_download/%(book_id)s/%(format)s'
    my_books_url = base_url + '/account/my-ebooks'
    url = base_url + '/packt/offers/free-learning/'

    def __init__(self, email=None, password=None):
        self.session = requests.Session()
        self.email = email
        self.password = password

    def auth_required(func, *args, **kwargs):
        def decorated(self, *args, **kwargs):
            if 'SESS_live' not in self.session.cookies:
                self.session.post(self.url, {
                    'email': self.email,
                    'password': self.password,
                    'form_id': 'packt_user_login_form'})
            return func(self, *args, **kwargs)
        return decorated

    @auth_required
    def claim_free_ebook(self):
        book = self.get_book_details()
        response = self.session.get(book['claim_url'])
        assert response.status_code == 200
        book.update({'url': self.url})
        return book

    def get_book_details(self, page=None):
        if page is None:
            response = self.session.get(self.url)
            page = BeautifulSoup(response.text, 'html.parser')
        summary = page.find('div', {'class': 'dotd-main-book-summary'})
        main_book_image = page.find('div', {'class': 'dotd-main-book-image'})
        claim_url = page.find('div', {'class': 'free-ebook'}).a['href']
        book_id = re.search(r'claim/(\d+)/', claim_url).groups()[0]
        return {
            'title': summary.find('div', {'class': 'dotd-title'}).getText().strip(),
            'description': summary.find('div', {'class': None}).getText().strip(),
            'book_url': self.base_url + main_book_image.a['href'],
            'image_url': 'https:%s' % main_book_image.img['src'],
            'claim_url': self.base_url + claim_url,
            'id': book_id}

    @auth_required
    def download_book(self, book, destination_dir='.'):
        for book_format in ['epub', 'mobi', 'pdf']:
            url = self.download_url % {
                'book_id': book['id'], 'format': book_format}
            name = book['book_url'][book['book_url'].rfind('/')+1:]
            filename = '%s/%s.%s' % (destination_dir, name, book_format)
            response = self.session.get(url, stream=True)
            if not path.exists(destination_dir):
                mkdir(destination_dir)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

    @auth_required
    def my_books(self):
        books = []
        response = self.session.get(self.my_books_url)
        page = BeautifulSoup(response.text, 'html.parser')
        lines = page.find_all('div', {'class': 'product-line'})
        for line in lines:
            if not line.get('nid'):
                continue
            books.append({
                'title': line.find('div', {'class': 'title'}).getText().strip(),
                'book_url': self.base_url + line.find('div', {
                    'class': 'product-thumbnail'}).a['href'],
                'id': line['nid']})
        return books


def claim_free_ebook():
    client = FreePacktBook(
        environ.get('PACKTPUB_EMAIL'), environ.get('PACKTPUB_PASSWORD'))
    book = client.claim_free_ebook()

    if environ.get('PACKTPUB_BOOKS_DIR'):
        client.download_book(book, environ['PACKTPUB_BOOKS_DIR'])

    slack_notification = SlackNotification(
        environ.get('SLACK_URL'), environ.get('SLACK_CHANNEL'))
    slack_notification.notify(book)
