# -*- coding: UTF-8 -*-
import datetime
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.client import Agent, AgentRebate
from models.user import User

if __name__ == '__main__':
    agent_rebates = AgentRebate.query.filter_by(
        year=datetime.datetime.strptime('2015', '%Y'))
    for k in agent_rebates:
        try:
            AgentRebate.add(agent=Agent.get(k.agent_id),
                            year=datetime.datetime.strptime('2016', '%Y'),
                            inad_rebate=k.inad_rebate,
                            douban_rebate=k.douban_rebate,
                            creator=User.get(95),
                            create_time=datetime.datetime.now())
        except Exception, e:
            print e
