#coding=utf-8
import random
import json
from models import Room
from . import lycan_static
from channels import Channel, Group
from common.log import logger

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def game_start(room_id):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    # 角色分配
    rolls = lycan_static.roll_num[str(len(users))]
    roll_list = []
    for id in rolls:
        for i in range(0, rolls[id]):
            roll_list.append(id)
    random.shuffle(roll_list)
    roll_index = 0
    usernames = []
    for i in range(0, len(users)):
        for username in users:
            if(users[username]['pos'] == i):
                usernames.append(username)
    for username in users:
        # 角色存入room
        user = users[username]
        resp = {}
        resp['func'] = lycan_static.func['send_roll']
        resp['roll1'] = roll_list[roll_index]
        resp['roll2'] = roll_list[roll_index + 1]
        if(lycan_static.roll_name[resp['roll1']] == u'盗贼' or lycan_static.roll_name[resp['roll2']] == u'盗贼'):
            resp['roll3'] = roll_list[len(users) * 2]
            resp['roll4'] = roll_list[len(users) * 2 + 1]
        roll_index += 2
        resp['usernames'] = usernames
        Channel(user['reply_channel']).send({
            'text': json.dumps(resp),
        })
    room.users = json.dumps(users)
    room.has_started = True
    room.save()


def is_exist(room, roll_name):
    roll_id = 0
    for id in lycan_static.roll_name:
        if lycan_static.roll_name[id] == roll_name:
            roll_id = id
    users = json.loads(room.users)
    return lycan_static.roll_num[str(len(users))][str(roll_id)] > 0


def is_alive(room, roll_name):
    users = json.loads(room.users)
    for username in users:
        user_life = users[username]['life']
        if user_life == 0:
            continue
        if lycan_static.roll_name[users[username]['roll' + str(3 - user_life)]] == roll_name:
            return True
    return False


def current_roll(room, username):
    if not username:
        return ''
    users = json.loads(room.users)
    user_life = users[username]['life']
    if user_life < 1:
        return ''
    return lycan_static.roll_name[users[username]['roll' + str(3 - user_life)]]


def round_init(room_id):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    # 回合数+1
    room.game_round += 1
    # 晚上都不能说话
    room.can_talk = False
    # 初始化结束发言记录
    room.finish_talk = '[]'
    # 初始化能发言的人
    talk_list = []
    for name in users:
        if users[name]['life'] > 0:
            talk_list.append(name)
    room.talk_list = json.dumps(talk_list)
    # 初始化投票记录
    room.vote_dead = '{}'
    # 初始化守卫选择
    if is_exist(room, u'守卫'):
        guarded = json.loads(room.guarded)
        guarded['last'] = guarded['now']
        guarded['now'] = ''
        room.guarded = json.dumps(guarded)
    # 初始化狼人选择
    if is_exist(room, u'狼人'):
        # 清除Group
        previous_lycan = json.loads(room.lycan)
        for name in previous_lycan['lycan_choice']:
            Group("room-%s-lycan" % room_id).discard(Channel(users[name]['reply_channel']))
        # 找出狼人
        lycan_choice = {}
        for username in users:
            # if lycan_static.roll_name[users[username]['roll1']] == u'狼人':
            if current_roll(room, username) == u'狼人':
                Group("room-%s-lycan" % room_id).add(Channel(users[username]['reply_channel']))
                lycan_choice[username] = ''
        lycan = {
            'lycan_choice': lycan_choice,
            'dead': ''
        }
        room.lycan = json.dumps(lycan)
    # 初始化女巫选择
    if is_exist(room, u'女巫'):
        poison = json.loads(room.poison)
        poison['dead'] = ''
        poison['is_rescue'] = False
        room.poison = json.dumps(poison)
    # 初始化死人
    room.dead = '[]'
    room.save()


def check_sheep(room_id):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    for name in users:
        if current_roll(room, name) == u'替罪羊':
            return name
    return ''


