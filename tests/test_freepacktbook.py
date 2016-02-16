import os

import pytest

from freepacktbook import FreePacktBook, InvalidCredentialsError
from vcr import VCR


vcr = VCR(path_transformer=VCR.ensure_suffix('.yaml'),
          cassette_library_dir=os.path.join('tests', 'cassettes'))

BOOK_TITLE = 'Multithreading in C# 5.0 Cookbook'
BOOK_ID = '12544'


@pytest.fixture
def packtpub_client():
    return FreePacktBook('test@example.com', 'mypassword')


@vcr.use_cassette
def test_claim_free_ebook(packtpub_client):
    book = packtpub_client.claim_free_ebook()
    assert book['title'] == BOOK_TITLE
    assert book['id'] == BOOK_ID


@vcr.use_cassette
def test_my_books(packtpub_client):
    books = packtpub_client.my_books()
    assert books[0]['id'] == BOOK_ID
    assert books[0]['title'] == '%s [eBook]' % (BOOK_TITLE,)


@vcr.use_cassette
def test_user_credentials():
    client = FreePacktBook('fake@user.com', 'not-real')
    with pytest.raises(InvalidCredentialsError):
        client.my_books()
