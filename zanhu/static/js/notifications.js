$(function () {
    const emptyMessage = "没有未读通知";
    const notice = $("#notifications");     // 获取通知按钮

    function checkNotifications() {
        $.ajax({
            url: "/notifications/latest-notifications/",
            cache: false,
            success: function (data) {
                if (!data.includes(emptyMessage)) {  //视图返回的data是页面的源码，其中包含如果没有通知返回 "没有未读通知"
                    // 如果页面中没有 emptyMessage = "没有未读通知"，则将给通知按钮添加一个样式
                    notice.addClass("btn-danger");
                }
            }
        })
    }

    checkNotifications();   // 页面加载时执行判断通知按钮的操作

    function update_social_activity(id_value) {
        const newsToUpdate = $('[news-id=' + id_value + ']');
        $.ajax({
            url: "/news/update-interactions/",
            type: "POST",
            data:{"id_value": id_value},
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            }
        })
    }

    notice.click(function () {
        if ($('.popover').is(":visible")) {  // is(":visible") 判断是否是可见元素
            notice.popover('hide');   // popover 是一个气泡弹框，元素可见设置为隐藏
            checkNotifications();
        } else {
            notice.popover('dispose');
            $.ajax({
                url: "/notifications/latest-notifications/",
                cache: false,
                success: function (data) {
                    notice.popover({
                        html: true,
                        trigger: 'focus',
                        container: 'body',
                        placement: 'bottom',
                        content: data,
                    });
                    notice.popover('show');
                    notice.removeClass('btn-danger')
                },
            });
        }
        return false;   // 将弹框html显示在原页面上，而不是直接跳到这个html页面
    })

    // websocket连接，使用使用wss(https)或者ws(http)
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = ws_scheme + "://" + window.location.host + "/ws/notifications/";
    const ws = new ReconnectingWebSocket(ws_path);

    // 监听后盾发送过来的消息
    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        switch (data.key) {
            case "notification":
                // 需要通知用户的通知消息
                if (currentUser !== data.actor_user) {
                    // 判断当前用户与websocket传递的数据中动作发起是否是一致的，用户自己给自己的内容进行操作不需要有通知提示
                    notice.addClass("btn-danger");
                }
                break;
            case "social_update":
                // 当发布内容有互动的时候
                if (currentUser !== data.actor_user) {
                    notice.addClass("btn-danger");  // 将通知按钮变红提示登录用户
                }
                // 获取消息提示对应内容的数据
                update_social_activity(data.id_value);
                break;
            // case "additional_news":
            //     // 当其他用户发布了动态
            //     if (currentUser !== data.actor_user) {
            //         $('.stream-update').show();
            //     }
            //     break;
            case "new_message":
                if (currentUser !== data.actor_user) {
                    notice.addClass("btn-danger");
                }
                break;
            default:
                console.log('error', data);
                break;
        }
    }


});
