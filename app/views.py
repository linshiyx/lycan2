#coding=utf-8
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from common.mymako import render_mako_context, render_json
from django.contrib.auth.models import User
from models import Room
import json
import lycan_biz
import lycan_static
from channels import Channel, Group
from common.log import logger

# Create your views here.

import sys
reload(sys)
sys.setdefaultencoding("utf-8")



def index(request):
    # 强制response中包含csrftoken，在蓝鲸中删去
    request.META["CSRF_COOKIE_USED"] = True

    if request.user.is_authenticated():
        return render_mako_context(request, 'home.html', {'username': request.user.username, 'SITE_URL': '/'})
    else:
        return render_mako_context(request, 'home.html', {'username': '', 'SITE_URL': '/'})


def register_ajax(request):
    username = request.POST['nick']
    password = request.POST['psd']
    if User.objects.filter(username=username).exists():
        return HttpResponse(u'用户名已存在')
    user = User.objects.create_user(username=username, password=password)
    user.save()
    user = authenticate(username=username, password=password)
    login(request, user)
    return HttpResponse('success')


def login_ajax(request):
    username = request.POST['nick']
    password = request.POST['psd']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse('success')
        else:
            return HttpResponse(u'用户被禁')
    else:
        return HttpResponse(u'登录失败')


def create_room(request):
    user = request.user
    room_id = request.POST['room_id']
    room = Room.objects.filter(room_id=room_id)
    if not room:
        # 创建房间
        room = Room.objects.create(room_id=room_id)
        room.game_round = 0
        room.users = json.dumps({user.username : {'ready' : '0', 'pos' : 0, 'life': 2}})
        room.save()
        # 房间存入session
        request.session['room_id'] = room_id
        request.session.modified = True
        resp = {}
        resp['username'] = user.username
        resp['pos'] = 0
        resp['result'] = 'success'
        resp['people_num'] = 1
        return HttpResponse(json.dumps(resp))
    else:
        return HttpResponse(json.dumps({'result': u'房间名已存在'}))


def join_room(request):
    user = request.user
    room_id = request.POST['room_id']
    room = Room.objects.filter(room_id=room_id)
    if not room:
        return HttpResponse(json.dumps({'result': u'房间名不存在'}))
    elif room[0].has_started:
        return HttpResponse(json.dumps({'result': u'游戏已开始'}))
    else:
        room = room[0]
        # 加入房间
        users = json.loads(room.users)
        users[user.username] = {'ready' : '0', 'pos' : len(users), 'life': 2}
        room.users = json.dumps(users)
        room.save()
        # 房间存入session
        request.session['room_id'] = room_id
        request.session.modified = True
        # 通知更改房间人数
        resp = {'func': lycan_static.func['people_num'], 'people_num': len(users)}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        resp = {}
        resp['username'] = user.username
        resp['pos'] = len(users) - 1
        resp['result'] = 'success'
        resp['people_num'] = len(users)
        return HttpResponse(json.dumps(resp))


def ready(request):
    ready = request.POST['ready']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    if room.has_started:
        return
    users = json.loads(room.users)
    user = users[request.user.username]
    logger.debug(request.user.username + ' ready')
    if(ready == '0'):
        resp = {'func': lycan_static.func['chat_gm'], 'text': request.user.username + u' 已准备'}
        Group('room-%s' % room_id).send({
            'text': json.dumps(resp)
        })
        user['ready'] = '1'
        room.users = json.dumps(users)
        room.save()
        all_ready = True
        for username in users:
            if users[username]['ready'] == '0':
                all_ready = False
        if all_ready and len(users)>1:
            lycan_biz.game_start(room_id)
        return HttpResponse('1')
    else:
        user['ready'] = '0'
        room.users = json.dumps(users)
        room.save()
        resp = {'func': lycan_static.func['chat_gm'], 'text': request.user.username + u' 取消准备'}
        Group('room-%s' % room_id).send({
            'text': json.dumps(resp)
        })
        return HttpResponse('0')


def confirm_roll(request):
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    user = users[request.user.username]
    if user.get('roll1', ''):
        return
    logger.debug(request.user.username + ' confirm_roll:' + request.POST['roll1'] + ' ' + request.POST['roll2'])
    # 保存用户身份
    user['roll1'] = request.POST['roll1']
    user['roll2'] = request.POST['roll2']
    room.users = json.dumps(users)
    room.save()
    resp = {'func': lycan_static.func['chat_gm'], 'text': request.user.username + u' 已确认身份'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })
    # 判断是否全部确认完毕
    all_confirm = True
    for username in users:
        user = users[username]
        if not user.get('roll1'):
            all_confirm = False
    if all_confirm:
        Channel('new_round').send({
            'room_id': room_id,
        })
    return HttpResponse('confirm_roll_success')


