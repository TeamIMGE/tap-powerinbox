# tap-powerinbox
A singer tap to make GET requests to Powerinbox - RevenueStripe.

## Connecting Tap Powerinbox

### Requirements

To set up Tap Powerinbox in Stitch, you need the following from your Powerinbox account:
1. GUID
2. Company ID

### Setup

1. Retrieve your GUID from Powerinbox.
2. Retrieve your Company ID from Powerinbox.

Create a [config.json.example](https://github.com/TeamIMGE/tap-powerinbox/blob/master/config.json.example) file in the following format, where `guid` and `company_id` are the credentials you just retrieved. It also accepts an initial `start_date` (#format: 1990-01-01) which is the date the tap starts pulling data from.

```json
{
  "guid": "add-powerinbox-guid",
  "company_id": "add-powerinbox-company-id"
  "start_date": "add-start-date"
}
```

## Table Schemas

Each header denotes the table name.

### powerinbox_response
- Description: values returned from the GET request

| NAME          | TYPE   | DESCRIPTION  |
| :-----------: |:------:| :-----------------------------------------------------------------:|
| date          | string | The date in YYYY-MM-DD format (UTC)                                |
| stripe        | number | The stripe Id                                                      |
| sub_id        | string | The subId passed in the stripe url query parameter                 |
| unique_opens  | number | The unique number of stripe opens per user                         |
| total_clicks  | number | The total number of clicks                                         |
| net_revenue   | string | The net revenue in US dollars with two significant digits (“0.00”) |
