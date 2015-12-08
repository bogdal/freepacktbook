import json
import requests


class SlackNotification(object):

    def __init__(self, slack_url, channel):
        self.slack_url = slack_url
        self.channel = channel

    def notify(self, data):
        if not all([self.slack_url, self.channel]):
            return
        payload = {
            'channel': self.channel,
            'username': 'PacktPub Free Learning',
            'icon_emoji': ':books:',
            'attachments': [{
                'fallback': 'Today\'s Free eBook: %s' % data['title'],
                'pretext': 'Today\'s Free eBook:',
                'color': '#ff7f00',
                'fields': [{
                    'title': data['title'],
                    'value': '%s %s' % (
                        data['description'], data['url']),
                    'short': False
                }]
            }]}
        requests.post(self.slack_url, data={'payload': json.dumps(payload)})
