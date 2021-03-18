import datetime
import json
import requests
import urllib3

import falcon

try:
    import model
    import util
except ModuleNotFoundError:
    print('common package not in python path')

logger = util.Logger(__name__)


CRAWLER_ENDPOINT = 'https://crawler.run-it-down.lol/'
REPORT_ENDPOINT = 'https://reporter.run-it-down.lol/'


class Main:

    def on_post(self, req, resp):
        logger.info('calling core')
        body = json.loads(req.stream.read())

        # surpress tls check
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # parse request
        rr = model.AnalyseRequest(
            summoner_name=body['summonerName'],
            summoner_name_buddy=body['summonerNameBuddy'],
            request_time=datetime.datetime.now().isoformat(),
            analyse_range=(body['startIndex'], body['endIndex']) if body.get('startIndex') and body.get('endIndex') else None,
        )

        # execute crawler
        # TODO remove hardcoded range
        header = {
            'X-Riot-Token': body['XRiotToken'],
            'endpoint': 'https://euw1.api.riotgames.com/'
        }
        logger.info('calling crawler')
        for summoner_name in (rr.summoner_name, rr.summoner_name_buddy):
            data = {
                'summonerName': summoner_name,
                'startIndex': rr.analyse_range[0] if rr.analyse_range,
                'endIndex': rr.analyse_range[1] if rr.analyse_range,
            }
            requests.post(url=CRAWLER_ENDPOINT, data=data, headers=header)

        # get report
        report = requests.get(url=REPORT_ENDPOINT, params={'summonerName': rr.summoner_name})

        # return report
        resp.body = report.content


def create():
    api = falcon.API()
    api.add_route('/', Main())
    logger.info('falcon initialized')
    return api


application = create()
