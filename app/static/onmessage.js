/**
 * Created by antelope on 2016/8/5.
 */
function get_roll(jsonobj, left_col, user_roll, usernames, userlives, site_url) {
    var user_num = jsonobj.usernames.length;
    for (var i = 0; i < user_num; i++) {
        usernames.push(jsonobj.usernames[i]);
        userlives.push(2);
    }
    // 画表格
    var roll_table = $("<table id='roll_table' class='table'></table>");
    left_col.append(roll_table);
    //                第一行
    var tr = $("<tr></tr>");
    tr.append($("<td></td>").html("序号"));
    for (var i = 0; i < user_num; i++) {
        var td = $("<td></td>").html(i + 1);
        tr.append(td);
    }
    roll_table.append(tr);
//                第二行
    tr = $("<tr></tr>");
    tr.append($("<td></td>").html("昵称"));
    for (var i = 0; i < user_num; i++) {
        var td = $("<td></td>").html(usernames[i]);
        tr.append(td);
    }
    roll_table.append(tr);
//                第三行
    tr = $("<tr></tr>");
    tr.append($("<td></td>").html("生命值"));
    for (var i = 0; i < user_num; i++) {
        var td = $("<td></td>").html(2);
        td.attr("id", "life_td" + i);
        tr.append(td);
    }
    roll_table.append(tr);

    // 确认身份顺序
    var roll_id1 = parseInt(jsonobj.roll1);
    var roll_id2 = parseInt(jsonobj.roll2);
    var roll_div = $("<div id='roll_div' style='border-bottom: 2px solid #428bca; " +
        "margin-bottom: 5px; padding-bottom: 5px'></div>");
    var roll_span = $("<span></span>");
    roll_span.html("您的两个身份分别是：" + roll_list[roll_id1] + "和" + roll_list[roll_id2] + "，是否将" +
        roll_list[roll_id1] + "作为第一身份？");
    // 是与否按钮
    var confirm_btn = $("<button class='btn btn-success'>是</button>");
    var deny_btn = $("<button class='btn btn-danger'>否</button>");
    confirm_btn.click(function () {
        confirm_roll_click(roll_id1, roll_id2);
    });
    deny_btn.click(function () {
        confirm_roll_click(roll_id2, roll_id1);
    });
    function confirm_roll_click(r1, r2) {
        user_roll[0] = r1;
        user_roll[1] = r2;
        roll_span.html("身份一：" + roll_list[r1] + " 身份二：" + roll_list[r2]);
        confirm_btn.remove();
        deny_btn.remove();
        $.post(site_url + "confirm_roll/", {
            roll1: r1,
            roll2: r2,
        }, function (data, statue) {
            console.log(data);
        });
    }

    left_col.append(roll_div);
    roll_div.append(roll_span);
    roll_div.append(confirm_btn);
    roll_div.append(deny_btn);

    if (roll_id1 == 6 || roll_id2 == 6) {
        confirm_roll_click(6, roll_id1+roll_id2-6);
    }
}


function cupid_start(left_col, usernames, site_url) {
    var choice;
    var cupid_div = $("<div'></div>");
    left_col.append(cupid_div);
    var msg_p = $("<p>请选择情侣</p>");
    cupid_div.append(msg_p);
    var valentine_div = $("<div class='btn-group' role='group'></div>");
    cupid_div.append(valentine_div);
    // var btns = [];
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        btn.html(usernames[i]);
        valentine_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            target = $(target);
            if (target.hasClass("btn-default")) {
                target.removeClass("btn-default");
                target.addClass("btn-success");
            } else {
                target.removeClass("btn-success");
                target.addClass("btn-default");
            }
        });
    }
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    cupid_div.append(confirm_btn);
    confirm_btn.click(function () {
        choice = [];
        var btns = valentine_div.children();
        for (var i = 0; i < btns.length; i++) {
            if ($(btns[i]).hasClass("btn-success")) {
                choice.push($(btns[i]).html());
            }
        }
        if (choice.length != 2) {
            msg_p.html("必须选择2个人");
            return;
        }
        $.post(site_url + "confirm_valentine/", {
            valentine1: choice[0],
            valentine2: choice[1],
        }, function (data, statue) {
            cupid_div.remove();
            console.log(data);
        })
    });
}


function get_valentine(jsonobj, roll_div) {
    var valentine_span = $("<span></span>");
    valentine_span.html(" 您的情侣是 " + jsonobj.name + ", 他的身份分别为：" + jsonobj.roll1 + ", "
        + jsonobj.roll2);
    roll_div.append(valentine_span);
}


