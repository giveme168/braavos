# encoding: utf-8
import sys
sys.path.append('/Users/guoyu1/workspace/inad/braavos')
# sys.path.append('/home/inad/apps/braavos/releases/current')

from app import app

from models.user import Out, OutReport


if __name__ == '__main__':
    outs = Out.all()
    for k in outs:
        OutReport.add(start_time=k.start_time,
                      end_time=k.end_time,
                      address=k.address,
                      reason=k.reason,
                      meeting_s=k.meeting_s,
                      persions=k.persions,
                      m_persion=k.m_persion,
                      m_persion_type=k.m_persion_type,
                      creator_type=k.creator_type,
                      create_time=k.create_time,
                      status=k.status,
                      out=k,
                      creator=k.creator)
        for i in k.joiners:
            OutReport.add(start_time=k.start_time,
                          end_time=k.end_time,
                          address=k.address,
                          reason=k.reason,
                          meeting_s=k.meeting_s,
                          persions=k.persions,
                          m_persion=k.m_persion,
                          m_persion_type=k.m_persion_type,
                          creator_type=k.creator_type,
                          create_time=k.create_time,
                          status=k.status,
                          out=k,
                          creator=i)
