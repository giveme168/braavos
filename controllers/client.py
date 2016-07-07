# -*- coding: UTF-8 -*-
import datetime
import operator

from flask import Blueprint, request, redirect, abort, url_for, g, jsonify
from flask import render_template as tpl, flash

from models.client import Client, Group, Agent, AgentRebate, AgentMediumRebate
from models.medium import Medium, MediumRebate
from models.attachment import Attachment
from forms.client import NewClientForm, NewGroupForm, NewAgentForm
from forms.medium import NewMediumForm
from models.user import Team
from controllers.helpers.client_helpers import write_client_excel, write_medium_excel

client_bp = Blueprint('client', __name__,
                      template_folder='../templates/client')


@client_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('client.clients'))


@client_bp.route('/new_client', methods=['GET', 'POST'])
def new_client():
    form = NewClientForm(request.form)
    if request.method == 'POST' and form.validate():
        db_client_name = Client.name_exist(form.name.data)
        if not db_client_name:
            client = Client.add(form.name.data, form.industry.data)
            flash(u'新建客户(%s)成功!' % client.name, 'success')
        else:
            flash(u'客户%s已存在，不用添加!' % form.name.data, 'danger')
            return tpl('client.html', form=form, title=u"新建客户")
        return redirect(url_for("client.clients"))
    return tpl('client.html', form=form, title=u"新建客户")


