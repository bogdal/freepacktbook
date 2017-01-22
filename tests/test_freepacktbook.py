import os
from sys import version_info

import pytest

from freepacktbook import FreePacktBook, InvalidCredentialsError
from mock import mock_open, patch
from vcr import VCR

if version_info.major == 2:
    import __builtin__ as builtins
else:
    import builtins


vcr = VCR(path_transformer=VCR.ensure_suffix('.yaml'),
          cassette_library_dir=os.path.join('tests', 'cassettes'))

BOOK_TITLE = 'Multithreading in C# 5.0 Cookbook'
BOOK_SLUG = 'multithreading_in_c_5_0_cookbook'
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
    assert books[0]['title'] == BOOK_TITLE


@vcr.use_cassette
def test_download_book(packtpub_client, monkeypatch):
    monkeypatch.setattr('freepacktbook.path.exists', lambda x: False)
    monkeypatch.setattr('freepacktbook.mkdir', lambda x: None)
    book = packtpub_client.claim_free_ebook()
    with patch.object(builtins, 'open', mock_open()) as result:
        packtpub_client.download_book(
            book, destination_dir='/test',formats=['epub'])
    assert result.call_args[0][0] == '/test/%s/%s.epub' % (
        BOOK_TITLE, BOOK_SLUG,)


@vcr.use_cassette
def test_download_code_files(packtpub_client, monkeypatch):
    monkeypatch.setattr('freepacktbook.path.exists', lambda x: False)
    monkeypatch.setattr('freepacktbook.mkdir', lambda x: None)
    book = packtpub_client.claim_free_ebook()
    with patch.object(builtins, 'open', mock_open()) as result:
        packtpub_client.download_code_files(
            book, destination_dir='/test')
    assert result.call_args[0][0] == '/test/%s/%s_code.zip' % (
        BOOK_TITLE, BOOK_SLUG,)


@vcr.use_cassette
def test_user_credentials():
    client = FreePacktBook('fake@user.com', 'not-real')
    with pytest.raises(InvalidCredentialsError):
        client.my_books()
