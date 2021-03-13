import json
import requests
import urllib3

import falcon

try:
    import util
except ModuleNotFoundError:
    print('common package not in python path')

logger = util.Logger(__name__)


CRAWLER_ENDPOINT = 'https://crawler.run-it-down.lol/summoner'
REPORT_ENDPOINT = 'https://crawler.run-it-down.lol/report'


class Solo:

    def on_post(self, req, resp):
        logger.info('POST /analyze/solo')
        body = json.loads(req.stream.read())

        # surpress tls check
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # execute crawler
        # TODO remove hardcoded range
        data = {
            'summonerName': body['summonerName'],
            'startIndex': '0',
            'endIndex': '10'
        }
        header = {
            'X-Riot-Token': body['XRiotToken'],
            'endpoint': 'https://euw1.api.riotgames.com/'
        }
        logger.info('calling crawler')
        res = requests.post(url=CRAWLER_ENDPOINT, data=data, headers=header)

        # get report
        if res.status_code == 201:
            params = {
                'summoner': body['summonerName']
            }
            report = requests.get(url=util.urljoin(REPORT_ENDPOINT, '/solo'), params=params)
        else:
            logger.error('calling crawler failed')

        # return report
        if report.status_code == 201:
            resp.body = report.content
            resp.status_code = 201
        else:
            logger.error('no report returned')


def create():
    api = falcon.API()
    api.add_route('/analyze/solo', Solo())
    logger.info('falcon initialized')
    return api


application = create()