@client_bp.route('/new_group', methods=['GET', 'POST'])
def new_group():
    if not (g.user.is_contract() or g.user.is_super_leader()):
        abort(403)
    form = NewGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        db_group_name = Group.name_exist(form.name.data)
        if not db_group_name:
            group = Group.add(form.name.data)
            flash(u'新建代理集团(%s)成功!' % group.name, 'success')
        else:
            flash(u'新建代理集团(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('group.html', form=form, group=None, title=u"新建代理集团")
        return redirect(url_for("client.groups"))
    return tpl('group.html',
               form=form,
               group=None,
               title=u"新建代理集团")


@client_bp.route('/new_agent', methods=['GET', 'POST'])
def new_agent():
    if not (g.user.is_contract() or g.user.is_super_leader()):
        abort(403)
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        db_agent_name = Agent.name_exist(form.name.data)
        if not db_agent_name:
            agent = Agent.add(form.name.data, Group.get(form.group.data),
                              form.tax_num.data, form.address.data, form.phone_num.data,
                              form.bank.data, form.bank_num.data)
            flash(u'新建代理/直客(%s)成功!' % agent.name, 'success')
        else:
            flash(u'新建代理/直客(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('/client/agent/info.html', form=form, title=u"新建代理公司", status='news')
        return redirect(url_for("client.agents"))
    return tpl('/client/agent/info.html',
               form=form,
               status='news',
               title=u"新建代理/直客")


@client_bp.route('/new_medium', methods=['GET', 'POST'])
def new_medium():
    if not (g.user.is_media_leader() or g.user.is_super_leader()):
        abort(403)
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        db_medium_name = Medium.name_exist(form.name.data)
        if not db_medium_name:
            medium = Medium.add(
                name=form.name.data,
                owner=Team.get(form.owner.data),
                abbreviation=form.abbreviation.data,
                tax_num=form.tax_num.data,
                address=form.address.data,
                phone_num=form.phone_num.data,
                bank=form.bank.data,
                bank_num=form.bank_num.data)
            medium.save()
            flash(u'新建媒体(%s)成功!' % medium.name, 'success')
        else:
            flash(u'新建媒体(%s)失败, 名称已经被占用!' % form.name.data, 'danger')
            return tpl('/client/medium/info.html', form=form, title=u"新建媒体")
        return redirect(url_for("client.medium_detail", medium_id=medium.id))
    return tpl('/client/medium/info.html', form=form, title=u"新建媒体")


@client_bp.route('/client/<client_id>', methods=['GET', 'POST'])
def client_detail(client_id):
    client = Client.get(client_id)
    if not client:
        abort(404)
    form = NewClientForm(request.form)
    if request.method == 'POST' and form.validate():
        client.name = form.name.data
        client.industry = form.industry.data
        client.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = client.name
        form.industry.data = client.industry
    return tpl('client.html', form=form, title=u"客户-" + client.name)


@client_bp.route('/agent/<agent_id>/delete', methods=['GET', 'POST'])
def agent_delete(agent_id):
    Agent.get(agent_id).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('client.agents'))


@client_bp.route('/agent/<agent_id>', methods=['GET', 'POST'])
def agent_detail(agent_id):
    if not (g.user.is_contract() or g.user.is_super_leader() or g.user.is_finance()):
        abort(403)
    agent = Agent.get(agent_id)
    if not agent:
        abort(404)
    form = NewAgentForm(request.form)
    if request.method == 'POST' and form.validate():
        agent.name = form.name.data
        agent.group = Group.get(form.group.data)
        agent.tax_num = form.tax_num.data
        agent.address = form.address.data
        agent.phone_num = form.phone_num.data
        agent.bank = form.bank.data
        agent.bank_num = form.bank_num.data
        agent.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = agent.name
        form.group.data = agent.group.id if agent.group else None
        form.tax_num.data = agent.tax_num
        form.address.data = agent.address
        form.phone_num.data = agent.phone_num
        form.bank.data = agent.bank
        form.bank_num.data = agent.bank_num
    return tpl('/client/agent/info.html',
               form=form,
               agent=agent,
               status='update',
               title=u"代理/直客-" + agent.name)


@client_bp.route('/group/<group_id>/delete', methods=['GET', 'POST'])
def group_delete(group_id):
    Group.get(group_id).delete()
    flash(u'删除成功', 'success')
    return redirect(url_for('client.groups'))


@client_bp.route('/group/<group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    if not (g.user.is_contract() or g.user.is_super_leader() or g.user.is_finance()):
        abort(403)
    group = Group.get(group_id)
    if not group:
        abort(404)
    form = NewGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        group.name = form.name.data
        group.save()
        flash(u'保存成功', 'success')
    else:
        form.name.data = group.name
    return tpl('group.html',
               form=form,
               group=group,
               title=u"代理集团-" + group.name)


@client_bp.route('/medium/<medium_id>', methods=['GET', 'POST'])
def medium_detail(medium_id):
    if not (g.user.is_media_leader() or g.user.is_super_leader() or g.user.is_media() or g.user.is_finance()):
        abort(403)
    medium = Medium.get(medium_id)
    if not medium:
        abort(404)
    form = NewMediumForm(request.form)
    if request.method == 'POST' and form.validate():
        medium.name = form.name.data
        medium.owner = Team.get(form.owner.data)
        medium.level = form.level.data
        medium.abbreviation = form.abbreviation.data
        medium.tax_num = form.tax_num.data
        medium.address = form.address.data
        medium.phone_num = form.phone_num.data
        medium.bank = form.bank.data
        medium.bank_num = form.bank_num.data
        medium.save()
        flash(u'保存成功!', 'success')
    else:
        form.name.data = medium.name
        form.owner.data = medium.owner_id
        form.level.data = medium.level or 100
        form.abbreviation.data = medium.abbreviation
        form.tax_num.data = medium.tax_num
        form.address.data = medium.address
        form.phone_num.data = medium.phone_num
        form.bank.data = medium.bank
        form.bank_num.data = medium.bank_num
    return tpl('/client/medium/info.html', form=form,
               title=u"媒体-" + medium.name, status='update',
               medium=medium)


@client_bp.route('/mediums', methods=['GET'])
def mediums():
    medium_rebate = MediumRebate.all()
    medium_rebate_data = {}
    for k in medium_rebate:
        if str(k.medium.id) + '_' + str(k.year.year) not in medium_rebate_data:
            medium_rebate_data[str(k.medium.id) + '_' + str(k.year.year)] = str(k.rebate) + '%'
    medium_data = []
    for medium in Medium.all():
        dict_medium = {}
        dict_medium['files_update_time'] = medium.files_update_time
        dict_medium['abbreviation'] = medium.abbreviation
        dict_medium['level_cn'] = medium.level_cn
        dict_medium['id'] = medium.id
        dict_medium['name'] = medium.name
        dict_medium['level'] = medium.level or 100
        if str(medium.id) + '_2014' in medium_rebate_data:
            dict_medium['rebate_2014'] = medium_rebate_data[str(medium.id) + '_2014']
        else:
            dict_medium['rebate_2014'] = u'无'
        if str(medium.id) + '_2015' in medium_rebate_data:
            dict_medium['rebate_2015'] = medium_rebate_data[str(medium.id) + '_2015']
        else:
            dict_medium['rebate_2015'] = u'无'
        if str(medium.id) + '_2016' in medium_rebate_data:
            dict_medium['rebate_2016'] = medium_rebate_data[str(medium.id) + '_2016']
        else:
            dict_medium['rebate_2016'] = u'无'
        medium_data.append(dict_medium)
    medium_data = sorted(medium_data, key=operator.itemgetter('level'), reverse=False)
    if request.values.get('action') == 'excel':
        return write_medium_excel(mediums=medium_data)
    return tpl('/client/medium/index.html', mediums=medium_data)


@client_bp.route('/medium/<medium_id>/rebate')
def medium_rebate(medium_id):
    medium = Medium.get(medium_id)
    rebates = MediumRebate.query.filter_by(medium=medium)
    return tpl('/client/medium/rebate/index.html', medium=medium, rebates=rebates)


@client_bp.route('/medium/<medium_id>/files/<aid>/delete', methods=['GET'])
def medium_files_delete(medium_id, aid):
    print '2222'
    attachment = Attachment.get(aid)
    attachment.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("client.medium_detail", medium_id=medium_id))


@client_bp.route('/medium/<medium_id>/rebate/create', methods=['GET', 'POST'])
def medium_rebate_create(medium_id):
    medium = Medium.get(medium_id)
    if request.method == 'POST':
        rebate = float(request.values.get('rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        if MediumRebate.query.filter_by(medium=medium, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return tpl('/client/medium/rebate/create.html', medium=medium)
        MediumRebate.add(medium=medium,
                         rebate=rebate,
                         year=now_year,
                         creator=g.user,
                         create_time=datetime.datetime.now())
        flash(u'添加成功!', 'success')
        return redirect(url_for('client.medium_rebate', medium_id=medium_id))
    return tpl('/client/medium/rebate/create.html', medium=medium)


@client_bp.route('/medium/<medium_id>/rebate/<rebate_id>/update', methods=['GET', 'POST'])
def medium_rebate_update(medium_id, rebate_id):
    medium = Medium.get(medium_id)
    rebate = MediumRebate.get(rebate_id)
    if request.method == 'POST':
        rebate_num = float(request.values.get('rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        if rebate.year != now_year and MediumRebate.query.filter_by(medium=medium, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return redirect(url_for('client.medium_rebate_update', medium_id=medium_id, rebate_id=rebate_id))
        rebate.year = now_year
        rebate.rebate = rebate_num
        rebate.creator = g.user
        rebate.create_time = datetime.datetime.now()
        rebate.save()
        flash(u'修改成功!', 'success')
        return redirect(url_for('client.medium_rebate', medium_id=medium_id))
    return tpl('/client/medium/rebate/update.html', medium=medium, rebate=rebate)


@client_bp.route('/medium/<medium_id>/rebate/<rebate_id>/delete', methods=['GET'])
def medium_rebate_delete(medium_id, rebate_id):
    MediumRebate.get(rebate_id).delete()
    return redirect(url_for('client.medium_rebate', medium_id=medium_id))


@client_bp.route('/clients', methods=['GET'])
def clients():
    info = request.values.get('info', '')
    clients = Client.all()
    if info:
        clients = [c for c in clients if info in c.name]
    return tpl('clients.html', clients=clients, info=info)


@client_bp.route('/groups', methods=['GET'])
def groups():
    groups = Group.all()
    return tpl('groups.html', groups=groups)


@client_bp.route('/agents', methods=['GET'])
def agents():
    agents = Agent.all()
    agent_rebate = AgentRebate.all()
    agent_rebate_data = {}
    for k in agent_rebate:
        if str(k.agent.id) + '_' + str(k.year.year) not in agent_rebate_data:
            agent_rebate_data[str(k.agent.id) + '_' + str(k.year.year)] = str(k.inad_rebate) + '%'
    info = request.values.get('info', '')
    if info:
        agents = [k for k in agents if info in k.name]
    agent_data = []
    for agent in agents:
        dict_agent = {}
        dict_agent['id'] = agent.id
        dict_agent['name'] = agent.name
        dict_agent['group_name'] = agent.group.name
        dict_agent['group_id'] = agent.group.id
        if str(agent.id) + '_2014' in agent_rebate_data:
            dict_agent['rebate_2014'] = agent_rebate_data[str(agent.id) + '_2014']
        else:
            dict_agent['rebate_2014'] = u'无'
        if str(agent.id) + '_2015' in agent_rebate_data:
            dict_agent['rebate_2015'] = agent_rebate_data[str(agent.id) + '_2015']
        else:
            dict_agent['rebate_2015'] = u'无'
        if str(agent.id) + '_2016' in agent_rebate_data:
            dict_agent['rebate_2016'] = agent_rebate_data[str(agent.id) + '_2016']
        else:
            dict_agent['rebate_2016'] = u'无'
        agent_data.append(dict_agent)
    if request.values.get('action') == 'excel':
        return write_client_excel(agents=agent_data)
    return tpl('/client/agent/index.html', agents=agent_data, info=info)


@client_bp.route('/agent/<agent_id>/files/<aid>/delete', methods=['GET'])
def agent_files_delete(agent_id, aid):
    attachment = Attachment.get(aid)
    attachment.delete()
    flash(u'删除成功!', 'success')
    return redirect(url_for("client.agent_detail", agent_id=agent_id))


@client_bp.route('/agent/<agent_id>/rebate')
def agent_rebate(agent_id):
    agent = Agent.get(agent_id)
    rebates = AgentRebate.query.filter_by(agent=agent)
    medium_rebates = AgentMediumRebate.query.filter_by(agent=agent)
    return tpl('/client/agent/rebate/index.html',
               agent=agent, rebates=rebates,
               medium_rebates=medium_rebates)


@client_bp.route('/agent/get_rebate_json', methods=['GET', 'POST'])
def agent_get_rebate_json():
    agent_id = request.values.get('agent_id', 0)
    year = request.values.get(
        'year', datetime.datetime.now().strftime('%Y-%m-%d'))
    year = datetime.datetime.strptime(
        year, '%Y-%m-%d').replace(month=1, day=1).date()
    agent_rebates = AgentRebate.query.filter_by(
        agent_id=agent_id, year=year).first()
    if agent_rebates:
        return jsonify({'ret': True, 'rebate': agent_rebates.inad_rebate})
    return jsonify({'ret': False, 'rebate': 0})


@client_bp.route('/agent/<agent_id>/medium_rebate/create', methods=['GET', 'POST'])
def agent_medium_rebate_create(agent_id):
    agent = Agent.get(agent_id)
    mediums = Medium.all()
    if request.method == 'POST':
        rebate = float(request.values.get('rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        medium_id = int(request.values.get('medium', 0))
        try:
            medium = Medium.get(medium_id)
        except:
            flash(u'出错了，找不到该媒体!', 'danger')
            return tpl('/client/agent/rebate/medium/create.html', agent=agent)
        if AgentMediumRebate.query.filter_by(agent=agent, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return tpl('/client/agent/rebate/medium/create.html', agent=agent)
        AgentMediumRebate.add(agent=agent,
                              medium=medium,
                              rebate=rebate,
                              year=now_year,
                              creator=g.user,
                              create_time=datetime.datetime.now())
        flash(u'添加成功!', 'success')
        agent.add_comment(g.user, u"新建了媒体返点信息: 所属媒体:%s 执行年:%s 返点信息:%s%%" %
                          (medium.name, year, str(rebate)), msg_channel=9)
        return redirect(url_for('client.agent_rebate', agent_id=agent_id))
    return tpl('/client/agent/rebate/medium/create.html', agent=agent, mediums=mediums)


@client_bp.route('/agent/<agent_id>/medium_rebate/<rebate_id>/delete', methods=['GET'])
def agent_medium_rebate_delete(agent_id, rebate_id):
    rebate = AgentMediumRebate.get(rebate_id)
    agent = Agent.get(agent_id)
    agent.add_comment(g.user, u"删除了媒体返点信息: 所属媒体:%s 执行年:%s 返点信息:%s%%" %
                      (rebate.medium.name, rebate.year.year, str(rebate.rebate)), msg_channel=9)
    rebate.delete()
    return redirect(url_for('client.agent_rebate', agent_id=agent_id))


@client_bp.route('/agent/<agent_id>/medium_rebate/<rebate_id>/update', methods=['GET', 'POST'])
def agent_medium_rebate_update(agent_id, rebate_id):
    agent = Agent.get(agent_id)
    rebate = AgentMediumRebate.get(rebate_id)
    mediums = Medium.all()
    if request.method == 'POST':
        g_rebate = float(request.values.get('rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        medium_id = int(request.values.get('medium', 0))
        try:
            medium = Medium.get(medium_id)
        except:
            flash(u'出错了，找不到该媒体!', 'danger')
            return redirect(url_for('client.agent_medium_rebate_update',
                                    agent_id=agent_id,
                                    rebate_id=rebate_id,
                                    mediums=mediums))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        if rebate.year != now_year and AgentMediumRebate.query.filter_by(agent=agent, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return redirect(url_for('client.agent_medium_rebate_update',
                                    agent_id=agent_id,
                                    rebate_id=rebate_id,
                                    mediums=mediums))
        rebate.medium = medium
        rebate.year = now_year
        rebate.rebate = g_rebate
        rebate.creator = g.user
        rebate.create_time = datetime.datetime.now()
        rebate.save()
        flash(u'修改成功!', 'success')
        agent.add_comment(g.user, u"修改了媒体返点信息: 所属媒体:%s 执行年:%s 返点信息:%s%%" %
                          (medium.name, year, str(rebate.rebate)), msg_channel=9)
        return redirect(url_for('client.agent_rebate', agent_id=agent_id))
    return tpl('/client/agent/rebate/medium/update.html', agent=agent, rebate=rebate, mediums=mediums)


@client_bp.route('/agent/<agent_id>/rebate/create', methods=['GET', 'POST'])
def agent_rebate_create(agent_id):
    agent = Agent.get(agent_id)
    if request.method == 'POST':
        douban_rebate = float(request.values.get('douban_rebate', 0))
        inad_rebate = float(request.values.get('inad_rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        if AgentRebate.query.filter_by(agent=agent, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return tpl('/client/agent/rebate/create.html', agent=agent)
        AgentRebate.add(agent=agent,
                        douban_rebate=douban_rebate,
                        inad_rebate=inad_rebate,
                        year=now_year,
                        creator=g.user,
                        create_time=datetime.datetime.now())
        flash(u'添加成功!', 'success')
        agent.add_comment(g.user, u"新建了返点信息: 执行年:%s 致趣返点信息:%s%% 豆瓣返点信息:%s%%" %
                          (year, str(inad_rebate), str(douban_rebate)), msg_channel=9)
        return redirect(url_for('client.agent_rebate', agent_id=agent_id))
    return tpl('/client/agent/rebate/create.html', agent=agent)


@client_bp.route('/agent/<agent_id>/rebate/<rebate_id>/delete', methods=['GET'])
def agent_rebate_delete(agent_id, rebate_id):
    rebate = AgentRebate.get(rebate_id)
    agent = Agent.get(agent_id)
    agent.add_comment(g.user, u"删除了返点信息: 执行年:%s 致趣返点信息:%s%% 豆瓣返点信息:%s%%" %
                      (rebate.year.year, str(rebate.inad_rebate), str(rebate.douban_rebate)), msg_channel=9)
    rebate.delete()
    return redirect(url_for('client.agent_rebate', agent_id=agent_id))


@client_bp.route('/agent/<agent_id>/rebate/<rebate_id>/update', methods=['GET', 'POST'])
def agent_rebate_update(agent_id, rebate_id):
    agent = Agent.get(agent_id)
    rebate = AgentRebate.get(rebate_id)
    if request.method == 'POST':
        douban_rebate = float(request.values.get('douban_rebate', 0))
        inad_rebate = float(request.values.get('inad_rebate', 0))
        year = request.values.get(
            'year', datetime.datetime.now().strftime('%Y'))
        now_year = datetime.datetime.strptime(year, '%Y').date()
        if rebate.year != now_year and AgentRebate.query.filter_by(agent=agent, year=now_year).count() > 0:
            flash(u'该执行年返点信息已存在!', 'danger')
            return redirect(url_for('client.agent_rebate_update', agent_id=agent_id, rebate_id=rebate_id))
        rebate.year = now_year
        rebate.douban_rebate = douban_rebate
        rebate.inad_rebate = inad_rebate
        rebate.creator = g.user
        rebate.create_time = datetime.datetime.now()
        rebate.save()
        flash(u'修改成功!', 'success')
        agent.add_comment(g.user, u"修改了返点信息: 执行年:%s 致趣返点信息:%s%% 豆瓣返点信息:%s%%" %
                          (year, str(inad_rebate), str(douban_rebate)), msg_channel=9)
        return redirect(url_for('client.agent_rebate', agent_id=agent_id))
    return tpl('/client/agent/rebate/update.html', agent=agent, rebate=rebate)
