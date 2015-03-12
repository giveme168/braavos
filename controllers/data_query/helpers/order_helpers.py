# -*- coding: UTF-8 -*-
import datetime
import xlwt


#根据开始时间、结束时间，返回相应的月份及天数
def get_monthes_pre_days(pre_month,start,end):
    pre_month_days_list=[]  
    count = 0
    while True :
        targetmonth=count+pre_month.month
        try:
            p_month_date=pre_month.replace(year=pre_month.year+int(targetmonth/12),month=(targetmonth%12))
        except:
            p_month_date=pre_month.replace(year=pre_month.year+int((targetmonth+1)/12),month=((targetmonth+1)%12),day=1)
            p_month_date+=datetime.timedelta(days=-1)
        
        if start.replace(day=1) <= p_month_date:
            month_last_day = get_month_last_date(p_month_date)
            if start.replace(day=1) == end.replace(day=1):
                days = (end-start).days+1
            else:
                if start.replace(day=1) == p_month_date:
                    days = (month_last_day-start).days+1
                elif end <= month_last_day:
                    days = end.day
                elif start.replace(day=1) < p_month_date:
                    days = month_last_day.day

            pre_month_days_list.append({'month':p_month_date,'days':days})
        if end.strftime('%Y-%m') == p_month_date.strftime('%Y-%m'):
            break
        count += 1
    return pre_month_days_list


#获取本月的最后一天
def get_month_last_date(date_time):
    y=date_time.year
    m = date_time.month
    month_start_dt = datetime.date(y,m,1)

    if m == 12:
        month_end_dt = datetime.date(y+1,1,1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.date(y,m+1,1) - datetime.timedelta(days=1)
    return datetime.datetime.strptime(month_end_dt.isoformat(),'%Y-%m-%d')


def write_excel(orders,type,th_obj):
    xls = xlwt.Workbook(encoding='utf-8')
    sheet = xls.add_sheet("Sheet")
    if type == 1:
        keys = [u'代理/直客',u'客户','Campaign',u'总金额',u'开始',u'结束']
    else:
        keys = [u'客户','Campaign',u'总金额',u'开始',u'结束']
    keys += [ k['month'] for k in th_obj]
    for k in range(len(keys)):
        sheet.write(0,k,keys[k])
    for k in range(len(orders)):
        order_pre_money = orders[k]['order_pre_money']
        if type == 1:
            sheet.write(k+1,0,orders[k]['agent_name'])
            sheet.write(k+1,1,orders[k]['client_name'])
            sheet.write(k+1,2,orders[k]['campaign'])
            sheet.write(k+1,3,orders[k]['money'])
            sheet.write(k+1,4,str(orders[k]['start']))
            sheet.write(k+1,5,str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k+1,5+m+1,order_pre_money[m]['money'])
        else:
            sheet.write(k+1,0,orders[k]['medium_name'])
            sheet.write(k+1,1,orders[k]['campaign'])
            sheet.write(k+1,2,orders[k]['money'])
            sheet.write(k+1,3,str(orders[k]['start']))
            sheet.write(k+1,4,str(orders[k]['end']))
            for m in range(len(order_pre_money)):
                sheet.write(k+1,4+m+1,order_pre_money[m]['money'])
    return xls