function guard_start(left_col, usernames, userlives, site_url) {
    var choice = "";
    var guard_div = $("<div'></div>");
    left_col.append(guard_div);
    var msg_p = $("<p>请守卫一位玩家</p>");
    guard_div.append(msg_p);
    var guarded_div = $("<div class='btn-group' role='group'></div>");
    guard_div.append(guarded_div);
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        if (userlives[i] < 1) btn.attr("disabled", true);
        btn.html(usernames[i]);
        guarded_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target = $(target);
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = guarded_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    guard_div.append(confirm_btn);
    confirm_btn.click(function () {
        if (choice == "") {
            msg_p.html("必须守卫一位玩家");
            return;
        }
        $.post(site_url + "confirm_guarded/", {
            guarded: choice,
        }, function (data, statue) {
            guard_div.remove();
            console.log(data);
        })
    });
}

function seer_start(left_col, usernames, userlives, site_url) {
    var choice = "";
    var seer_div = $("<div'></div>");
    left_col.append(seer_div);
    var msg_p = $("<p>请预言一位玩家</p>");
    seer_div.append(msg_p);
    var seen_div = $("<div class='btn-group' role='group'></div>");
    seer_div.append(seen_div);
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        if (userlives[i] < 1) btn.attr("disabled", true);
        btn.html(usernames[i]);
        seen_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target = $(target);
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = seen_div.children();
    var request_btn = $("<button class='btn btn-warning'>确定</button>");
    seer_div.append(request_btn);
    request_btn.click(function () {
        if (choice == "") {
            msg_p.html("必须选择一位玩家");
            return;
        }
        $.post(site_url + "request_seen/", {
            seen: choice,
        }, function (data, statue) {
            msg_p.html(choice + "是" + data + ",确认后请点击按钮继续游戏。");
            seen_div.remove();
            request_btn.remove();
            seer_div.append(confirm_btn);
        })
    });
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        $(this).attr('disabled','disabled');
        $.post(site_url + "confirm_seen/", {}, function (data, statue) {
            seer_div.remove();
            console.log(data);
        })
    })
}

function lycan_start(left_col, usernames, userlives, site_url) {
    var choice = "";
    var lycan_div = $("<div id='lycan_div'></div>");
    left_col.append(lycan_div);
    var msg_p = $("<p>请选择死人</p>");
    lycan_div.append(msg_p);
    var dead_div = $("<div class='btn-group' role='group'></div>");
    lycan_div.append(dead_div);
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        btn.html(usernames[i]);
        if (userlives[i] < 1) btn.attr("disabled", true);
        dead_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target = $(target);
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = dead_div.children();
    var request_btn = $("<button class='btn btn-warning'>确定</button>");
    lycan_div.append(request_btn);
    request_btn.click(function () {
        if (choice == "") {
            msg_p.html("必须选择一位玩家");
            return;
        }
        $.post(site_url + "confirm_dead/", {
            choice: choice,
        }, function (data, statue) {
            msg_p.html("您已选择" + choice + ",正等待其他人选择，期间可以变更选择。");
            console.log("success");
        })
    });
}


function witch_start(left_col, usernames, userlives, site_url, poison, dead) {
    var choice = "";
    var is_rescue = false;
    var witch_div = $("<div'></div>");
    left_col.append(witch_div);
    var rescue_div = $("<div></div>");
    var poison_div = $("<div></div>");
    var dead_div = $("<div class='btn-group' role='group'></div>");
    if (poison % 2 != 0 && dead != "") {
        var rescue_span = $("<span></span>");
        rescue_span.html("今晚被咬的是" + dead + "，是否使用解药？");
        var rescue_btn = $("<button class='btn btn-danger'>否</button>");
        rescue_btn.click(function () {
            if (rescue_btn.hasClass("btn-success")) {
                rescue_btn.removeClass("btn-success");
                rescue_btn.addClass("btn-danger");
                rescue_btn.html("否");
                is_rescue = false;
            } else {
                rescue_btn.removeClass("btn-danger");
                rescue_btn.addClass("btn-success");
                rescue_btn.html("是");
                is_rescue = true;
            }
        });
        witch_div.append(rescue_div);
        rescue_div.append(rescue_span);
        rescue_div.append(rescue_btn);
    }
    if (poison >> 1 > 0) {
        var msg_p = $("<p>是否需要使用毒药？</p>");
        for (var i = 0; i < usernames.length; i++) {
            var btn = $("<button type='button' class='btn btn-default'></button>");
            btn.html(usernames[i]);
            if (userlives[i] < 1) btn.attr("disabled", true);
            dead_div.append(btn);
            btn.click(function (ev) {
                var target = ev.target || ev.srcElement;
                target = $(target);
                if (target.hasClass("btn-success")) {
                    target.removeClass("btn-success");
                    choice = "";
                    return;
                }
                for (var i = 0; i < btns.length; i++) {
                    $(btns[i]).removeClass("btn-success");
                }
                target.addClass("btn-success");
                choice = target.html();
            });
        }
        witch_div.append(poison_div);
        poison_div.append(msg_p);
        poison_div.append(dead_div);
    }
    var btns = dead_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        $.post(site_url + "confirm_witch/", {
            choice: choice,
            is_rescue: is_rescue,
        }, function (data, statue) {
            witch_div.remove();
            console.log(data);
        })
    });
    witch_div.append(confirm_btn);
}


