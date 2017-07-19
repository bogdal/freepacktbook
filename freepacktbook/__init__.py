from os import environ
from argparse import ArgumentParser, HelpFormatter
from operator import attrgetter

from .anticaptcha import Anticaptcha
from .freepacktbook import FreePacktBook, FreePacktBookAnticaptcha
from .slack import SlackNotification
from .utils import env_variables_required, check_config

__all__ = [
    'Anticaptcha',
    'FreePacktBook', 'FreePacktBookAnticaptcha',
    'SlackNotification']


def download_parser(description):

    class SortedHelpFormatter(HelpFormatter):
        def add_arguments(self, actions):
            actions = sorted(actions, key=attrgetter('option_strings'))
            super(SortedHelpFormatter, self).add_arguments(actions)

    parser = ArgumentParser(description=description, formatter_class=SortedHelpFormatter)
    parser.add_argument(
        '--force', action='store_true', help='override existing files')
    parser.add_argument(
        '--formats', nargs='+', metavar='FORMAT',
        help='ebook formats (epub, mobi, pdf)')
    parser.add_argument(
        '--with-code-files', action='store_true', help='download code files')
    return parser


@env_variables_required(['PACKTPUB_EMAIL', 'PACKTPUB_PASSWORD', 'ANTICAPTCHA_KEY'])
def claim_free_ebook():
    parser = download_parser('Claim Free PacktPub eBook')
    parser.add_argument(
        '--download', action='store_true', help='download ebook')
    parser.add_argument(
        '--slack', action='store_true', help='send Slack notification')
    env_args = environ.get('PACKTPUB_ARGS')
    args = parser.parse_args(env_args.split() if env_args else None)
    if args.download:
        check_config(['PACKTPUB_BOOKS_DIR'])

    client = FreePacktBookAnticaptcha(
        anticaptcha_key=environ.get('ANTICAPTCHA_KEY'),
        email=environ.get('PACKTPUB_EMAIL'),
        password=environ.get('PACKTPUB_PASSWORD'))
    book = client.claim_free_ebook()

    if args.download:
        download_ebooks(client, parser, [book])

    if args.slack:
        slack_notification = SlackNotification(
            environ.get('SLACK_URL'), environ.get('SLACK_CHANNEL'))
        slack_notification.notify(book)
    print(book['title'])


@env_variables_required([
    'PACKTPUB_EMAIL', 'PACKTPUB_PASSWORD', 'PACKTPUB_BOOKS_DIR'])
def download_ebooks(client=None, parser=None, books=None):
    if parser is None:
        parser = download_parser('Download all my ebooks')
    args = parser.parse_args()
    if client is None:
        client = FreePacktBook(
            environ.get('PACKTPUB_EMAIL'), environ.get('PACKTPUB_PASSWORD'))
    if books is None:
        books = client.my_books()
    formats = args.formats
    if formats:
        formats = filter(lambda x: x in client.book_formats, formats)
    for book in books:
        kwargs = {
            'book': book,
            'destination_dir': environ.get('PACKTPUB_BOOKS_DIR'),
            'override': args.force}
        client.download_book(formats=formats, **kwargs)
        if args.with_code_files:
            client.download_code_files(**kwargs)
