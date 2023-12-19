# api-client
Rest and websocket API client


## JSON Protocol

The websocket API uses JSON for all requests and responses. All requests must
include

* an `id` string which can be used to correlate requests with responses
* a `method` string which indicates the type of request

All requests will receive a response back from the server, with the same `id` and `method` as the request, provided the `method` is valid. If the `method` is invalid, the server will respond with an error.

A valid request, that is a request with a valid method, will receive a response with the following schema

```json
{
  "id": "<same as request>",
  "method": "<same as request>",
  "message": "<string>",
  "error": true | false
}
```

if the `error` flag is `true`, the `message` field will contain the error message, otherwise the request was successful.

### Auth Request

```json
{
  "id": "<string>",
  "method": "auth",
  "token": "API token",
}
```

### Subscribe Request

```json
{
  "id": "<string>",
  "method": "subscribe",
  "channel": "<string>",
}
```

* Subscribe to `server_info` channel to receive server info updates
  ```json
  {
    "id": "<string>",
    "method": "subscribe",
    "channel": "server_info",
  }
  ```

* Subscribe to `tickers` channel to receive tickers updates, this example subscribe to all tickers in the `crude` product group
  ```json
  {
    "id": "<string>",
    "method": "subscribe",
    "channel": {
      "tickers": {
        "product_groups": ["crude"]
      }
    }
  }
  ```

* Subscribe to `dashboards` channel to receive dashboards updates, the first update will be the full state of the dashboard, subsequent updates will be incremental updates.
  ```json
  {
    "id": "<string>",
    "method": "subscribe",
    "channel":"dashboards"
  }
  ```
