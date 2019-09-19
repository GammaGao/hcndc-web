/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 菜单样式加载
            menu_init('任务总览', '');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 接口名称请求
            this.all_ajax_request();
            // 任务表单事件注册
            this.form_event();
        },
        // 事件注册器
        control: function (controls) {
            let controller = this;
            for (let selector in controls) {
                for (let event in controls[selector]) {
                    $(document).on(event, selector, (function (selector, event) {
                        return function () {
                            let continueBubbling = controls[selector][event].call(controller, this);
                            if (continueBubbling !== true) {
                                return false;
                            }
                        };
                    })(selector, event));
                }
            }
        },
        user_info: function () {
            // 元素渲染
            let element_restart = this.element_init;
            $.ajax({
                url: BASE.uri.user_api,
                type: 'get',
                success: function (result) {
                    if (!result.data.role) {
                        window.location.href = BASE.uri.login;
                    }
                    let html = [];
                    html.push('<a href="#">', result.data.user_name, '</a>');
                    html.push('<dl class="layui-nav-child">');
                    html.push('<dd><a href="#">退出登陆</a></dd></dl>');
                    $('#user-info').html(html.join(''));
                    element_restart();
                }
            });
        },
        tree_toggle: function () {
            let isShow = true;
            $('.kit-side-fold').click(function () {
                $('div.layui-side.layui-bg-black li span').each(function () {
                    if ($(this).is(':hidden')) {
                        $(this).show();
                    } else {
                        $(this).hide();
                    }
                });
                if (isShow) {
                    // 设置宽度
                    $('.layui-side.layui-bg-black').width(60);
                    // 修改图标的位置
                    $('.kit-side-fold button').css('width', '60px');
                    $('.kit-side-fold button i').addClass('layui-icon-spread-left');
                    $('.kit-side-fold button i').removeClass('layui-icon-shrink-right');
                    // footer和body的宽度修改
                    $('.layui-body').css('left', '60px');
                    // 二级导航栏隐藏
                    $('dd span').each(function () {
                        $(this).hide();
                    });
                    isShow = false;
                    layui.use('element', function () {
                        let element = layui.element;
                        element.init();
                    })
                } else {
                    $('.layui-side.layui-bg-black').width(200);
                    $('.kit-side-fold button').css('width', '100%');
                    $('.kit-side-fold button i').removeClass('layui-icon-spread-left');
                    $('.kit-side-fold button i').addClass('layui-icon-shrink-right');
                    $('.layui-body').css('left', '200px');
                    $('dd span').each(function () {
                        $(this).show();
                    });
                    isShow = true;
                }
                // 元素渲染刷新
                layui.use('element', function () {
                    let element = layui.element;
                    element.init();
                })
            });
        },
        element_event: function () {
            this.control({
                '#user-info dl a': {
                    // 用户登出
                    click: this.userLoginOut
                }
            })
        },
        userLoginOut: function () {
            $.ajax({
                url: BASE.uri.login_api,
                type: 'delete',
                success: function () {
                    window.location.href = BASE.uri.login;
                },
                error: function (error) {
                    let result = error.responseJSON;
                    layer.alert(sprintf('退出登陆失败: %s', result.msg))
                }
            })
        },
        // 多请求异步渲染
        all_ajax_request: function () {
            let that = this;
            $.when(
                // 接口名称请求
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
                // 任务表单请求
                $.ajax({
                    url: BASE.uri.job.detail_api + window.job_id + '/',
                    type: 'get'
                })
            ).done(
                function (interface_id_list, exec_host_list, job_id_list, job_detail) {
                    that.interface_id_list_init(interface_id_list);
                    that.exec_host_init(exec_host_list);
                    that.job_id_list_init(job_id_list);
                    that.job_detail_init(job_detail);
                }
            ).fail(function () {
                console.log("接口请求出错")
            })
        },
        // 接口名称初始化
        interface_id_list_init: function (result) {
            let data = result[0].data;
            layui.use('form', function () {
                let form = layui.form;
                let html = [];
                for (let i in data) {
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
                for (let i in data) {
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
            for (let i in data) {
                html.push(sprintf('<option value="%s">%s(%s)</option>',
                    data[i].job_id,
                    data[i].job_id,
                    data[i].job_name
                ))
            }
            $('select[xm-select=job_prep]').append(html.join(''));
            formSelects.render('job_prep');
        },
        // 任务详情初始化
        job_detail_init: function (result) {
            let data = result[0].data;
            // 旧依赖
            window.old_prep = data.prep_id.join(',');
            layui.use('form', function () {
                let form = layui.form;
                let formSelects = layui.formSelects;
                form.val('job_detail', {
                    'job_name': data.job_name,
                    'job_desc': data.job_desc,
                    'server_id': data.server_id,
                    'server_dir': data.server_dir,
                    'server_script': data.server_script,
                    'is_deleted': data.is_deleted === 1
                });
                formSelects.value('job_prep', data.prep_id);
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
                    $.ajax({
                        url: BASE.uri.job.detail_api + window.job_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            layer.open({
                                id: 'job_update_success',
                                btn: ['返回列表', '留在本页'],
                                title: '修改任务成功',
                                content: sprintf('任务id: %s, 状态: %s', result.data.id, result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.job.list;
                                }
                            });
                            // 禁止多次提交
                            $('button[lay-filter=job-save]').attr('class', 'layui-btn layui-btn-disabled');
                            $('button[lay-filter=job-save]').attr('disabled', 'disabled');
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'job_update_error',
                                title: '修改任务失败',
                                content: sprintf('任务id: %s, 状态: %s', data.job_id, result.msg)
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