def confirm_valentine(request):
    valentine1 = request.POST['valentine1']
    valentine2 = request.POST['valentine2']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    # 保存情侣
    if room.valentine != '[]':
        return
    logger.debug('confirm_valentine：' + valentine1.decode().encode('utf-8') + ' ' + valentine2.decode().encode('utf-8'))
    room.valentine = json.dumps([valentine1, valentine2])
    room.save()
    # 通知情侣1
    resp = {'func': lycan_static.func['valentine_recgonize']}
    resp['name'] = valentine2
    resp['roll1'] = lycan_static.roll_name[users[valentine2]['roll1']]
    resp['roll2'] = lycan_static.roll_name[users[valentine2]['roll2']]
    Channel(users[valentine1]['reply_channel']).send({
        "text": json.dumps(resp),
    })
    # 通知情侣2
    resp['name'] = valentine1
    resp['roll1'] = lycan_static.roll_name[users[valentine1]['roll1']]
    resp['roll2'] = lycan_static.roll_name[users[valentine1]['roll2']]
    Channel(users[valentine2]['reply_channel']).send({
        "text": json.dumps(resp),
    })
    # 守卫开始
    Channel('guard_start').send({
        'room_id': room_id,
    })
    return HttpResponse('confirm_valentine_success')


def confirm_guarded(request):
    choice = request.POST['guarded']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    guarded = json.loads(room.guarded)
    if guarded['now']:
        return
    guarded['now'] = choice
    logger.debug('confirm_guarded:' + guarded['now'])
    room.guarded = json.dumps(guarded)
    room.save()
    Channel('seer_start').send({
        'room_id': room_id,
    })
    return HttpResponse('confirm_guarded_success')


def request_seen(request):
    seen = request.POST['seen']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    logger.debug('seen:' + seen)
    # users = json.loads(room.users)
    # user = users[seen]
    # if lycan_static.roll_name[user['roll1']] == u'狼人':
    if lycan_biz.current_roll(room, seen) == u'狼人':
        return HttpResponse('坏人')
    else:
        return HttpResponse('好人')


def confirm_seen(request):
    logger.debug('confirm_seen')
    room_id = request.session['room_id']
    Channel('lycan_start').send({
        'room_id': room_id,
    })
    return HttpResponse('confirm_seen_success')


def confirm_dead(request):
    username = request.user.username
    choice = request.POST['choice']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    lycan = json.loads(room.lycan)
    logger.debug('confirm_dead:' + username + '->' + choice)
    lycan_choice = lycan['lycan_choice']
    lycan_choice[username] = choice
    room.lycan = json.dumps(lycan)
    room.save()
    same = True
    for name in lycan_choice:
        if lycan_choice[name] != choice:
            break
            same = False
    if not same:
        return HttpResponse('not same')
    else:
        lycan['dead'] = choice
        room.lycan = json.dumps(lycan)
        room.save()
        resp = {'func': lycan_static.func['lycan_end']}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        Channel('witch_start').send({
            'room_id': room_id,
        })
    return HttpResponse('lycan_choose_success')


def confirm_witch(request):
    choice = request.POST['choice']
    is_rescue = request.POST['is_rescue']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    poison = json.loads(room.poison)
    # if poison['dead'] != 'cantbeaname':
    #     return
    logger.debug('confirm_witch:' + choice + ' ' + is_rescue)
    if choice:
        poison['poison'] -= 2
        poison['dead'] = choice
    else:
        poison['dead'] = ''
    if is_rescue == 'true':
        poison['poison'] -= 1
        poison['is_rescue'] = True
    room.poison = json.dumps(poison)
    room.save()
    Channel("day_start").send({
        'room_id': room_id,
    })
    return HttpResponse("witch_success")


def vote_badge(request):
    username = request.user.username
    choice = request.POST['choice']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    talk_list = json.loads(room.talk_list)
    logger.debug('vote_badge:' + username + '->' + choice)
    resp = {'func': lycan_static.func['chat_gm'], 'text': username + u' 已投票'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })
    # 更新投票记录
    vote_list = json.loads(room.vote_badge)
    vote_list[username] = choice
    room.vote_badge = json.dumps(vote_list)
    room.save()
    # 若还有人没投票则继续等待
    if len(talk_list) != len(vote_list):
        return HttpResponse("wait_others_to_vote")
    # 统计投票结果
    room.badge = lycan_biz.count_vote(vote_list)
    room.save()
    # 公布投票结果
    text = u'投票结果：\n'
    for name in vote_list:
        if vote_list[name]:
            text += name + "->" +  vote_list[name] + "\n"
        else:
            text += name + u'弃权\n'
    resp = {'func': lycan_static.func['chat_gm'], 'text': text}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 若选出警长
    if room.badge:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'警长为' + room.badge}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        users = json.loads(room.users)
        resp = {'func': lycan_static.func['change_badge'], 'badge_id':  users[room.badge]['pos']}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        Channel('deliver_dead').send({
            "room_id": room_id,
        })
        return HttpResponse('vote_badge_success')
    # 若票数相同
    room.vote_badge = '{}'
    room.save()
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'最高票相同，请重新为警长投票'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    users = json.loads(room.users)
    resp = {'func': lycan_static.func['vote_badge']}
    for name in talk_list:
        Channel(users[name]['reply_channel']).send({
            'text': json.dumps(resp),
        })
    return HttpResponse("重新竞选警长")


