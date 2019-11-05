/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 工作流名称请求
            this.interface_list_id_req();
            // 服务器名称请求
            this.exec_host_req();
            // 任务列表请求
            this.job_list_req();
            // 任务参数请求
            this.job_params_req();
            // 任务表单事件注册
            this.form_event();
        },
        // 工作流ID渲染
        interface_list_id_req: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        for (let i = 0; i < res.data.length; i++) {
                            html.push(sprintf(
                                '<option value="%s">%s(%s)</option>',
                                res.data[i].interface_id,
                                res.data[i].interface_id,
                                res.data[i].interface_name
                            ))
                        }
                        $('select[name=interface_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 任务列表请求
        job_list_req: function () {
            $.ajax({
                url: BASE.uri.job.id_list_api,
                type: 'get',
                success: function (res) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    for (let i = 0; i < res.data.length; i++) {
                        html.push(sprintf('<option value="%s">%s(%s)</option>',
                            res.data[i].job_id,
                            res.data[i].job_id,
                            res.data[i].job_name
                        ))
                    }
                    $('select[xm-select=job_prep]').append(html.join(''));
                    formSelects.render('job_prep');
                }
            })
        },
        // 任务参数请求
        job_params_req: function () {
            $.ajax({
                url: BASE.uri.params.id_list_api,
                type: 'get',
                success: function (res) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    for (let i = 0; i < res.data.length; i++) {
                        html.push(sprintf('<option value="%s">%s(%s)</option>',
                            res.data[i].param_id,
                            res.data[i].param_id,
                            res.data[i].param_name
                        ))
                    }
                    $('select[xm-select=job_params]').append(html.join(''));
                    formSelects.render('job_params');
                }
            })
        },
        // 执行服务器请求
        exec_host_req: function () {
            $.ajax({
                url: BASE.uri.base.exec_host_api,
                type: 'get',
                data: {is_deleted: 1},
                success: function (result) {
                    let data = result.data;
                    let $server_host = $('select[name=server_id]');
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        for (let i = 0; i < data.length; i++) {
                            html.push(sprintf(
                                '<option value="%s">%s(%s)</option>',
                                data[i]['server_id'],
                                data[i]['server_name'],
                                data[i]['server_host']
                            ))
                        }
                        $server_host.append(html.join(''));
                        form.render();
                    });
                }
            });
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(job-save)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.job.add_api,
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