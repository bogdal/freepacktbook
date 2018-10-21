import os
import json
from sys import version_info

from mock import mock_open, patch
import pytest
import requests_mock
import requests

from freepacktbook.slack import SlackNotification

def test_should_notify():
    channel = '#abc'
    slackUrl = 'http://my.slack.com'
    slackNotif = SlackNotification(slackUrl, channel)	
    data= {'title': 'ttt', 'url': 'someUrl.com', 'image_url': 'aa.com', 'book_url': 'bu', 'description': 'desc'}

    with requests_mock.mock() as m:
	m.post(slackUrl)
	slackNotif.notify(data)
	assert m.called is True
	assert m.called_once is True       

def test_should_not_notify():
    channel = '#abc'
    slackUrl = None
    slackNotif = SlackNotification(slackUrl, channel)	
    data= {'title': 'ttt', 'url': 'someUrl.com', 'image_url': 'aa.com', 'book_url': 'bu', 'description': 'desc'}

    with requests_mock.mock() as m:
        m.post(slackUrl)
        slackNotif.notify(data)
        assert m.called is False

