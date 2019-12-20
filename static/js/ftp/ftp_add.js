/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // FTP配置表单默认赋值
            this.default_form_value();
            // FTP配置表单选择器监听
            this.select_form_event();
            // 任务表单事件注册
            this.form_event();
        },
        // FTP配置表单默认赋值
        default_form_value: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.val("ftp_detail", {
                    'ftp_port': '21'
                });
            })
        },
        // 数据源表单选择器监听
        select_form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(ftp_type)', function (data) {
                    let ftp_port = $('input[name=ftp_port]').val();
                    // hive / impala 认证方式
                    if (Number(data.value) === 1 && (ftp_port === '' || ftp_port === '22')) {
                        $('input[name=ftp_port]').val('21');
                    } else if (Number(data.value) === 2 && (ftp_port === '' || ftp_port === '21')) {
                        $('input[name=ftp_port]').val('22');
                    }
                    form.render();
                });
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 测试连接
                form.on('submit(ftp-test)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.ftp.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
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
                form.on('submit(ftp-save)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.ftp.add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('新增成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5, shift: 6});
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