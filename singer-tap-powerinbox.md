# Tap Powerinbox

## Connecting Tap Powerinbox

### Requirements

To set up Tap Powerinbox in Stitch, you need the following from your Powerinbox account:
1. GUID
2. Company ID

### Setup

1. Retrieve your GUID from Powerinbox.
2. Retrieve your Company ID from Powerinbox.

Create a `config.json` file in the following format, where `guid` and `company_id` are the credentials you just retrieved.

```json
{
  "guid": "add-powerinbox-guid",
  "company_id": "add-powerinbox-company-id"
}
```

---

## Tap Powerinbox Replication

- Calls to the Tap Powerinbox API is limited to 100 every 30 seconds, with 5 max tries if a request isn't completed successfully. The tap should remain well below this max during normal use.

---

## Tap Powerinbox Table Schemas

Each header denotes the table name.

### powerinbox_response
- Description: values returned from the GET request

| NAME          | TYPE   | DESCRIPTION  |
| ------------- |:------:| ------------------------------------------------------------------:|
| date          | string | The date in YYYY-MM-DD format (UTC)                                |
| stripe        | number | The stripe Id                                                      |
| sub_id        | string | The subId passed in the stripe url query parameter                 |
| unique_opens  | number | The unique number of stripe opens per user                         |
| total_clicks  | number | The total number of clicks                                         |
| net_revenue   | string | The net revenue in US dollars with two significant digits (“0.00”) |
