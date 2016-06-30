# -*- coding: UTF-8 -*-
import datetime


##########################
# 根据Q获取所有月份
##########################
def check_Q_get_monthes(Q):
    qs = {'00': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
          'Q1': ['01', '02', '03'],
          'Q2': ['04', '05', '06'],
          'Q3': ['07', '08', '09'],
          'Q4': ['10', '11', '12'],
          }
    return qs[Q]


##########################
# 根据年、Q获取所有月份
##########################
def check_year_Q_get_monthes(year, Q):
    qs = {'00': [datetime.datetime.strptime(str(year) + k, '%Y%m') for k in
                 ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']],
          'Q1': [datetime.datetime.strptime(str(year) + k, '%Y%m') for k in ['01', '02', '03']],
          'Q2': [datetime.datetime.strptime(str(year) + k, '%Y%m') for k in ['04', '05', '06']],
          'Q3': [datetime.datetime.strptime(str(year) + k, '%Y%m') for k in ['07', '08', '09']],
          'Q4': [datetime.datetime.strptime(str(year) + k, '%Y%m') for k in ['10', '11', '12']],
          }
    return qs[Q]


##########################
# 根据月份获取当前Q
##########################
def check_month_get_Q(month):
    monthes = {'01': 'Q1',
               '02': 'Q1',
               '03': 'Q1',
               '04': 'Q2',
               '05': 'Q2',
               '06': 'Q2',
               '07': 'Q3',
               '08': 'Q3',
               '09': 'Q3',
               '10': 'Q4',
               '11': 'Q4',
               '12': 'Q4',
               }
    return monthes[month]


##########################
# 根据年和Q获取下个Q的数据
##########################
def get_after_year_month_by_Q(year, Q):
    year = int(year)
    if Q == 'Q4':
        year += 1
        Q = 'Q1'
    else:
        Q = 'Q' + str(int(Q[1]) + 1)
    # return [str(year)+'-'+k+'-01' for k in check_Q_get_monthes(Q)]
    return year, check_Q_get_monthes(Q)


##########################
# 根据年和Q获取上个Q的数据
##########################
def get_last_year_month_by_Q(year, Q):
    year = int(year)
    if Q == 'Q1':
        year -= 1
        Q = 'Q4'
    else:
        Q = 'Q' + str(int(Q[1]) - 1)
    # return [str(year)+'-'+k+'-01' for k in check_Q_get_monthes(Q)]
    return year, check_Q_get_monthes(Q)


############################################
# 根据开始时间、结束时间，返回相应的月份及天数
############################################
def get_monthes_pre_days(start, end):
    pre_month_days_list = []
    count = 0
    pre_month = start.replace(day=1)
    while True:
        targetmonth = count + pre_month.month
        try:
            if targetmonth == 12:
                p_month_date = pre_month.replace(
                    year=pre_month.year, month=targetmonth)
            else:
                p_month_date = pre_month.replace(
                    year=pre_month.year + int(targetmonth / 12), month=(targetmonth % 12))
        except Exception, e:
            p_month_date = pre_month.replace(year=pre_month.year + int((targetmonth + 1) / 12),
                                             month=((targetmonth + 1) % 12), day=1)
            p_month_date += datetime.timedelta(days=-1)
        if start.replace(day=1) <= p_month_date:
            month_last_day = get_month_last_date(p_month_date)
            if start.replace(day=1) == end.replace(day=1):
                days = (end - start).days + 1
            else:
                if start.replace(day=1) == p_month_date:
                    days = (month_last_day - start).days + 1
                elif end <= month_last_day:
                    days = end.day
                elif start.replace(day=1) < p_month_date:
                    days = month_last_day.day
            pre_month_days_list.append({'month': p_month_date, 'days': days})
        if end.strftime('%Y-%m') == p_month_date.strftime('%Y-%m'):
            break
        count += 1
    return pre_month_days_list


######################
# 获取本月的最后一天
######################
def get_month_last_date(date_time):
    y = date_time.year
    m = date_time.month
    if m == 12:
        month_end_dt = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
    return datetime.datetime.strptime(month_end_dt.isoformat(), '%Y-%m-%d')

# if __name__ == '__main__':
# print
# get_monthes_pre_days(datetime.datetime.strptime('2014-12-04','%Y-%m-%d'),datetime.datetime.strptime('2015-01-12','%Y-%m-%d'))
