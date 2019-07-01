/**
 * Created by xx on 2018/11/09.
 */

(function () {
    let Controller = function () {
        this.init();
    };
    Controller.prototype = {
        init: function () {
            // 登陆
            this.form_event();
        },
        form_event: function () {
            userLogin = this.userLogin;
            // layui事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(login)', function (data) {
                    data.field.password = hex_md5(data.field.password);
                    userLogin(data.field);
                });
            });
            // 键盘事件
            $(document).keydown(function (event) {
                if (event.keyCode == 13) {
                    $('button[lay-filter="login"]').click();
                }
            });
        },
        userLogin: function (data) {
            // 登陆
            $.ajax({
                url: BASE.uri.login_api,
                contentType: "application/json; charset=utf-8",
                type: 'post',
                data: JSON.stringify(data),
                success: function () {
                    window.location.href = BASE.uri.index;
                },
                error: function (error) {
                    result = error.responseJSON;
                    layer.alert(sprintf('登陆失败: %s', result.msg))
                }
            });
        }
    };
    new Controller();
})();