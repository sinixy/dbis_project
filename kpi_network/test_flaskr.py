import os
import tempfile

import pytest

from kpi_network import app


app.config['TESTING'] = True

@pytest.fixture
def client():
    client = app.test_client()
    return client

def test_login(client):
    data = client.get('/user/1').data
    print(data)
    assert 'id' in data.keys()