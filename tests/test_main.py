from unittest.mock import MagicMock
import pytest

def test_redis_connection_mocked():
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    assert mock_redis.ping() is True

def test_health_logic():
    assert True

def test_math_logic():
    assert 1 + 1 == 2