def deal_dead(room_id, dead):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    hunter = ''
    elder = ''
    # 生命减少记录
    lost_dict = {}
    for name in dead:
        lost_dict[name] = 1
    # 若有情侣死透，则两人皆死透
    valentine = json.loads(room.valentine)
    for name in valentine:
        if users[name]['life'] == 1 and name in dead:
            for name1 in valentine:
                lost_dict[name1] = users[name1]['life']
    for name in lost_dict:
        for i in range(0, lost_dict[name]):
            if lycan_static.roll_name[users[name]['roll' + str(3 + i - users[name]['life'])]] == u'猎人':
                hunter = name
            if lycan_static.roll_name[users[name]['roll' + str(3 + i - users[name]['life'])]] == u'长老':
                elder = name
                for name in users:
                    if users[name]['life'] > 0 and (current_roll(room, name) != u'狼人'):
                        users[name]['roll' + str(3 - users[name]['life'])] = '1'
                room.users = json.dumps(users)
                room.save()
    update_dead(room_id, lost_dict, elder)
    # 根据生命减少查看是否有猎人
    return hunter


def update_dead(room_id, lost_dict, elder):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    talk_list = json.loads(room.talk_list)
    # 生命减少,且从可交流列表移除
    for name in lost_dict:
        users[name]['life'] -= lost_dict[name]
        talk_list.remove(name)
    room.users = json.dumps(users)
    room.talk_list = json.dumps(talk_list)
    room.save()
    logger.info(room_id + ':' + json.dumps(lost_dict))
    # 客户端通知更新命数
    resp = {'func': lycan_static.func['notify_dead']}
    resp['lost_dict'] = lost_dict
    Group("room-%s" % room_id).send({
        "text": json.dumps(resp),
    })
    # 判断长老
    if elder:
        resp = {'func': lycan_static.func['chat_gm'], 'text': u'长老死了，所有玩家现有角色失去功能'}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })



# 返回票数最多的名字或‘’
def count_vote(vote_list):
    from collections import Counter
    c = Counter()
    for name in vote_list:
        if vote_list[name]:
            c[vote_list[name]] += 1
    max_vote_num = 0
    for name in vote_list:
        if max_vote_num < c[name]:
            max_vote_num = c[name]
    same_vote = []
    for name in vote_list:
        if max_vote_num == c[name]:
            same_vote.append(name)
    if len(same_vote) == 1:
        return same_vote[0]
    else:
        return ''


# 判断是否结束
def check_result(room_id):
    room = Room.objects.filter(room_id=room_id)[0]
    users = json.loads(room.users)
    result = ''
    # 还活着的
    alive_list = []
    for name in users:
        if users[name]['life'] > 0:
            alive_list.append(name)
    # 判断平局
    if len(alive_list) == 0:
        result = u'同归于尽'
    # 判断情侣获胜
    if len(alive_list) == 2 and alive_list[0] in json.loads(room.valentine):
        result = u'情侣获胜'
    # 判断狼人或平民获胜
    lycan_num = 0
    for name in alive_list:
        if lycan_static.roll_name[users[name]['roll1']] == u'狼人' \
                or lycan_static.roll_name[users[name]['roll2']] == u'狼人':
            lycan_num += 1
    if lycan_num == 0 and len(alive_list) != 0:
        result += u'平民获胜'
    if lycan_num == len(alive_list) and len(alive_list) != 0:
        result += u'狼人获胜'
    if result:
        resp = {'func': lycan_static.func['chat_gm'], 'text': result}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
        display_roll = ''
        publish_result = json.loads(room.publish_result)
        for i in range(0, len(users)):
            for name in users:
                if users[name]['pos'] == i:
                    display_roll += name + ' 的身份为：' + lycan_static.roll_name[publish_result[name]['roll1']] + ' '\
                                   + lycan_static.roll_name[publish_result[name]['roll2']] + '\n'
        resp = {'func': lycan_static.func['chat_gm'], 'text': display_roll}
        Group("room-%s" % room_id).send({
            "text": json.dumps(resp),
        })
    return result