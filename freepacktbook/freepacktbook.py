from os import makedirs, path, rename
import datetime
import json
import logging
import random
import re

import requests
from slugify import slugify
from tqdm import tqdm

from .anticaptcha import Anticaptcha
from .utils import ImproperlyConfiguredError


logger = logging.getLogger(__name__)

user_agents = [
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36",
]


class InvalidCredentialsError(Exception):
    pass


class Session(requests.Session):
    def request(self, method, url, **kwargs):
        logger.debug("%s: %s" % (method, url))
        return super(Session, self).request(method, url, **kwargs)


class FreePacktBook(object):

    base_url = "https://www.packtpub.com"
    url = base_url + "/packt/offers/free-learning"
    book_details_url = "https://static.packt-cdn.com/products/%(book_id)s/summary"
    offer_url = "https://services.packtpub.com/free-learning-v1/offers"
    claim_url = "https://services.packtpub.com/free-learning-v1/users/%(user_uuid)s/claims/%(offer_id)s"
    my_books_url = "https://services.packtpub.com/entitlements-v1/users/me/products"
    download_url = "https://services.packtpub.com/products-v1/products/%(book_id)s/files/%(format)s"

    book_formats = ["epub", "mobi", "pdf"]

    def __init__(self, email=None, password=None):
        self.session = Session()
        self.session.headers.update({"User-Agent": random.choice(user_agents)})
        self.email = email
        self.password = password

    def auth_required(func, *args, **kwargs):
        def decorated(self, *args, **kwargs):
            if "access_token_live" not in self.session.cookies:
                self.session.post(
                    self.url,
                    {
                        "email": self.email,
                        "password": self.password,
                        "form_id": "packt_user_login_form",
                    },
                )
                if "access_token_live" not in self.session.cookies:
                    raise InvalidCredentialsError()
                access_token = self.session.cookies["access_token_live"]
                self.session.headers.update(
                    {"Authorization": "Bearer %s" % access_token}
                )
            return func(self, *args, **kwargs)

        return decorated

    def download_file(self, url, file_path, override=False):
        if not path.exists(path.dirname(file_path)):
            makedirs(path.dirname(file_path))
        if not path.exists(file_path) or override:
            response = self.session.get(url, stream=True)
            total = int(response.headers.get("Content-Length", 0))
            if not total:
                return
            filename = path.split(file_path)[1]
            chunk_size = 1024
            progress = tqdm(
                total=total,
                leave=True,
                unit_scale=chunk_size,
                unit="B",
                desc="Downloading %s" % (filename,),
            )
            temp_file_path = "%s_incomplete" % (file_path,)
            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        progress.update(chunk_size)
            rename(temp_file_path, file_path)
            progress.close()

    def get_recaptcha_response(self, site_key):
        raise ImproperlyConfiguredError("Captcha solver is required.")

    @auth_required
    def should_claim(self, book):
        response = self.session.get(self.my_books_url, params={"search": book["title"]})
        return "count" not in response.json()

    @auth_required
    def claim_free_ebook(self):
        offer = self.get_offer()
        book = self.get_book_details(offer["book_id"])
        if self.should_claim(book):
            keys = self.get_claim_keys()
            url = self.claim_url % {
                "user_uuid": keys["user_uuid"],
                "offer_id": offer["offer_id"],
            }
            data = json.dumps(
                {"recaptcha": self.get_recaptcha_response(keys["site_key"])}
            )
            data = self.session.put(url, data=data).json()
            if "errorCode" in data:
                raise Exception(data["message"])
        return book

    def get_offer(self):
        today = datetime.date.today()
        response = self.session.get(
            self.offer_url,
            params={"dateFrom": today, "dateTo": today + datetime.timedelta(days=1)},
        )
        data = response.json()["data"][0]
        return {"offer_id": data["id"], "book_id": data["productId"]}

    def get_book_details(self, book_id):
        response = self.session.get(self.book_details_url % {"book_id": book_id})
        return response.json()

    @auth_required
    def get_claim_keys(self):
        response = self.session.get(self.url)
        return {
            "site_key": re.search(
                "Packt.offers.onLoadRecaptcha\('(.+?)'\)", response.text
            ).groups()[0],
            "user_uuid": re.search('uuid":"(.+?)"', response.text).groups()[0],
        }

    @auth_required
    def download_book(self, book, destination_dir=".", formats=None, override=False):
        title = book["title"]
        if formats is None:
            formats = self.book_formats
        for book_format in formats:
            url = self.download_url % {
                "book_id": book["productId"],
                "format": book_format,
            }
            response = self.session.get(url).json()
            if "data" in response:
                book_url = response["data"]
                slug = slugify(title, separator="_")
                file_path = "%s/%s/%s.%s" % (destination_dir, title, slug, book_format)
                if book_format == "code":
                    file_path = "%s/%s/%s_code.zip" % (destination_dir, title, slug)
                self.download_file(book_url, file_path, override=override)

    @auth_required
    def download_code_files(self, book, destination_dir=".", override=False):
        return self.download_book(
            book, destination_dir, formats=["code"], override=override
        )

    @auth_required
    def my_books(self, max_pages=10):
        per_page = 25
        books = []
        for page_number in range(0, max_pages):
            data = self.session.get(
                self.my_books_url,
                params={
                    "sort": "createdAt:DESC",
                    "offset": page_number * per_page,
                    "limit": per_page,
                },
            ).json()
            books += [
                {"title": book["productName"], "productId": book["productId"]}
                for book in data["data"]
            ]
            if page_number * per_page + per_page > data["count"]:
                break

        return books


class FreePacktBookAnticaptcha(FreePacktBook):
    def __init__(self, anticaptcha_key, **kwargs):
        self.anticaptcha_key = anticaptcha_key
        super(FreePacktBookAnticaptcha, self).__init__(**kwargs)

    def get_recaptcha_response(self, site_key):
        anitcaptcha = Anticaptcha(self.anticaptcha_key)
        return anitcaptcha.get_recaptcha_response(self.url, site_key)