function update_dead(usernames, userlives, lost_dict) {
    for (var i = 0; i < usernames.length; i++) {
        for (var name in lost_dict) {
            if (usernames[i] == name) {
                userlives[i] -= lost_dict[name];
                $("#life_td" + i).html(userlives[i]);
                god_say(name + "死了")
                if (userlives[i] == 0) {
                    god_say(name + " out")
                }
            }
        }
    }
}

function hunter_act(left_col, usernames, talk_list, site_url) {
    var choice = "";
    var hunter_div = $("<div'></div>");
    var msg_p = $("<p>请拉一位玩家同归于尽</p>");
    var hunted_div = $("<div class='btn-group' role='group'></div>");
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        if ($.inArray(usernames[i], talk_list) == -1) 
            btn.attr("disabled", true);
        btn.html(usernames[i]);
        hunted_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target = $(target);
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = hunted_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        if (choice == "") {
            msg_p.html("必须带走一位玩家");
            return;
        }
        $.post(site_url + "confirm_hunted/", {
            hunted: choice,
        }, function (data, statue) {
            hunter_div.remove();
            console.log(data);
        })
    });
    left_col.append(hunter_div);
    hunter_div.append(msg_p);
    hunter_div.append(hunted_div);
    hunter_div.append(confirm_btn);
}


function free_talk(left_col, site_url) {
    var confirm_btn = $("<button class='btn btn-warning'>发言结束</button>");
    confirm_btn.click(function () {
        confirm_btn.remove();
        $.post(site_url + "finish_talk/", {}, function (data, statue) {
            console.log(data);
        })
    });
    left_col.append(confirm_btn);
}


function vote_badge(left_col, usernames, site_url) {
    var choice = "";
    var vote_div = $("<div id='vote_badge_div' ></div>");
    var msg_p = $("<p>投票选举警长</p>");
    var voted_div = $("<div class='btn-group' role='group'></div>");
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        btn.html(usernames[i]);
        voted_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            target = $(target);
            if (target.hasClass("btn-success")) {
                target.removeClass("btn-success");
                choice = "";
                return;
            }
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = voted_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        vote_div.remove();
        $.post(site_url + "vote_badge/", {
            choice: choice,
        }, function (data, statue) {
            console.log(data);
        })
    });
    left_col.append(vote_div);
    vote_div.append(msg_p);
    vote_div.append(voted_div);
    vote_div.append(confirm_btn);
}


function hand_badge(left_col, usernames, userlives, site_url) {
    var choice = "";
    var hand_div = $("<div></div>");
    var msg_p = $("<p>警徽给一位玩家</p>");
    var handed_div = $("<div class='btn-group' role='group'></div>");
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        if (userlives[i] < 1) btn.attr("disabled", true);
        btn.html(usernames[i]);
        handed_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target = $(target);
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = handed_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        if (choice == "") {
            msg_p.html("必须给一位玩家");
            return;
        }
        $.post(site_url + "hand_badge/", {
            choice: choice,
        }, function (data, statue) {
            hand_div.remove();
            console.log(data);
        })
    });
    left_col.append(hand_div);
    hand_div.append(msg_p);
    hand_div.append(handed_div);
    hand_div.append(confirm_btn);
}


function vote_dead(left_col, usernames, talk_list, site_url) {
    var choice = "";
    var vote_div = $("<div id='vote_dead_div'></div>");
    var msg_p = $("<p>投票决定处死谁</p>");
    var voted_div = $("<div class='btn-group' role='group'></div>");
    for (var i = 0; i < usernames.length; i++) {
        var btn = $("<button type='button' class='btn btn-default'></button>");
        if ($.inArray(usernames[i], talk_list) == -1) btn.attr("disabled", true);
        btn.html(usernames[i]);
        voted_div.append(btn);
        btn.click(function (ev) {
            var target = ev.target || ev.srcElement;
            target = $(target);
            if (target.hasClass("btn-success")) {
                target.removeClass("btn-success");
                choice = "";
                return;
            }
            for (var i = 0; i < btns.length; i++) {
                $(btns[i]).removeClass("btn-success");
            }
            target.addClass("btn-success");
            choice = target.html();
        });
    }
    var btns = voted_div.children();
    var confirm_btn = $("<button class='btn btn-warning'>确定</button>");
    confirm_btn.click(function () {
        vote_div.remove();
        $.post(site_url + "vote_dead/", {
            choice: choice,
        }, function (data, statue) {
            console.log(data);
        })
    });
    left_col.append(vote_div);
    vote_div.append(msg_p);
    vote_div.append(voted_div);
    vote_div.append(confirm_btn);
}