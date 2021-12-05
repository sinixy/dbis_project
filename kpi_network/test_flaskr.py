import os
import tempfile
import json

import pytest

from kpi_network import app


app.config['TESTING'] = True

@pytest.fixture
def client():
    client = app.test_client()
    return client


def test_get_user(client):
    # перевірка чи повертає сервер дані про користувача
    data = json.loads(client.get('/user/1').data)
    # перевірка чи повертає сервер id користувача і чи відсутні помилки
    assert 'id' in data['data'].keys()
    assert data['data']['id'] == 1
    assert not data['errors']

def test_create_user(client):
    # перевірка чи коректно сервер створює користувача
    data = json.loads(client.post('/user', json ={'login': 'logex', 'password': 'passex', 'name': "nameex", 'status': 'student'}).data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка чи не буде сервер створювати користувача з некоректними даними
    data = json.loads(client.post('/user', json={'login': 'logex', 'password': 'passex', 'name': "nameex", 'status': 'notstudent'}).data)
    assert not data['data']
    assert data['errors'][0] == 'Unknown user type'
    data = json.loads(client.post('/user', json={'login': 'logex', 'password': 'passex', 'name': "nameex"}).data)
    assert not data['data']
    assert data['errors'][0] == 'Bad request.'

# def test_delete_user(client):

def test_get_channel(client):
    # перевірка чи повертає сервер коретну інформацію про канал
    data = json.loads(client.get('/channel/1').data)
    assert 'id' in data['data'].keys()
    assert data['data']['id'] == 1
    assert not data['errors']
    # перевірка коректності поведінки серверу при запиті неіснуючого каналу
    data = json.loads(client.get('/channel/10').data)
    assert not data['data']
    assert data['errors'][0] == 'Channel not found'

# def test_create_channel(client):
#     # перевірка чи коректно сервер створює канал
#     data = json.loads(client.post('/channel', json={'name': 'nameex', 'description': 'descex', 'photo': ''}).data)
#     assert 'id' in data['data'].keys()
#     assert not data['errors']

def test_edit_channel(client):
    # первірка коректності поведінки серверу на запит про зміну каналу
    data = json.loads(client.put('/channel/1', json={'name': 'nameex'}).data)
    assert not data['data']
    data = json.loads(client.put('/channel/10', json={'name': 'nameex'}).data)
    assert not data['data']
    assert data['errors'][0] == 'Channel not found'

# def test_channel_members

def test_get_post(client):
    # перевірка чи повертає сервер коретну інформацію про пост
    data = json.loads(client.get('/posts/1').data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка коректності поведінки серверу при запиті неіснуючого посту
    data = json.loads(client.get('/posts/10').data)
    assert not data['data']
    assert data['errors'][0] == 'Post not found'

# def test_create_post(client):
#     # перевірка чи коректно сервер створює пост
#     data = json.loads(client.post('/posts', json={'text': 'textex', 'channel': '10'}).data)
#     assert 'id' in data['data'].keys()
#     assert not data['errors']
#     # перевірка чи не створює сервер пост з неіснуючим каналом
#     data = json.loads(client.post('/posts', json={'text': 'textex', 'channel': '10'}).data)
#     assert not data['data']
#     assert data['errors'][0] == 'Specified channel does not exist'











