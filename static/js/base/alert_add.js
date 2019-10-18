/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 预警配置表单选择器监听
            this.select_form_event();
            // 预警表单提交注册
            this.form_event();
        },
        // 预警表单选择器监听
        select_form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(alert_channel)', function (data) {
                    if (data.value === '2'){
                        $('input[name=param_host]').parent().parent().css('display', 'none');
                        $('input[name=param_port]').parent().parent().css('display', 'none');
                        $('input[name=param_pass]').parent().parent().css('display', 'none');
                    } else {
                        $('input[name=param_host]').parent().parent().removeAttr('style');
                        $('input[name=param_port]').parent().parent().removeAttr('style');
                        $('input[name=param_pass]').parent().parent().removeAttr('style');
                    }
                    form.render();
                });
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(alert-save)', function (data) {
                    data = data.field;
                    data.param_port = data.param_port || 0;
                    $.ajax({
                        url: BASE.uri.base.alert_add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            layer.open({
                                id: 'alert_add_success',
                                btn: ['返回列表', '留在本页'],
                                title: '新增预警配置成功',
                                content: sprintf('状态: %s', result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.base.alert_list;
                                }
                            })
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'alert_add_error',
                                title: '新增预警配置失败',
                                content: sprintf('状态: %s', result.msg)
                            })
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