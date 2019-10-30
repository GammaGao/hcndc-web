/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 预警配置表单初始化
            this.alert_form_init();
            // 预警表单提交注册
            this.form_event();
        },
        // 预警配置表单初始化
        alert_form_init: function () {
            $.ajax({
                url: BASE.uri.base.alert_detail_api + window.conf_id + '/',
                type: 'get',
                success: function (result) {
                    let data = result.data;
                    layui.use('form', function () {
                        let form = layui.form;
                        form.val('alert_conf_detail', {
                            'alert_channel': data.alert_channel,
                            'conf_name': data.conf_name,
                            'param_host': data.param_host,
                            'param_port': data.param_port,
                            'param_config': data.param_config,
                            'param_pass': data.param_pass,
                            'is_deleted': data.is_deleted === 1
                        });
                        // 钉钉隐藏该选项
                        if (data.alert_channel === 2){
                            $('input[name=param_host]').parent().parent().css('display', 'none');
                            $('input[name=param_port]').parent().parent().css('display', 'none');
                            $('input[name=param_pass]').parent().parent().css('display', 'none');
                        }
                        form.render();
                    })
                }
            });
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(alert-save)', function (data) {
                    data = data.field;
                    data.is_deleted = data.is_deleted ? 1 : 0;
                    data.param_port = data.param_port ? data.param_port : 0;
                    $.ajax({
                        url: BASE.uri.base.alert_detail_api + window.conf_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            layer.open({
                                id: 'alert_update_success',
                                btn: ['返回列表', '留在本页'],
                                title: '修改预警配置成功',
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
                                id: 'alert_update_error',
                                title: '修改预警配置失败',
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