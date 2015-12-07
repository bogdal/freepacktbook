import os

from bs4 import BeautifulSoup
import requests


class FreePacktBook(object):

    base_url = 'https://www.packtpub.com'
    url = base_url + '/packt/offers/free-learning/'

    def __init__(self, email=None, password=None):
        self.session = requests.Session()
        self.email = email
        self.password = password

    def claim_free_ebook(self):
        response = self.session.post(self.url, {
            'email': self.email,
            'password': self.password,
            'form_id': 'packt_user_login_form'})
        parser = BeautifulSoup(response.text, 'html.parser')
        claim_url = self.base_url + parser.find('div', {
            'class': 'free-ebook'}).a['href']
        response = self.session.get(claim_url)
        assert response.status_code == 200

    def get_book_details(self):
        response = self.session.get(self.url)
        parser = BeautifulSoup(response.text, 'html.parser')
        summary = parser.find('div', {'class': 'dotd-main-book-summary'})
        title = summary.find('div', {'class': 'dotd-title'}).getText().strip()
        description = summary.find('div', {'class': None}).getText().strip()
        main_book_image = parser.find('div', {'class': 'dotd-main-book-image'})
        image_url = 'https:%s' % main_book_image.img['src']
        url = self.base_url + main_book_image.a['href']
        return {'title': title, 'description': description,
                'url': url, 'image_url': image_url}


def claim_free_ebook():
    client = FreePacktBook(
        os.environ.get('PACKTPUB_EMAIL'), os.environ.get('PACKTPUB_PASSWORD'))
    client.claim_free_ebook()
