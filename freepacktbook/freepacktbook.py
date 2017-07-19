from os import makedirs, path, rename
import logging
import random
import re

from bs4 import BeautifulSoup
import requests
from slugify import slugify
from tqdm import tqdm

from .anticaptcha import Anticaptcha
from .utils import ImproperlyConfiguredError


logger = logging.getLogger(__name__)

user_agents = [
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36']


class InvalidCredentialsError(Exception):
    pass


class Session(requests.Session):

    def request(self, method, url, **kwargs):
        logger.debug('%s: %s' % (method, url))
        return super(Session, self).request(method, url, **kwargs)


class FreePacktBook(object):

    base_url = 'https://www.packtpub.com'
    code_files_url = base_url + '/code_download/%(id)s'
    download_url = base_url + '/ebook_download/%(book_id)s/%(format)s'
    my_books_url = base_url + '/account/my-ebooks'
    url = base_url + '/packt/offers/free-learning'

    book_formats = ['epub', 'mobi', 'pdf']

    def __init__(self, email=None, password=None):
        self.session = Session()
        self.session.headers.update({'User-Agent': random.choice(user_agents)})
        self.email = email
        self.password = password

    def auth_required(func, *args, **kwargs):
        def decorated(self, *args, **kwargs):
            if 'SESS_live' not in self.session.cookies:
                response = self.session.post(self.url, {
                    'email': self.email,
                    'password': self.password,
                    'form_id': 'packt_user_login_form'})
                page = BeautifulSoup(response.text, 'html.parser')
                error = page.find('div', {'class': 'messages error'})
                if error:
                    raise InvalidCredentialsError(error.getText())
            return func(self, *args, **kwargs)
        return decorated

    def download_file(self, url, file_path, override=False):
        if not path.exists(path.dirname(file_path)):
            makedirs(path.dirname(file_path))
        if not path.exists(file_path) or override:
            response = self.session.get(url, stream=True)
            total = int(response.headers.get('Content-Length', 0))
            print(response.headers)
            print('total', total)
            if not total:
                return
            filename = path.split(file_path)[1]
            chunk_size = 1024
            progress = tqdm(
                total=total, leave=True, unit_scale=chunk_size, unit='B',
                desc='Downloading %s' % (filename,))
            temp_file_path = '%s_incomplete' % (file_path,)
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        progress.update(chunk_size)
            rename(temp_file_path, file_path)
            progress.close()

    def get_recaptcha_response(self, site_key):
        raise ImproperlyConfiguredError('Captcha solver is required.')

    @auth_required
    def claim_free_ebook(self):
        book = self.get_book_details()
        response = self.session.post(book['claim_url'], data={
            'g-recaptcha-response': self.get_recaptcha_response(book['site_key'])})
        assert response.url == self.my_books_url
        book.update({'url': self.url})
        return book

    def get_book_details(self, page=None):
        if page is None:
            response = self.session.get(self.url)
            page = BeautifulSoup(response.text, 'html.parser')
        summary = page.find('div', {'class': 'dotd-main-book-summary'})
        main_book_image = page.find('div', {'class': 'dotd-main-book-image'})
        claim_url = page.find('div', {'class': 'free-ebook'}).form['action']
        book_id = re.search(r'claim/(\d+)/', claim_url).groups()[0]
        title = summary.find('div', {'class': 'dotd-title'}).getText().strip()
        title = title.replace(':', ' -')
        return {
            'title': title,
            'description': summary.find('div', {'class': None}).getText().strip(),
            'book_url': self.base_url + main_book_image.a['href'],
            'image_url': 'https:%s' % main_book_image.img['src'],
            'claim_url': self.base_url + claim_url,
            'id': book_id,
            'site_key': re.search(
                "Packt.offers.onLoadRecaptcha\(\'(.+?)\'\)", page.getText()).groups()[0]}

    @auth_required
    def download_book(self, book, destination_dir='.', formats=None,
                      override=False):
        title = book['title']
        if formats is None:
            formats = self.book_formats
        for book_format in formats:
            url = self.download_url % {
                'book_id': book['id'], 'format': book_format}
            slug = slugify(title, separator='_')
            file_path = '%s/%s/%s.%s' % (destination_dir, title, slug, book_format)
            self.download_file(url, file_path, override=override)

    @auth_required
    def download_code_files(self, book, destination_dir='.', override=False):
        title = book['title']
        url = self.code_files_url % {'id': int(book['id']) + 1}
        file_path = '%s/%s/%s_code.zip' % (
            destination_dir, title, slugify(title, separator='_'))
        self.download_file(url, file_path, override=override)

    @auth_required
    def my_books(self):
        books = []
        response = self.session.get(self.my_books_url)
        page = BeautifulSoup(response.text, 'html.parser')
        lines = page.find_all('div', {'class': 'product-line'})
        for line in lines:
            if not line.get('nid'):
                continue
            title = line.find('div', {'class': 'title'}).getText().strip()
            title = title.replace(' [eBook]', '').replace(':', ' -')
            books.append({
                'title': title,
                'book_url': self.base_url + line.find('div', {
                    'class': 'product-thumbnail'}).a['href'],
                'id': line['nid']})
        return books


class FreePacktBookAnticaptcha(FreePacktBook):

    def __init__(self, anticaptcha_key, **kwargs):
        self.anticaptcha_key = anticaptcha_key
        super(FreePacktBookAnticaptcha, self).__init__(**kwargs)

    def get_recaptcha_response(self, site_key):
        anitcaptcha = Anticaptcha(self.anticaptcha_key)
        return anitcaptcha.get_recaptcha_response(self.url, site_key)
