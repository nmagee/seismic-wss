# Seismic Portal to Kafka Stream Processor

This application connects to the European-Mediterranean Seismological Centre (EMSC) seismic portal websocket and streams real-time seismic events to Apache Kafka.

## Features

- **Real-time streaming**: Connects to the EMSC websocket for live seismic data
- **Kafka integration**: Streams JSON events to Apache Kafka topics
- **Configurable**: Environment variables for Kafka broker and topic configuration
- **Robust error handling**: Graceful handling of connection issues and malformed data
- **Comprehensive logging**: Detailed logging for monitoring and debugging

## Prerequisites

- Python 3.7+
- Apache Kafka cluster
- Network access to `wss://www.seismicportal.eu/standing_order/websocket`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 02-seismic-wss
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BROKER` | `localhost:9092` | Kafka broker address |
| `KAFKA_TOPIC` | `eu_seismic` | Kafka topic name |

Example:
```bash
export KAFKA_BROKER=my-kafka-cluster:9092
export KAFKA_TOPIC=seismic_events
```

## Usage

### Running the Application

```bash
python stream-kafka.py
```

The application will:
1. Connect to the EMSC websocket
2. Listen for seismic events
3. Parse and validate JSON messages
4. Send events to Kafka with appropriate keys
5. Log event details for monitoring

### Sample Output

```
2024-01-15 10:30:00,123 - INFO - Starting Seismic Kafka Producer
2024-01-15 10:30:00,124 - INFO - Kafka Broker: localhost:9092
2024-01-15 10:30:00,124 - INFO - Kafka Topic: eu_seismic
2024-01-15 10:30:00,124 - INFO - WebSocket URI: wss://www.seismicportal.eu/standing_order/websocket
2024-01-15 10:30:00,125 - INFO - Connecting to WebSocket: wss://www.seismicportal.eu/standing_order/websocket
2024-01-15 10:30:00,456 - INFO - WebSocket connection established
2024-01-15 10:30:00,457 - INFO - Listening for seismic events...
2024-01-15 10:30:15,789 - INFO - >>>> create  event from EMSC   , unid:20240115_0000001, T0:2024-01-15T10:30:15.000Z, Mag:4.2, Region: Mediterranean Sea
```

### Event Data Structure

The application processes seismic events with the following structure:

```json
{
  "action": "create",
  "data": {
    "properties": {
      "auth": "EMSC",
      "unid": "20240115_0000001",
      "time": "2024-01-15T10:30:15.000Z",
      "mag": 4.2,
      "flynn_region": "Mediterranean Sea"
    }
  },
  "id": "event_001"
}
```

## Testing

Run the test suite to verify the application:

```bash
python test_stream.py
```

The tests verify:
- Configuration loading
- WebSocket client functionality
- Kafka producer integration

## Architecture

The application consists of two main classes:

### `SeismicKafkaProducer`
- Manages Kafka producer lifecycle
- Handles message serialization and sending
- Provides context manager interface for resource cleanup

### `SeismicWebSocketClient`
- Manages WebSocket connection to EMSC
- Handles message reception and processing
- Integrates with Kafka producer for event streaming

## Error Handling

The application includes comprehensive error handling:

- **Connection failures**: Automatic reconnection attempts
- **Malformed JSON**: Graceful parsing with error logging
- **Kafka errors**: Producer error handling and recovery
- **WebSocket disconnections**: Clean shutdown and reconnection

## Monitoring

The application provides detailed logging for monitoring:

- Connection status and events
- Message processing statistics
- Error conditions and recovery
- Performance metrics

## Troubleshooting

### Common Issues

1. **Connection refused**: Check Kafka broker address and network connectivity
2. **WebSocket connection failed**: Verify network access to EMSC portal
3. **JSON parsing errors**: Check for malformed messages in logs
4. **Kafka producer errors**: Verify topic exists and permissions

### Debug Mode

Enable debug logging by modifying the logging level in the code:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

