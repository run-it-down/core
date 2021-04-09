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


# REPORT_ENDPOINT = 'http://127.0.0.1:1338'


class Analyze:

    def on_get(self, req, resp):
        logger.info('/GET analyze')
        body = json.loads(req.stream.read())

        # surpress tls check
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # parse request
        rr = model.AnalyseRequest(
            summoner_name=body['summonerName'],
            summoner_name_buddy=body['summonerNameBuddy'],
            request_time=datetime.datetime.now().isoformat(),
        )
        logger.info(f'{rr.summoner_name=}, {rr.summoner_name_buddy=}')

        logger.info('check summoner existence')
        not_found = False
        missing_summoners = []
        # check if both summoners exist. if not, return who does not exist
        for summoner_name in (rr.summoner_name, rr.summoner_name_buddy):
            res = requests.get(url=CRAWLER_ENDPOINT, params={'summoner': summoner_name})
            if res.status_code == falcon.HTTP_NOT_FOUND:
                missing_summoners.append(summoner_name)
                not_found = True

        if not_found:
            resp.status = falcon.HTTP_NOT_FOUND
            resp.text = {f'{", ".join(missing_summoners)} not existent.'}
            return

        logger.info('calling reporter')
        # get report
        report = requests.get(
            url=REPORT_ENDPOINT,
            params={'summoner1': rr.summoner_name, 'summoner2': rr.summoner_name_buddy},
        )

        # return report
        logger.info('reporting done')
        resp.text = report.content


class Crawl:
    def on_post(self, req, resp):
        logger.info('POST /crawl')
        body = json.loads(req.stream.read())

        # surpress tls check
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # parse request
        rr = model.AnalyseRequest(
            summoner_name=body['summonerName'],
            summoner_name_buddy=body['summonerNameBuddy'],
            request_time=datetime.datetime.now().isoformat(),
        )

        logger.info(f'{rr.summoner_name=}, {rr.summoner_name_buddy=}')

        # parsing token
        header = {
            'X-Riot-Token': req.headers['X-RIOT-TOKEN'],
            'ENDPOINT': 'https://euw1.api.riotgames.com/'
        }

        logger.info('calling crawler')
        for summoner_name in (rr.summoner_name, rr.summoner_name_buddy):
            res = requests.post(
                url=CRAWLER_ENDPOINT,
                json={'summonerName': summoner_name, },
                headers=header
            )
            logger.info(res)
        logger.info('crawling done')


def create():
    api = falcon.API()
    api.add_route('/analyze', Analyze())
    api.add_route('/crawl', Crawl())
    logger.info('falcon initialized')
    return api


application = create()
