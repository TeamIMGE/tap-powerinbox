#!/usr/bin/env python3
"""A singer tap to make GET requests to Powerinbox - RevenueStripe."""

#make all imports
import json
import sys
import time
from datetime import datetime, timedelta
import requests
import singer
import backoff

#get the most recent date - add to the url
URL_DATE = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

#base_url to make the get request. params added later
BASE_URL = 'https://reports.revenuestripe.com/company/'

LOGGER = singer.get_logger()
SESSION = requests.Session()

#define the schema for the response
SCHEMA = {
    "type": [
        "null",
        "object"
    ],
    "additionalProperties": False,
    "properties": {
        "stripe": {
            "type": [
                "null",
                "integer"
            ]
        },
        "sub_id": {
            "type":  [
                "null",
                "string"
            ]
        },
        "unique_opens": {
            "type":  [
                "null",
                "integer"
            ]
        },
        "total_clicks": {
            "type":  [
                "null",
                "integer"
            ]
        },
        "net_revenue": {
            "type":  [
                "null",
                "string"
            ]
        },
        "date": {
            "type":  [
                "null",
                "string",
            ],
            "format": "date-time"
        }
    }
}

def giveup(error):
    """Look for errors """
    LOGGER.error(error.response.text)
    response = error.response
    return not (response.status_code == 429 or
                response.status_code >= 500)

@backoff.on_exception(backoff.constant,
                      (requests.exceptions.RequestException),
                      jitter=backoff.random_jitter,
                      max_time=100,
                      max_tries=5,
                      giveup=giveup,
                      interval=30)

def request(url, params):
    """Make the GET request"""
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response

def parse_response(values):
    """Format the output before writing to singer.write_records"""
    final = {}
    final['stripe'] = values['stripe']
    final['sub_id'] = values['sub_id']
    final['unique_opens'] = values['unique_opens']
    final['total_clicks'] = values['total_clicks']
    final['net_revenue'] = values['net_revenue']
    final['date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(values['date'], '%Y-%m-%d'))
    return final

def do_sync(guid, company_id, url_date):
    """Use the request function to get data and write the schema and response to singer"""
    LOGGER.info('Getting data from powerinbox')

    # company_id and guid pulled from config file and use date declared above
    ext_url = ('{company_id}/{guid}/all_stripe/{url_date}.json'
               .format(company_id=company_id, guid=guid, url_date=url_date))

    try:
        response = requests.get(BASE_URL+ext_url)
        payload = response.json()
        for record in payload:
            singer.write_schema('powerinbox_response', SCHEMA, 'stripe')
            singer.write_records('powerinbox_response', [parse_response(record)])

    except requests.exceptions.RequestException as err:
        LOGGER.fatal('Error on ' + err.request.url +
                     '; received status ' + str(err.response.status_code) +
                     ': ' + err.response.text)
        sys.exit(-1)

    LOGGER.info('Tap exiting normally')


def main():
    """Main function"""
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    do_sync(config['guid'], config['company_id'], URL_DATE)

if __name__ == '__main__':
    main()
