/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // FTP配置详情请求
            this.ftp_detail_request();
            // 任务表单事件注册
            this.form_event();
        },
        // FTP配置详情请求
        ftp_detail_request: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.ftp.detail_api + window.ftp_id + '/',
                type: 'get',
                success: function (result) {
                    if (result.status === 200) {
                        that.ftp_detail_init(result.data)
                    } else {
                        layer.alert('请求FTP配置详情API异常', {icon: 5, shift: 6});
                    }
                }
            });
        },
        // FTP配置详情初始化
        ftp_detail_init: function (data) {
            layui.use('form', function () {
                let form = layui.form;
                form.val('ftp_detail', {
                    'ftp_name': data.ftp_name,
                    'ftp_desc': data.ftp_desc,
                    'ftp_type': data.ftp_type,
                    'ftp_host': data.ftp_host,
                    'ftp_port': data.ftp_port,
                    'ftp_user': data.ftp_user,
                    'ftp_passwd': data.ftp_passwd,
                    'is_deleted': data.is_deleted === 1
                });
                form.render();
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 测试连接
                form.on('submit(ftp-test)', function () {
                    $.ajax({
                        url: BASE.uri.ftp.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify({ftp_id: window.ftp_id}),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('连接成功', {icon: 6});
                            } else {
                                layer.msg(sprintf('连接失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('连接失败[%s]', result.msg), {icon: 5, shift: 6});
                        }
                    })
                });
                // 保存表单
                form.on('submit(ftp-update)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.ftp.detail_api + window.ftp_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('修改成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5, shift: 6});
                        }
                    });
                });
            });
        },
        element_init: function () {
            // 元素渲染刷新
            layui.use('element', function () {
                let element = layui.element;
                element.init();
            });
        }
    };
    new Controller();
})();