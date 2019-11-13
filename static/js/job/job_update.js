/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 多请求异步渲染
            this.all_ajax_request();
            // 任务表单事件注册
            this.form_event();
        },
        // 多请求异步渲染
        all_ajax_request: function () {
            let that = this;
            $.when(
                // 任务流名称请求
                $.ajax({
                    url: BASE.uri.interface.id_list_api,
                    type: 'get'
                }),
                // 服务器名称请求
                $.ajax({
                    url: BASE.uri.base.exec_host_api,
                    type: 'get',
                    data: {is_deleted: 1}
                }),
                // 任务列表请求
                $.ajax({
                    url: BASE.uri.job.id_list_api,
                    type: 'get'
                }),
                // 参数列表请求
                $.ajax({
                    url: BASE.uri.params.id_list_api,
                    type: 'get'
                }),
                // 任务表单请求
                $.ajax({
                    url: BASE.uri.job.detail_api + window.job_id + '/',
                    type: 'get'
                })
            ).done(
                function (interface_id_list, exec_host_list, job_id_list, param_id_list, job_detail) {
                    that.interface_id_list_init(interface_id_list);
                    that.exec_host_init(exec_host_list);
                    that.job_id_list_init(job_id_list);
                    that.param_id_list_init(param_id_list);
                    that.job_detail_init(job_detail);
                }
            ).fail(function () {
                console.log("任务流请求出错")
            })
        },
        // 任务流名称初始化
        interface_id_list_init: function (result) {
            let data = result[0].data;
            layui.use('form', function () {
                let form = layui.form;
                let html = [];
                for (let i = 0; i < data.length; i++) {
                    html.push(sprintf(
                        '<option value="%s">%s(%s)</option>',
                        data[i].interface_id,
                        data[i].interface_id,
                        data[i].interface_name
                    ))
                }
                $('select[name=interface_id]').append(html.join(''));
                form.render('select');
            });
        },
        // 服务器名称初始化
        exec_host_init: function (result) {
            let data = result[0].data;
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
        },
        // 任务列表初始化
        job_id_list_init: function (result) {
            let data = result[0].data;
            let formSelects = layui.formSelects;
            let html = [];
            for (let i = 0; i < data.length; i++) {
                html.push(sprintf('<option value="%s">%s(%s)</option>',
                    data[i].job_id,
                    data[i].job_id,
                    data[i].job_name
                ))
            }
            $('select[xm-select=job_prep]').append(html.join(''));
            formSelects.render('job_prep');
        },
        // 参数列表初始化
        param_id_list_init: function(result) {
            let data = result[0].data;
            let formSelects = layui.formSelects;
            let html = [];
            for (let i = 0; i < data.length; i++) {
                html.push(sprintf('<option value="%s">%s(%s)</option>',
                    data[i].param_id,
                    data[i].param_id,
                    data[i].param_name
                ))
            }
            $('select[xm-select=job_params]').append(html.join(''));
            formSelects.render('job_params');
        },
        // 任务详情初始化
        job_detail_init: function (result) {
            let data = result[0].data;
            // 任务旧依赖
            window.old_prep = data.prep_id.join(',');
            // 参数旧依赖
            window.old_params = data.param_id.join(',');
            layui.use('form', function () {
                let form = layui.form;
                let formSelects = layui.formSelects;
                form.val('job_detail', {
                    'interface_id': data.interface_id,
                    'job_name': data.job_name,
                    'job_desc': data.job_desc,
                    'job_index': data.job_index,
                    'server_id': data.server_id,
                    'server_dir': data.server_dir,
                    'server_script': data.server_script,
                    'return_code': data.return_code,
                    'is_deleted': data.is_deleted === 1
                });
                formSelects.value('job_prep', data.prep_id);
                formSelects.value('job_params', data.param_id);
                form.render();
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(job-save)', function (data) {
                    data = data.field;
                    // 添加原任务依赖
                    data.old_prep = window.old_prep;
                    // 添加原任务参数
                    data.old_params = window.old_params;
                    $.ajax({
                        url: BASE.uri.job.detail_api + window.job_id + '/',
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
                                layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5});
                            }
                            // 禁止多次提交
                            // $('button[lay-filter=job-save]').attr('class', 'layui-btn layui-btn-disabled');
                            // $('button[lay-filter=job-save]').attr('disabled', 'disabled');
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5});
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