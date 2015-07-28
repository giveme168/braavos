# -*- coding: utf-8 -*-
from models.client import Client, Group, Agent, AgentRebate


class searchAdClient(Client):
    __tablename__ = 'searchAd_client'


class searchAdGroup(Group):
    __tablename__ = 'searchAd_group'


class searchAdAgent(Agent):
    __tablename__ = 'searchAd_agent'


class searchAdAgentRebate(AgentRebate):
    __tablename__ = 'searchAd_agent_rebate'
