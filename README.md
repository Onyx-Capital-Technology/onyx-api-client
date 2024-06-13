# Onyx API Client

[![build](https://github.com/Onyx-Capital-Technology/onyx-api-client/actions/workflows/build.yml/badge.svg)](https://github.com/Onyx-Capital-Technology/onyx-api-client/actions/workflows/build.yml)

This repository contains a Python
Rest and websocket API client


## Installation & Testing

* Clone this repository
* Install the dependencies (it uses `poetry` so it needs toi be installed first)
  ```bash
  make install
  ```
* Add a `.env` file inside the repository directory with the following content
  ```
  ONYX_API_TOKEN=...
  ```
* Run the `test.py` script
  ```bash
  poetry run python test.py
  ```
  If succesful, it should print the server info and the tickers for the `dub` product.

## Websocket JSON Protocol

Onyx websocket API is located at `wss://ws.onyxhub.co/stream/v1`.

The websocket API uses a JSON protocol for all requests and responses.

A client request must be an object which includes

* an `id` string which can be used to correlate requests with responses
* a `method` string which indicates the type of request

All requests will receive a response back from the server, with the same `id` and `method` as the request, provided the `method` is valid. If the `method` is invalid, the server will terminate the connection without response.

A valid request, that is a request with a valid method, will receive a response with the following schema

```json
{
  "id": "<same as request>",
  "method": "<same as request>",
  "message": "<object | string>",
  "error": true | false
}
```

if the `error` flag is `true`, the `message` field will contain the error message, otherwise the request was successful.

### Auth Request

Once the websocket connection is established, the client must authenticate with the server by sending an `auth` request.
Failing to authenticate will result in the server terminating the connection after approximatetly 5 seconds.
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

#### Subscribe to server_info

Subscribe to `server_info` channel to receive server info updates
```json
{
  "id": "<string>",
  "method": "subscribe",
  "channel": "server_info",
}
```

#### Subscribe to tickers

Subscribe to `tickers` channel to receive tickers updates, this example subscribe to all tickers in the `ebob` product
```json
{
  "id": "<string>",
  "method": "subscribe",
  "channel": {
    "tickers": {
      "products": ["ebob"]
    }
  }
}
```

#### Subscribe to dashboards

Subscribe to `dashboards` channel to receive dashboards updates, the first update will be the full state of the dashboard, subsequent updates will be incremental updates.
```json
{
  "id": "<string>",
  "method": "subscribe",
  "channel":"dashboards"
}
```

#### Subscribe to RFQ

**CURRENTLY THIS IS AVAILABLE FOR INTERNAL USERS ONLY**.

Subscribe to an `rfq` (request for quote) stream, only if the user has the required trading permissions.

* `RFQ` for an outright
  ```json
  {
    "id": "<string>",
    "method": "subscribe",
    "channel": {
      "rfq": {
        "symbol": "brtu24",
        "exchange": "ice",
        "size": 10,
      }
    }
  }
  ```
* `RFQ` for a spread
  ```json
  {
    "id": "<string>",
    "method": "subscribe",
    "channel": {
      "rfq": {
        "symbol": {
          "front": "brtu24",
          "back": "brtz24",
        },
        "exchange": "ice",
        "size": 10,
      }
    }
  }
  ```

#### Subscribe to Product Risk

**CURRENTLY THIS IS AVAILABLE FOR INTERNAL USERS ONLY**.

Subscribe to `product_risk` stream, only if the user has the required trading permissions.
```json
{
  "id": "<string>",
  "method": "subscribe",
  "channel": {
    "product_risk": {
      "product_symbol": "ebob",
      "account_id": "account_id"
    }
  }
}
```

### Unsubscribe Request

To unsubscribe from  `dashboards` and `server_info` channels, send the following request

```json
{
  "id": "<string>",
  "method": "unsubscribe",
  "channel": "<string>",
}
```

To unsubscribe from  `tickers` channels, send the following request

```json
{
  "id": "<string>",
  "method": "unsubscribe",
  "channel": "tickers": {
    "products": ["ebob"]
  }
}
```

To unsubscribe from  `rfq` channels, send the following request

```json
{
  "id": "<string>",
  "method": "unsubscribe",
  "channel": "rfq": {
    "symbol": {
      "front": "brtu24",
      "back": "brtz24",
    },
    "exchange": "ice",
  }
}
```

### Streaming Events

The server will send events to the client as thay occur if the client is subscribed to the corresponding channel.

An event payload is a JSON object with the following schema

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
      "product_symbol": "<string>",
      "timestamp_millis": "<integer>",
      "mid": "<string>",
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

#### RFQ Event

```json
{
  "channel": "tickers",
  "message": [
    {
      "symbol": "<string/Spread/Butterfly>",
      "exchange": "ice",
      "product_symbol": "<string>",
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

* a Spread takes the following form
```json
{
  "front": "<string>",
  "back": "<string>",
}
```
* a Butterfly takes the following form
```json
{
  "front": "<string>",
  "middle": "<string>",
  "back": "<string>",
}
```

### Place Order Request

To place an order for a given rfq stream, send the following request

```json
{
  "id": "<string>",
  "method": "order",
  "symbol": "<string/Spread/Butterfly>",
  "exchange": "ice" | "cme",
  "side": "buy" | "sell",
  "amount": "<string>",
  "price": "<string>",
  "timestamp_millis": "<unsigned integer>",
  "client_order_id": "<optional string>",
  "account_id": "<optional string>",
}
```

* The `symbol` is the symbol of the rfq stream
* The `client_order_id` is optional, if provided it must be unique
* The `timestamp_millis` is the UTC time when the order was placed by the client, used for rejecting orders that are too old due to network latency.
* The `account_id` is optional, if provided the order will be placed on the specified account, otherwise the order will be placed on the default account.
