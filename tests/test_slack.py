import requests_mock

from freepacktbook.slack import SlackNotification


def test_should_notify():
    channel = '#abc'
    slack_url = 'http://my.slack.com'
    slack_notification = SlackNotification(slack_url, channel)
    data = {
        'title': 'ttt',
        'url': 'someUrl.com',
        'image_url': 'aa.com',
        'book_url': 'bu',
        'description': 'desc'}

    with requests_mock.mock() as req_mock:
        req_mock.post(slack_url)
        slack_notification.notify(data)
        assert req_mock.called is True
        assert req_mock.called_once is True


def test_should_not_notify():
    channel = '#abc'
    slack_url = None
    slack_notification = SlackNotification(slack_url, channel)
    data = {
        'title': 'ttt',
        'url': 'someUrl.com',
        'image_url': 'aa.com',
        'book_url': 'bu',
        'description': 'desc'}

    with requests_mock.mock() as req_mock:
        req_mock.post(slack_url)
        slack_notification.notify(data)
        assert req_mock.called is False
