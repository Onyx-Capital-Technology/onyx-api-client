# api-client
Rest and websocket API client


## JSON Protocol

### Auth Request

```json
{
  "id": "<integer>",
  "method": "auth",
  "token": "API token",
}
```


### Subscribe Request

```json
{
  "id": "<integer>",
  "method": "subscribe",
  "channel": "<string>",
}
```

* Subscribe to `server_info` channel to receive server info updates
  ```json
  {
    "id": "<integer>",
    "method": "subscribe",
    "channel": "server_info",
  }
  ```
