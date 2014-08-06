from models.client import Client, Agent


def _add_client(name):
    client = Client(name, 0)
    client.add()
    return client


def _add_agent(name):
    agent = Agent(name)
    agent.add()
    return agent


def test_client(session):
    client = _add_client('testclient')

    client2 = Client.get(client.id)
    assert client2.name == 'testclient'

    client.name = 'testclient2'
    client.save()
    client3 = Client.get(client.id)
    assert client3.name == 'testclient2'


def test_agent(session):
    agent = _add_agent('testagent')

    agent2 = Agent.get(agent.id)
    assert agent2.name == 'testagent'
