# api-client
Rest and websocket API client


## JSON Protocol

### Auth Request

```json
{
  "id": "<integer>",
  "method": "auth",
  "payload": {
    "token": "API token",
  }
}
```


### Subscribe Request

```json
{
  "id": "<integer>",
  "method": "subscribe",
  "payload": {
    "channel": "<string>",
  }
}
```
