from os import environ

from bs4 import BeautifulSoup
import requests

from .slack import SlackNotification


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
        page = BeautifulSoup(response.text, 'html.parser')
        claim_url = page.find('div', {'class': 'free-ebook'}).a['href']
        response = self.session.get(self.base_url + claim_url)
        assert response.status_code == 200
        return self.get_book_details(page)

    def get_book_details(self, page=None):
        if page is None:
            response = self.session.get(self.url)
            page = BeautifulSoup(response.text, 'html.parser')
        summary = page.find('div', {'class': 'dotd-main-book-summary'})
        main_book_image = page.find('div', {'class': 'dotd-main-book-image'})
        return {
            'title': summary.find('div', {'class': 'dotd-title'}).getText().strip(),
            'description': summary.find('div', {'class': None}).getText().strip(),
            'url': self.url,
            'book_url': self.base_url + main_book_image.a['href'],
            'image_url': 'https:%s' % main_book_image.img['src']}


def claim_free_ebook():
    client = FreePacktBook(
        environ.get('PACKTPUB_EMAIL'), environ.get('PACKTPUB_PASSWORD'))
    book = client.claim_free_ebook()

    slack_notification = SlackNotification(
        environ.get('SLACK_URL'), environ.get('SLACK_CHANNEL'))
    slack_notification.notify(book)
