from models.client import Client, Agent
from helper import add_client, add_agent


def test_client(session):
    client = add_client('testclient')

    client2 = Client.get(client.id)
    assert client2.name == 'testclient'

    client.name = 'testclient2'
    client.save()
    client3 = Client.get(client.id)
    assert client3.name == 'testclient2'


def test_agent(session):
    agent = add_agent('testagent')

    agent2 = Agent.get(agent.id)
    assert agent2.name == 'testagent'
