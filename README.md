# European Earthquake Websocket Stream

This Python script makes a websocket connection to the [EPOS Seismic data stream](https://www.seismicportal.eu/realtime.html). Using long polling the connection refreshes
every 15 seconds and returns events in near real-time.


## Requirements

Install the `tornado` package:

```
pip install tornado
```

## Data Output

The JSON for an example event:

```
{'action': 'update', 'data': {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [24.15, 40.26, -8.0]}, 'id': '20250607_0000162', 'properties': {'source_id': '1817989', 'source_catalog': 'EMSC-RTS', 'lastupdate': '2025-06-07T14:51:14.430215Z', 'time': '2025-06-07T12:55:46.7Z', 'flynn_region': 'AEGEAN SEA', 'lat': 40.26, 'lon': 24.15, 'depth': 8.0, 'evtype': 'ke', 'auth': 'THE', 'mag': 2.5, 'magtype': 'ml', 'unid': '20250607_0000162'}}}
```

which is rendered into a logging output:

```
INFO:root:>>>> update  event from AFAD   , unid:20250608_0000132, T0:2025-06-08T11:27:46.0Z, Mag:1.4, Region: EASTERN TURKEY
```

The script could easily be modified to transform data elements, or pass the stream into a logging aggregator such as Kafka.

