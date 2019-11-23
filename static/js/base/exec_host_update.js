/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 执行服务器表单初始化
            this.exec_host_form_init();
            // 任务表单事件注册
            this.form_event();
        },
        // 任务表单初始化
        exec_host_form_init: function () {
            $.ajax({
                url: BASE.uri.base.exec_host_detail_api + window.server_id + '/',
                type: 'get',
                success: function (result) {
                    let data = result.data;
                    layui.use('form', function () {
                        let form = layui.form;
                        form.val('exec_host_detail', {
                            'server_host': data.server_host,
                            'server_name': data.server_name,
                            'is_deleted': data.is_deleted === 1
                        });
                        form.render();
                    })
                }
            });
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 测试服务器
                form.on('submit(exec-host-test)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.base.exec_host_test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            let msg = [
                                '连接成功</br>',
                                '系统: ', result.data.system, '</br>',
                                'CPU内核数: ', result.data.cpu, '</br>',
                                '硬盘总量: ', result.data.disk.total, ', 使用量: ', result.data.disk.used, '</br>',
                                '内存总量', result.data.memory.total, ', 使用量: ', result.data.memory.used, '</br>',
                            ];
                            layer.alert(msg.join(''), {icon: 6});
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('连接服务器失败: [%s]', result.msg), {icon: 2});
                        }
                    })
                });
                // 保存
                form.on('submit(exec-host-save)', function (data) {
                    data = data.field;
                    data.is_deleted = data.is_deleted ? 1 : 0;
                    $.ajax({
                        url: BASE.uri.base.exec_host_detail_api + window.server_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('修改执行服务器成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('修改执行服务器失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('修改执行服务器失败[%s]', result.msg), {icon: 5, shift: 6});
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