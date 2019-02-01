import os
import time
import re
import io

import json
import datetime
from datetime import timedelta
import requests
import backoff
import singer
from singer import utils, metrics


REQUIRED_CONFIG_KEYS = ["guid", "company_id", "start_date"]
BASE_URL = "https://reports.revenuestripe.com/company/"
DATE_FORMAT = "%Y-%m-%d"

CONFIG = {}
STATE = {}

LOGGER = singer.get_logger()
SESSION = requests.session()

def get_abs_path(path):
    """get absolute path"""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schema():
    """get the schema"""
    return utils.load_json(get_abs_path("schemas/schema.json"))

def get_start_date(key):
    """get the start_date form state"""
    if key not in STATE:
        STATE[key] = CONFIG["start_date"]

    return STATE[key]

def on_giveup(details):
    """giveup logic for backoff"""
    url = details["args"]
    raise Exception("Giving up on request after {} tries with url {} " \
                    .format(details["tries"], url))

"""Calls to the API is limited to a maximum of 3 tries if a request isn't completed successfully.
The tap should remain well below this max during normal use. """

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_tries=3,
                      on_giveup=on_giveup,
                      factor=2)
@utils.ratelimit(9, 1)

def request(endpoint):
    """make the get request to endpoint"""
    url = endpoint
    req = requests.Request("GET", url).prepare()

    with metrics.http_request_timer(url) as timer:
        resp = SESSION.send(req)
        timer.tags[metrics.Tag.http_status_code] = resp.status_code

    json_body = resp.json()
    resp.raise_for_status()
    return json_body

def do_sync(guid, company_id, start_date):
    """Use the request function to get data and write the schema and response to singer"""
    schema = load_schema()
    LOGGER.info("---------- Writing Schema ----------")
    singer.write_schema("powerinbox_response", schema, "stripe")

    LOGGER.info("---------- Starting sync ----------")

    pickup_date = get_start_date("start_date")
    if (pickup_date):
        next_date = pickup_date
    else:
        next_date = start_date

    try:
        while next_date < utils.strftime(utils.now(), DATE_FORMAT):

            ext_url = ("{company_id}/{guid}/all_stripe/{date}.json"
                       .format(company_id=company_id, guid=guid, date=next_date))

            response = request(BASE_URL+ext_url)

            with metrics.record_counter(BASE_URL+ext_url) as counter:
                for record in response:
                    singer.write_records("powerinbox_response", [record])
                    utils.update_state(STATE, "start_date", next_date.encode("ascii", "ignore"))
                    counter.increment()

            next_date = utils.strftime((utils.strptime_to_utc(next_date)+
                                        timedelta(days=1)), DATE_FORMAT)

    except Exception as exc:
        LOGGER.critical(exc)
        singer.write_state(STATE)
        raise exc

    singer.write_state(STATE)
    LOGGER.info("---------- Completed sync ----------")

def main():
    """main function"""
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    CONFIG.update(args.config)
    STATE.update(args.state)
    guid = CONFIG["guid"]
    company_id = CONFIG["company_id"]
    start_date = CONFIG.get("start_date")
    do_sync(guid, company_id, start_date)

if __name__ == "__main__":
    main()
