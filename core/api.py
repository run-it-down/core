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
        )

        # execute crawler
        header = {
            'X-Riot-Token': req.headers['X-RIOT-TOKEN'],
            'endpoint': 'https://euw1.api.riotgames.com/'
        }
        logger.info('calling crawler')
        for summoner_name in (rr.summoner_name, rr.summoner_name_buddy):
            requests.post(url=CRAWLER_ENDPOINT, json={'summonerName': summoner_name, }, headers=header)

        # get report
        report = requests.get(url=REPORT_ENDPOINT,
                              params={'summoner1': rr.summoner_name, 'summoner2': rr.summoner_name_buddy})

        # return report
        resp.body = report.content


def create():
    api = falcon.API()
    api.add_route('/', Main())
    logger.info('falcon initialized')
    return api


application = create()
