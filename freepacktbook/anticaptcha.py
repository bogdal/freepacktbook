import time

import requests


class AnticaptchaError(Exception):
    pass


class Anticaptcha(object):

    base_url = 'https://api.anti-captcha.com'
    create_task_url = base_url + '/createTask'
    get_task_result_url = base_url + '/getTaskResult'
    language_pool = 'en'
    soft_id = 850

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def _post(self, url, **kwargs):
        response = self.session.post(url, **kwargs).json()
        if response.get('errorId'):
            raise AnticaptchaError(response.get('%s: %s' % (
                response.get('errorCode'), response.get('errorDescription'))))
        return response

    def _create_task(self, url, site_key):
        data = {
            'clientKey': self.api_key,
            'task': {
                'type': 'NoCaptchaTaskProxyless',
                'websiteURL': url,
                'websiteKey': site_key},
            'softId': self.soft_id,
            'languagePool': self.language_pool}
        response = self._post(self.create_task_url, json=data)
        return response.get('taskId')

    def _get_task_result(self, task_id):
        data = {
            'clientKey': self.api_key,
            'taskId': task_id}
        return self._post(self.get_task_result_url, json=data)

    def _wait_for_task_result(self, task_id):
        result = self._get_task_result(task_id)
        if result.get('status') == 'ready':
            return result
        time.sleep(2)
        return self._wait_for_task_result(task_id)

    def get_recaptcha_response(self, url, site_key):
        task_id = self._create_task(url, site_key)
        result = self._wait_for_task_result(task_id)
        return result['solution']['gRecaptchaResponse']
