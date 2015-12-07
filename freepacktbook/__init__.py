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


def claim_free_ebook():
    client = FreePacktBook(
        os.environ.get('PACKTPUB_EMAIL'), os.environ.get('PACKTPUB_PASSWORD'))
    client.claim_free_ebook()
