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


def test_login(client):
    # перевірка коректності авторизації користувача
    data = json.loads(client.post('/api/session', json = {'login': 'NancyDye8533', 'password': 'NancyDye8533'}).data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка чи не буде сервер авторизовувати користувача з некоректними даними
    data = json.loads(client.post('/api/session', json={'login': 'invalid login', 'password': 'NancyDye8533'}).data)
    assert not data['data']
    assert data['errors'][0] == 'Invalid login or password'


def test_get_session(client):
    client.post('/api/session',  json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    # перевірка чи коректно записується користувачу coockie
    data = json.loads(client.get('/api/session').data)
    assert 'id' in data['data'].keys()
    assert not data['errors']


def test_logout(client):
    client.post('/api/session',  json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    # перевірка коректності виходу з аккаунту користувача
    data = json.loads(client.delete('/api/session').data)
    data1 = json.loads(client.get('/api/session').data)
    assert not data1['data']
    assert data1['errors'][0] == 'No cookies'


def test_get_user(client):
    # перевірка чи повертає сервер дані про користувача
    data = json.loads(client.get('/api/user/1').data)
    # перевірка чи повертає сервер id користувача і чи відсутні помилки
    assert 'id' in data['data'].keys()
    assert data['data']['id'] == 1
    assert not data['errors']


def test_create_user(client):
    # перевірка чи коректно сервер створює користувача
    data = json.loads(client.post('/api/user', json ={'login': 'logex', 'password': 'passex', 'name': "nameex", 'status': 'student', 'group': 'kl-1', 'department': 'fict'}).data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка чи не буде сервер створювати користувача з некоректними даними
    data = json.loads(client.post('/api/user', json={'login': 'logex', 'password': 'passex', 'name': "nameex", 'status': 'notstudent'}).data)
    assert not data['data']
    assert data['errors'][0] == 'Unknown user type'
    data = json.loads(client.post('/api/user', json={'login': 'logex', 'password': 'passex', 'name': "nameex"}).data)
    assert not data['data']
    assert data['errors'][0] == 'Bad request.'


def test_edit_user(client):
    # первірка коректності поведінки серверу на запит про редагування юзера
    client.post('/api/session',  json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.put('/api/user', json={'name': "nameex", 'department': "departmentex", 'group': "groupex"}).data)
    assert not data['data']
    assert not data['errors']
    data1 = json.loads(client.get('/api/user/1').data)
    assert data1['data']['name'] == "nameex"
    assert not data1['errors']


def test_get_user_channels(client):
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.get('/api/user/channels').data)
    assert data['data']['items']
    assert not data['errors']


def test_get_channel(client):
    # перевірка чи повертає сервер коретну інформацію про канал
    data = json.loads(client.get('/api/channel/1').data)
    assert 'id' in data['data'].keys()
    assert data['data']['id'] == 1
    assert not data['errors']
    # перевірка коректності поведінки серверу при запиті неіснуючого каналу
    data = json.loads(client.get('/api/channel/999999').data)
    assert not data['data']
    assert data['errors'][0] == 'Channel not found'


def test_create_channel(client):
    # перевірка чи коректно сервер створює канал
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.post('/api/channel', json={'name': 'nameex', 'description': 'descex', 'members': [2, 3]}).data)
    assert 'id' in data['data'].keys()
    assert not data['errors']


def test_edit_channel(client):
    # первірка коректності поведінки серверу на запит про зміну каналу
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.put('/api/channel/9', json={'name': 'nameex'}).data)
    assert not data['data']
    data = json.loads(client.put('/api/channel/999999', json={'name': 'nameex'}).data)
    assert not data['data']
    assert data['errors'][0] == 'Channel not found'


def test_get_channel_posts(client):
    data = json.loads(client.get('/api/channel/1/posts').data)
    assert data['data']['items']
    assert not data['errors']


def test_get_post(client):
    # перевірка чи повертає сервер коретну інформацію про пост
    data = json.loads(client.get('/api/posts/1').data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка коректності поведінки серверу при запиті неіснуючого посту
    data = json.loads(client.get('/api/posts/999999').data)
    assert not data['data']
    assert data['errors'][0] == 'Post not found'


def test_create_post(client):
    # перевірка чи коректно сервер створює пост
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.post('/api/posts', json={'text': 'textex', 'channelId': 1}).data)
    print(data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
    # перевірка чи не створює сервер пост з неіснуючим каналом
    data = json.loads(client.post('/api/posts', json={'text': 'textex', 'channelId': 999999}).data)
    assert not data['data']
    assert data['errors'][0] == 'Specified channel does not exist'


def test_get_search(client):
    # перевіряє чи коректно сервер виконує пошук по користувачам
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.get('/api/search?query=Esther').data)
    assert data['data']['items']
    assert not data['errors']


def test_get_user_contacts(client):
    # перевіряє чи коректно сервер отримує контакти користувача
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.get('/api/user/contacts').data)
    assert data['data']['items']
    assert not data['errors']


def test_add_contact(client):
    # перевіряє чи коректно сервер додає контакт до поточного користувача
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.post('/api/contact/2').data)
    assert not data['data']
    assert not data['errors']


def test_get_direct_massages(client):
    # перевіряє чи коректно сервер отримує дані переписки (повідомлення) між поточним користувачем та partner'ом
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.get('/api/direct/36').data)
    assert data['data']['items']
    assert not data['errors']


def test_create_massage(client):
    # перевіряє чи коректно надсилає повідомлення
    client.post('/api/session', json={'login': 'NancyDye8533', 'password': 'NancyDye8533'})
    data = json.loads(client.post('/api/message', json={'receiverId': 2, 'text': 'halo'}).data)
    assert 'id' in data['data'].keys()
    assert not data['errors']
























