import json
import requests


class SlackNotification(object):

    def __init__(self, client, slack_url, channel):
        self.client = client
        self.slack_url = slack_url
        self.channel = channel

    def claim_free_ebook(self):
        book_details = self.client.claim_free_ebook()
        if self.slack_url and self.channel:
            data = {
                'channel': self.channel,
                'username': 'PacktPub Free Learning',
                'icon_emoji': ':books:',
                'attachments': [{
                    'fallback': 'Today\'s Free eBook: %s' % book_details['title'],
                    'pretext': 'Today\'s Free eBook:',
                    'color': '#ff7f00',
                    'fields': [{
                        'title': book_details['title'],
                        'value': '%s %s' % (
                            book_details['description'], self.client.url),
                        'short': False
                    }]
                }]}
            requests.post(self.slack_url, data={'payload': json.dumps(data)})
        return book_details
