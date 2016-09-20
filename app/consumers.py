#coding=utf-8
from channels import Channel, Group
import json
from channels.auth import channel_session_user_from_http
from models import Room
import lycan_static
import lycan_biz
import time
import random
from common.log import logger


import sys
reload(sys)
sys.setdefaultencoding("utf-8")



# Connected to websocket.connect
@channel_session_user_from_http
def ws_connect(message):
    room_id = message.content['path'].strip("/")
    message.channel_session['room_id'] = room_id
    message.channel_session['username'] = message.user.username
    # reply_channel存入Group
    Group("room-%s" % room_id).add(message.reply_channel)
    # reply_channel存入Room
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    user = users[message.user.username]
    user['reply_channel'] = message.reply_channel.name
    room.users = json.dumps(users)
    room.save()
    logger.info(message.user.username + u"进入了房间")
    resp = {'func': lycan_static.func['chat_gm'], 'text': message.user.username + u' 进入房间'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })


# Connected to websocket.receive
@channel_session_user_from_http
def ws_message(message):
    room_id = message.channel_session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    jsonstr = message.content['text']
    jsonobj = json.loads(jsonstr)
    if jsonobj['func'] == lycan_static.func['chat_public'] and room.can_talk:
        logger.info('chat_public:' + jsonstr)
        Group("room-%s" % message.channel_session['room_id']).send({
            "text": jsonstr,
        })
    elif jsonobj['func'] == lycan_static.func['chat_lycan']:
        logger.info('chat_lycan:' + jsonstr)
        Group("room-%s-lycan" % message.channel_session['room_id']).send({
            "text": jsonstr,
        })


# Connected to websocket.disconnect
@channel_session_user_from_http
def ws_disconnect(message):
    Group("room-%s" % message.channel_session['room_id']).discard(message.reply_channel)
    room_id = message.channel_session['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    del users[message.channel_session['username']]
    room.users = json.dumps(users)
    room.save()
    # 通知更改房间人数
    resp = {'func': lycan_static.func['people_num'], 'people_num': len(users)}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 当房间无人
    if len(users) == 0:
        room.delete()
    logger.info(message.channel_session['username'] + u'离开了房间')
    resp = {'func': lycan_static.func['chat_gm'], 'text': message.channel_session['username'] + u' 离开了房间'}
    Group('room-%s' % room_id).send({
        'text': json.dumps(resp)
    })


# 天黑
def new_round(message):
    # init
    room_id = message['room_id']
    lycan_biz.round_init(room_id)
    # notify clients
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'天黑请闭眼'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # cupid_start
    Channel('cupid_start').send({
        'room_id': room_id,
    })


# 丘比特回合
def cupid_start(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    if room.game_round == 1 and lycan_biz.is_exist(room, u'丘比特'):
        resp = {'func': lycan_static.func['cupid_start']}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
    else:
        Channel('guard_start').send({
            'room_id': room_id,
        })


# 守卫回合
def guard_start(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 若守卫存在
    is_exist = lycan_biz.is_exist(room, u'守卫')
    if is_exist:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'守卫请守卫'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
    # 若守卫不在场
    if not lycan_biz.is_alive(room, u'守卫'):
        # time.sleep(random.randint(2,10))
        Channel('seer_start').send({
            'room_id': room_id,
            'delay': is_exist,
        })
        return
    # 通知
    resp = {'func': lycan_static.func['guard_start']}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })


def seer_start(message):
    if message.get('delay', False):
        time.sleep(random.randint(2,10))
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 若预言家存在
    is_exist = lycan_biz.is_exist(room, u'预言家')
    if is_exist:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'预言家请验人'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
    # 若预言家不在场
    if not lycan_biz.is_alive(room, u'预言家'):
        # time.sleep(random.randint(2,10))
        Channel('lycan_start').send({
            'room_id': room_id,
            'delay': is_exist,
        })
        return
    # 通知
    resp = {'func': lycan_static.func['seer_start']}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })


def lycan_start(message):
    if message.get('delay', False):
        time.sleep(random.randint(2,10))
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 通知狼人回合开始
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'狼人请杀人'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 若狼人不在场
    if not lycan_biz.is_alive(room, u'狼人'):
        # time.sleep(random.randint(2,10))
        Channel('witch_start').send({
            'room_id': room_id,
            'delay': True,
        })
        return
    # 通知
    resp = {'func': lycan_static.func['lycan_start']}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })


