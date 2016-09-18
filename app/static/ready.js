/**
 * Created by antelope on 2016/8/5.
 */
function init_register_window(register_window) {
    register_window.kendoWindow({
        visible: false,
        modal: true,
        actions: [],
        resizable: false,
        height: 300,
        width: 400,
        position: {
            top: "30%",
            left: "20%",
        },
    });
}

function init_prepare_window(prepare_window) {
    prepare_window.kendoWindow({
        visible: false,
        modal: true,
        actions: [],
        resizable: false,
        height: 300,
        width: 400,
        position: {
            top: "30%",
            left: "20%",
        },
    });
}

var roll_list = ['狼人', '平民', '预言家', '女巫', '守卫', '猎人', '丘比特'];

//滑动至底部
function chat_scroll(panel) {
    panel.scrollTop = panel.scrollHeight;
}