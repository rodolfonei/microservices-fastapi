"""
Root conftest.py - shared fixtures for all tests
"""
import pytest
import fakeredis


@pytest.fixture(scope="session")
def redis_server():
    """
    Provides a fake Redis server for testing.
    Uses fakeredis for fast, isolated tests without external dependencies.
    """
    server = fakeredis.FakeRedis(decode_responses=True)
    yield server
    server.flushall()


@pytest.fixture
def clean_redis(redis_server):
    """
    Provides a clean Redis instance for each test.
    Clears all data before each test.
    """
    redis_server.flushall()
    yield redis_server
    redis_server.flushall()