def confirm_hunted(request):
    hunted = request.POST['hunted']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    logger.debug('confirm_hunted:' + hunted)
    lycan_biz.deal_dead(room_id, [hunted])
    # 游戏是否结束
    if lycan_biz.check_result(room_id):
        return HttpResponse("game_over")
    # 若游戏未结束
    Channel('hand_badge').send({
        'room_id': room_id,
    })
    return HttpResponse("hunter_success")


def hand_badge(request):
    choice = request.POST['choice']
    room_id = request.session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 保存转交结果
    room.badge = choice
    room.save()
    logger.debug('hand_badge:' + choice)
    # 通知转交结果
    users = json.loads(room.users)
    resp = {'func': lycan_static.func['change_badge'], 'badge_id': users[room.badge]['pos']}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'警长为' + room.badge}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 若暂时都死，则不投票直接下一回合
    if not json.loads(room.talk_list):
        Channel('new_round').send({
            'room_id': room_id,
        })
    # 若有人可投票但投票记录为空，则自由发言
    elif not json.loads(room.vote_dead):
        Channel('free_talk').send({
            'room_id': room_id,
        })
    # 若有人可投票且有投票记录，则开始下一回合
    else:
        Channel('new_round').send({
            'room_id': room_id,
        })
    return HttpResponse('hand_badge_success')


def finish_talk(request):
    username = request.user.username
    room_id = request.session['room_id']
    logger.debug('finish_talk:' + username)
    resp = {'func': lycan_static.func['chat_gm'], 'text': username + u' 结束发言'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })
    room = Room.objects.filter(room_id=room_id)[0]
    finish_list = json.loads(room.finish_talk)
    finish_set = set(finish_list)
    finish_set.add(username)
    finish_list = list(finish_set)
    room.finish_talk = json.dumps(finish_list)
    room.save()
    talk_list = json.loads(room.talk_list)
    if len(talk_list) == len(finish_list):
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'发言结束，游戏继续'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        Channel('vote_dead').send({
            'room_id': room_id,
        })
        return HttpResponse('talk_finish')
    return HttpResponse('wait_others_finish_talk')


def vote_dead(request):
    username = request.user.username
    choice = request.POST['choice']
    room_id = request.session['room_id']
    resp = {'func': lycan_static.func['chat_gm'], 'text': username + u' 已投票'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })
    logger.debug('vote_dead:' + username + '->' + choice)
    room = Room.objects.filter(room_id=room_id)[0]
    talk_list = json.loads(room.talk_list)
    # 更新投票记录
    vote_list = json.loads(room.vote_dead)
    vote_list[username] = choice
    room.vote_dead = json.dumps(vote_list)
    room.save()
    # 若还有人没投票则继续等待
    if len(talk_list) != len(vote_list):
        return HttpResponse("wait_others_to_vote")
    # 公布投票结果
    text = u'投票结果：\n'
    for name in vote_list:
        if vote_list[name]:
            text += name + "->" + vote_list[name] + "\n"
        else:
            text += name + u' 弃权\n'
    resp = {'func': lycan_static.func['chat_gm'], 'text': text}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 统计投票结果
    # 警长多一票
    badge_vote = ''
    for name in vote_list:
        if name == room.badge:
            badge_vote = vote_list[name]
    vote_list['badge'] = badge_vote
    dead = lycan_biz.count_vote(vote_list)
    # 若选出死者
    if dead:
        # 处理投票结果
        hunter = lycan_biz.deal_dead(room_id, [dead])
        # 猎人回合开始
        Channel('hunter_start').send({
            'room_id': room_id,
            'hunter': hunter,
        })
        return HttpResponse('vote_dead_success')
    # 若票数相同
    room.vote_dead = '{}'
    room.save()
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'最高票相同，请重新投票'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    users = json.loads(room.users)
    resp = {'func': lycan_static.func['vote_dead'], 'talk_list': talk_list}
    for name in talk_list:
        Channel(users[name]['reply_channel']).send({
            'text': json.dumps(resp),
        })
    return HttpResponse("重新票决")
