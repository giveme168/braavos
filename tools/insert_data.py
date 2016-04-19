# -*- coding: UTF-8 -*-
import datetime
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.client import AgentRebate
from models.user import User

if __name__ == '__main__':
    year_2015 = datetime.datetime.strptime('2015', '%Y').date()
    year_2016 = datetime.datetime.strptime('2016', '%Y').date()
    agent_rebates = AgentRebate.query.filter_by(year=year_2015)
    for k in agent_rebates:
        if not AgentRebate.query.filter_by(agent=k.agent, year=year_2016).first():
            AgentRebate.add(agent=k.agent,
                            year=year_2016,
                            inad_rebate=k.inad_rebate,
                            douban_rebate=k.douban_rebate,
                            creator=User.get(95),
                            create_time=datetime.datetime.now())
