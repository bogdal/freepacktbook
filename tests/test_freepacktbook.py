import os
from sys import version_info

from mock import mock_open, patch
import pytest
import requests_mock
from vcr import VCR

from freepacktbook import FreePacktBook
from freepacktbook.freepacktbook import InvalidCredentialsError

if version_info.major == 2:
    import __builtin__ as builtins
else:
    import builtins


vcr = VCR(path_transformer=VCR.ensure_suffix('.yaml'),
          cassette_library_dir=os.path.join('tests', 'cassettes'))


@pytest.fixture
def packtpub_client():
    client = FreePacktBook('test@example.com', 'mypassword')
    client.session.cookies['SESS_live'] = 'test'
    return client


@vcr.use_cassette
def test_get_book_details(packtpub_client):
    book = packtpub_client.get_book_details()
    assert book['title'] == 'Git - Version Control for Everyone'
    assert book['id'] == '10558'


@vcr.use_cassette
def test_my_books(packtpub_client):
    books = packtpub_client.my_books()
    assert books[0]['id'] == '12544'
    assert books[0]['title'] == 'Multithreading in C# 5.0 Cookbook'


def test_download_book(packtpub_client, monkeypatch):
    monkeypatch.setattr('freepacktbook.freepacktbook.path.exists', lambda x: True)
    monkeypatch.setattr('freepacktbook.freepacktbook.rename', lambda *args: None)
    book = {
        'id': '1234',
        'title': 'Test Book'}
    with patch.object(builtins, 'open', mock_open()) as result:
        with requests_mock.mock() as m:
            url = packtpub_client.download_url % {
                'book_id': book['id'], 'format': 'epub'}
            m.get(url, headers={'Content-Length': '100'})
            packtpub_client.download_book(
                book, destination_dir='/test',formats=['epub'], override=True)
    assert result.call_args[0][0] == '/test/Test Book/test_book.epub_incomplete'


def test_download_code_files(packtpub_client, monkeypatch):
    monkeypatch.setattr('freepacktbook.freepacktbook.path.exists', lambda x: True)
    monkeypatch.setattr('freepacktbook.freepacktbook.rename', lambda *args: None)
    book = {
        'id': '1234',
        'title': 'Test Book'}
    with patch.object(builtins, 'open', mock_open()) as result:
        with requests_mock.mock() as m:
            url = packtpub_client.code_files_url % {'id': int(book['id']) + 1}
            m.get(url, headers={'Content-Length': '100'})
            packtpub_client.download_code_files(
                book, destination_dir='/test', override=True)
    assert result.call_args[0][0] == '/test/Test Book/test_book_code.zip_incomplete'


@vcr.use_cassette
def test_user_credentials():
    client = FreePacktBook('fake@user.com', 'not-real')
    with pytest.raises(InvalidCredentialsError):
        client.my_books()
