import pytest
from unittest.mock import patch, MagicMock
import json
from tornado import gen

# Import functions from the stream module
from stream import myprocessing, listen, launch_client, echo_uri, PING_INTERVAL

import logging # Added import

# Mock for the websocket connection
@pytest.fixture
def mock_ws_connection():
    mock_ws = MagicMock()
    mock_ws.read_message = MagicMock()
    return mock_ws

@pytest.fixture
def mock_websocket_connect(mock_ws_connection):
    with patch('stream.websocket_connect', return_value=gen.maybe_future(mock_ws_connection)) as mock_connect:
        yield mock_connect

@pytest.fixture(autouse=True)
def setup_logging(): # Removed caplog from here as it's injected per test
    # Ensure logging is configured for tests that check caplog
    # stream.py configures logging in its __main__ block, which isn't run during pytest import.
    # The root logger is configured here. Tests using caplog will automatically use this.
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s', force=True)


# Tests for myprocessing function
def test_myprocessing_valid_json(caplog):
    caplog.set_level(logging.INFO)
    valid_message = '{"action": "update", "data": {"type": "Feature", "properties": {"auth": "TEST", "unid": "123", "time": "NOW", "mag": "5.0", "flynn_region": "Test Region"}}}'
    myprocessing(valid_message)
    # Check for the core message content, tolerate formatting variations from caplog
    assert ">>>> update  event from TEST   , unid:123, T0:NOW, Mag:5.0, Region: Test Region" in caplog.text
    assert any(record.levelno == logging.INFO for record in caplog.records)

def test_myprocessing_invalid_json(caplog):
    caplog.set_level(logging.ERROR) # This logs an exception, so check ERROR level
    invalid_message = 'this is not json'
    myprocessing(invalid_message)
    assert "Unable to parse json message" in caplog.text
    assert any(record.levelno == logging.ERROR for record in caplog.records)

def test_myprocessing_missing_keys(caplog):
    caplog.set_level(logging.ERROR) # This also logs an exception due to KeyError
    message_missing_keys = '{"action": "update", "data": {"type": "Feature", "properties": {"auth": "TEST"}}}' # Missing unid, time, etc.
    myprocessing(message_missing_keys)
    assert "Unable to parse json message" in caplog.text # The specific log message from the except block
    assert any(record.levelno == logging.ERROR for record in caplog.records)
    assert "KeyError: 'unid'" in caplog.text # Check that the KeyError is mentioned in the full log

# Tests for listen function
@pytest.mark.asyncio
async def test_listen_receives_message(mock_ws_connection):
    test_message = '{"data": "test"}'
    # Configure read_message to return a message then None to stop the loop
    mock_ws_connection.read_message.side_effect = [gen.maybe_future(test_message), gen.maybe_future(None)]

    with patch('stream.myprocessing') as mock_myprocessing:
        await listen(mock_ws_connection)
        mock_myprocessing.assert_called_once_with(test_message)
        # Also assert that read_message was called twice (once for message, once for None)
        assert mock_ws_connection.read_message.call_count == 2

@pytest.mark.asyncio
async def test_listen_handles_none_message(mock_ws_connection, caplog):
    caplog.set_level(logging.INFO)
    mock_ws_connection.read_message.return_value = gen.maybe_future(None) # Simulate connection close
    await listen(mock_ws_connection)
    assert "close" in caplog.text
    assert any(record.levelno == logging.INFO for record in caplog.records)
    mock_ws_connection.read_message.assert_called_once()

# Tests for launch_client function
@pytest.mark.asyncio
async def test_launch_client_success(mock_websocket_connect, mock_ws_connection, caplog):
    caplog.set_level(logging.INFO)
    with patch('stream.listen') as mock_listen:
        await launch_client()
        mock_websocket_connect.assert_called_once_with(echo_uri, ping_interval=PING_INTERVAL)
        mock_listen.assert_called_once_with(mock_ws_connection)
        assert f"Open WebSocket connection to {echo_uri}" in caplog.text
        assert "Waiting for messages..." in caplog.text
        assert all(record.levelno == logging.INFO for record in caplog.records if record.name == "root")


@pytest.mark.asyncio
async def test_launch_client_connection_error(mock_websocket_connect, caplog):
    caplog.set_level(logging.ERROR) # This logs an exception
    mock_websocket_connect.side_effect = Exception("Connection failed")
    with patch('stream.listen') as mock_listen: # listen should not be called
        await launch_client()
        mock_websocket_connect.assert_called_once_with(echo_uri, ping_interval=PING_INTERVAL)
        mock_listen.assert_not_called()
        assert "connection error" in caplog.text
        assert "Connection failed" in caplog.text # Check for the specific exception message
        # Ensure the "connection error" is logged as ERROR, "Connection failed" is also part of the error log.
        # The initial "Open WebSocket" might be INFO, so we filter for ERROR records.
        assert any(record.levelno == logging.ERROR and "connection error" in record.message for record in caplog.records)
        # "Connection failed" is part of the exception's string representation, which gets included in caplog.text
        # The above line already confirms the primary "connection error" log message at ERROR level.
        # The assert "Connection failed" in caplog.text (done a few lines above) confirms the exception message is in the output.
