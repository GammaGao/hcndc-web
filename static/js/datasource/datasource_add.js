/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 数据源配置表单选择器监听
            this.select_form_event();
            // 任务表单事件注册
            this.form_event();
        },
        // 数据源表单选择器监听
        select_form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(source_type)', function (data) {
                    // hive / impala 认证方式
                    if (Number(data.value) < 4) {
                        $('select[name=auth_type]').parent().parent().parent().css('display', 'none');
                    } else {
                        $('select[name=auth_type]').parent().parent().parent().removeAttr('style');
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
                form.on('submit(datasource-test)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.datasource.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('连接成功', {icon: 6});
                            } else {
                                layer.msg(sprintf('连接失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('连接失败[%s]', result.msg), {icon: 5});
                        }
                    })
                });
                // 保存表单
                form.on('submit(datasource-save)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.datasource.add_api,
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
                                layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5});
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