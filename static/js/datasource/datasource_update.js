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
            // 数据源详情请求
            this.datasource_detail_request();
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
        // 数据源详情请求
        datasource_detail_request: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.datasource.detail_api + window.source_id + '/',
                type: 'get',
                success: function (result) {
                    if (result.status === 200) {
                        that.datasource_detail_init(result.data)
                    } else {
                        layer.alert('请求数据源详情API异常', {icon: 5, shift: 6});
                    }
                }
            });
        },
        // 数据源详情初始化
        datasource_detail_init: function (data) {
            layui.use('form', function () {
                let form = layui.form;
                form.val('datasource_detail', {
                    'source_name': data.source_name,
                    'source_type': data.source_type,
                    'source_host': data.source_host,
                    'source_port': data.source_port,
                    'source_user': data.source_user,
                    'source_password': data.source_password,
                    'source_desc': data.source_desc,
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
                form.on('submit(datasource-test)', function (data) {
                    $.ajax({
                        url: BASE.uri.datasource.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify({source_id: window.source_id}),
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
                form.on('submit(datasource-update)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.datasource.detail_api + window.source_id + '/',
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