def witch_start(message):
    if message.get('delay', False):
        time.sleep(random.randint(2,10))
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 若女巫存在
    is_exist = lycan_biz.is_exist(room, u'女巫')
    if is_exist:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'女巫毒人救人'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
    # 若女巫不在场或无药
    poison = json.loads(room.poison)
    if (not lycan_biz.is_alive(room, u'女巫')) or (poison['poison'] == 0):
        # time.sleep(random.randint(2,10))
        Channel('day_start').send({
            'room_id': room_id,
            'delay': is_exist,
        })
        return
    # 通知女巫
    resp = {'func': lycan_static.func['witch_start']}
    resp['poison'] = poison['poison']
    resp['dead'] = json.loads(room.lycan)['dead']
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })


def day_start(message):
    if message.get('delay', False):
        time.sleep(random.randint(2,10))
    # 通知天亮了
    room_id = message['room_id']
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'天亮了'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 开始选警长
    Channel('vote_badge').send({
        'room_id': room_id,
    })


def vote_badge(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    talk_list = json.loads(room.talk_list)
    # 若没警长则竞选
    if not room.badge:
        # 更新自由聊天标记
        room.can_talk = True
        room.save()
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'开始竞选警长'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        resp = {'func': lycan_static.func['vote_badge']}
        for name in talk_list:
            Channel(users[name]['reply_channel']).send({
                'text': json.dumps(resp),
            })
    else:
        # 若有警长，公布夜晚死亡名单
        Channel('deliver_dead').send({
            'room_id': room_id,
        })


def deliver_dead(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    # 统计死者
    guarded = room.guarded
    poison = json.loads(room.poison)
    lycan = json.loads(room.lycan)
    dead = set()
    if lycan['dead'] != guarded and not poison['is_rescue'] and lycan['dead']:
        dead.add(lycan['dead'])
    if poison['dead']:
        dead.add(poison['dead'])
    dead = list(dead)
    # 若没死人
    if not dead:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'平安夜'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        Channel('free_talk').send({
            'room_id': room_id,
        })
        return
    # 处理死者
    hunter = lycan_biz.deal_dead(room_id, dead)
    # 猎人回合开始
    Channel('hunter_start').send({
        'room_id': room_id,
        'hunter': hunter,
    })


def hunter_start(message):
    room_id = message['room_id']
    hunter = message['hunter']
    # 若猎人未死
    if not hunter:
        # 若游戏未结束，移交警徽阶段
        if not lycan_biz.check_result(room_id):
            Channel('hand_badge').send({
                'room_id': room_id,
            })
            return
        # 若游戏结束，则终止
        else:
            return
    # 若猎人死了，开始猎人阶段
    room = Room.objects.filter(room_id=room_id)[0]
    resp = {'func': lycan_static.func['hunter_act'], "talk_list": room.talk_list, 'hunter': hunter}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })


def hand_badge(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    talk_list = json.loads(room.talk_list)
    if users[room.badge]['life'] == 0:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'请警长转交警徽'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        resp = {'func': lycan_static.func['hand_badge']}
        Channel(users[room.badge]['reply_channel']).send({
            "text": json.dumps(resp),
        })
        return
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


def free_talk(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    # 更新自由聊天标记
    room.can_talk = True
    room.save()
    # 通知
    talk_list = json.loads(room.talk_list)
    resp = {'func': lycan_static.func['free_talk'], 'talk_list': talk_list}
    for name in talk_list:
        Channel(users[name]['reply_channel']).send({
            'text': json.dumps(resp),
        })


def vote_dead(message):
    room_id = message['room_id']
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    talk_list = json.loads(room.talk_list)
    if (len(talk_list) < 2) or (len(talk_list) == 2 and not room.badge in talk_list):
        Channel('new_round').send({
            'room_id': room_id,
        })
        return
    resp = {'func': lycan_static.func['chat_gm'], 'text': u'开始票决'}
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    resp = {'func': lycan_static.func['vote_dead'], 'talk_list': talk_list}
    for name in talk_list:
        Channel(users[name]['reply_channel']).send({
            'text': json.dumps(resp),
        })
