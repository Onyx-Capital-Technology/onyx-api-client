# Onyx API Client
Rest and websocket API client


## Websocket JSON Protocol

The websocket API uses JSON for all requests and responses. All requests must
include

* an `id` string which can be used to correlate requests with responses
* a `method` string which indicates the type of request

All requests will receive a response back from the server, with the same `id` and `method` as the request, provided the `method` is valid. If the `method` is invalid, the server will terminate the connection without response.

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

### Streaming Events

The server will send events to the client as thay occur if the client is subscribed to the corresponding channel.

An avent payload is a JSON object with the following schema

```json
{
  "channel": "<string>",
  "message": "<object>",
  "message_type": "<int>"
}
```

where `channel` is the channel that produced the message, `message_type` is an integer that indicates the type of message, and `message` is the message payload.
The type of message can be
* 0 - not specified
* 1 - update
* 2 - create
* 3 - delete

#### Server Info Event

```json
{
  "channel": "server_info",
  "message": {
    "uid": "<string>",
    "timestamp": "<date iso-format string>",
    "age_millis": "<number>",
  },
  "message_type": 0
}
```

The `uid` is the unique identifier for the websocket connection. The `timestamp` is the UTC time when the server sent the event. The `age_millis` is the number of milliseconds since the websocket connection was established.


#### Dashboards Event


```json
{
  "channel": "dashboards",
  "message": "<dashboard object or list of dashboard objects>",
  "message_type": "<int>"
}
```

The first event after subscribing to the `dashboards` channel will be the full state of the user dashboards.

```json
{
  "channel": "dashboards",
  "message": ["<dashboard object>"],
  "message_type": 0
}
```

Subsequent events will be incremental updates to the user dashboards.

```json
{
  "channel": "dashboards",
  "message": "<dashboard object>",
  "message_type": 1 | 2 | 3
}
```

#### Tickers Event

```json
{
  "channel": "tickers",
  "message": [
    {
      "symbol": "<string>",
      "timestamp_millis": "<integer>",
      "bid": {
        "price": "<string>",
        "amount": "<string>",
      },
      "ask": {
        "price": "<string>",
        "amount": "<string>",
      },
    },
  ],
  "message_type": 1
}
```
