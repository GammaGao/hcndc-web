/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 菜单样式加载
            menu_init('调度总览', '调度列表');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 任务流ID渲染
            this.interface_list_id();
            // 表单搜索事件
            this.form_search();
            // 表格数据初始化
            this.table_data_load({});
            // UI组件渲染
            // this.restart('job_date');
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
        // 任务流ID渲染
        interface_list_id: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        html.push('<option value="0">请选择</option>');
                        for (let i in res.data) {
                            html.push('<option value="' + res.data[i].interface_id + '">' + res.data[i].interface_name + '</option>')
                        }
                        $('select[name=interface_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 表单搜索
        form_search: function () {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(dispatch-search)', function (data) {
                    that.table_data_load(data.field);
                });
            });
        },
        // 表格组件渲染
        table_data_load: function (data) {
            // 事件监听
            let that = this;
            // 自定义左侧工具栏
            let toolbar_div = [
                '<div class="layui-table-tool-temp">',
                '<div class="layui-inline" lay-event="add" title="添加调度"><i class="layui-icon layui-icon-add-1"></i></div>',
                '<div class="layui-inline" lay-event="update" title="修改调度"><i class="layui-icon layui-icon-edit"></i></div>',
                '<div class="layui-inline" lay-event="run" title="立即执行"><i class="layui-icon layui-icon-play"></i></div>',
                '<div class="layui-inline" lay-event="pause" title="暂停"><i class="layui-icon layui-icon-pause"></i></div>',
                '<div class="layui-inline" lay-event="resume" title="恢复"><i class="layui-icon layui-icon-refresh"></i></div>',
                '<div class="layui-inline" lay-event="delete" title="删除"><i class="layui-icon layui-icon-delete"></i></div>',
                '</div>'
            ].join('');
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#dispatch-list",
                    // height: 40,
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50],
                    title: '调度列表',
                    url: BASE.uri.dispatch.list_api,
                    where: data,
                    cols: [[{
                        type: 'checkbox'
                    }, {
                        field: "dispatch_id",
                        title: "调度id",
                        width: '5%',
                        sort: true
                    }, {
                        field: "interface_id",
                        title: "任务流id",
                        width: '5%'
                    }, {
                        field: "dispatch_name",
                        title: "调度名称"
                    }, {
                        field: "dispatch_desc",
                        title: "调度描述"
                    }, {
                        field: "next_run_time",
                        title: "下次运行时间"
                    }, {
                        field: "status",
                        title: "运行状态",
                        width: '6%',
                        templet: function (data) {
                            if (data.status === 0) {
                                return '<span class="layui-badge layui-bg-gray">删除</span>'
                            } else if (data.status === 1) {
                                return '<span class="layui-badge layui-bg-green">运行中</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-orange">暂停</span>'
                            }
                        }
                    }, {
                        field: "cron_expr",
                        title: "cron表达式",
                        width: '8%'
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            // 已删除
                            if (data.status === 0) {
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">立即执行</button>');
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">暂停</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">删除</button>');
                            }
                            // 运行中
                            else if (data.status === 1) {
                                html.push('<button class="layui-btn layui-btn-sm" lay-event="run">立即执行</button>');
                                html.push('<button class="layui-btn PREPARING layui-btn-sm" lay-event="pause">暂停</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                            }
                            // 暂停中
                            else if (data.status === 2) {
                                html.push('<button class="layui-btn layui-btn-sm" lay-event="run">立即执行</button>');
                                html.push('<button class="layui-btn layui-btn-normal layui-btn-sm" lay-event="resume">恢复</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                            }
                            html.push('</div>');
                            return html.join('');
                        }
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200,
                        countName: 'total'
                    }
                });
                // 工具栏事件监听
                that.toolbar_data_event();
                // 自定义事件监听
                that.table_data_event();
            });
        },
        // 工具栏事件监听
        toolbar_data_event: function () {
            // 工具栏事件注册
            layui.use('table', function () {
                let table = layui.table;
                table.on('toolbar(dispatch-list)', function (obj) {
                    // 工具栏事件监听
                    let check_status = table.checkStatus(obj.config.id);
                    let check_data = check_status.data;
                    switch (obj.event) {
                        // 新增
                        case 'add':
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '新增调度',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.dispatch.add,
                                end: function () {
                                    window.location.reload();
                                }
                            });
                            break;
                        // 修改
                        case 'update':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行', {icon: 5});
                            } else if (check_data.length > 1) {
                                layer.msg('只能同时编辑一个', {icon: 5})
                            } else {
                                layer.open({
                                    type: 2,
                                    anim: 5,
                                    title: '修改调度',
                                    maxmin: true,
                                    area: ['60%', '80%'],
                                    content: BASE.uri.dispatch.update + check_data[0].dispatch_id + '/',
                                    end: function () {
                                        window.location.reload();
                                    }
                                });
                            }
                            break;
                        // 立即执行
                        case 'run':
                            let delete_status = check_data.filter(item => item.status === 0);
                            if (delete_status.length > 0) {
                                layer.msg('存在已删除调度, 不能执行', {icon: 5});
                                break
                            } else {
                                let dispatch_id_arr = [];
                                check_data.forEach(item => dispatch_id_arr.push(item.dispatch_id));
                                layer.open({
                                    type: 2,
                                    anim: 5,
                                    title: '立即执行',
                                    maxmin: true,
                                    area: ['60%', '80%'],
                                    content: BASE.uri.dispatch.run + '?dispatch_id=' + dispatch_id_arr.join(',')
                                });
                            }
                            break;
                        // 暂停
                        case 'pause':
                            let pause_status = check_data.filter(item => item.status !== 1);
                            if (pause_status.length > 0) {
                                layer.msg('存在已删除或暂停中调度, 不能执行', {icon: 5});
                                break
                            } else {
                                let dispatch_id_arr = [];
                                check_data.forEach(item => dispatch_id_arr.push(item.dispatch_id));
                                $.ajax({
                                    url: BASE.uri.dispatch.action_api,
                                    contentType: "application/json; charset=utf-8",
                                    type: 'patch',
                                    data: JSON.stringify({dispatch_id: dispatch_id_arr, 'action': 1}),
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.open({
                                                id: 'dispatch_pause_succeed',
                                                title: '暂停调度成功',
                                                content: '暂停调度成功',
                                                yes: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                },
                                                cancel: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                }
                                            });
                                        } else {
                                            layer.alert(sprintf('暂停调度失败: [%s]', result.msg), {icon: 5});
                                        }
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.msg(sprintf('暂停调度失败[%s]', result.msg), {icon: 5});
                                    }
                                });
                            }
                            break;
                        // 恢复
                        case 'resume':
                            let resume_status = check_data.filter(item => item.status !== 2);
                            if (resume_status.length > 0) {
                                layer.msg('存在已删除或运行中调度, 不能执行', {icon: 5});
                                break
                            } else {
                                let dispatch_id_arr = [];
                                check_data.forEach(item => dispatch_id_arr.push(item.dispatch_id));
                                $.ajax({
                                    url: BASE.uri.dispatch.action_api,
                                    contentType: "application/json; charset=utf-8",
                                    type: 'patch',
                                    data: JSON.stringify({dispatch_id: dispatch_id_arr, 'action': 2}),
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.open({
                                                id: 'dispatch_resume_succeed',
                                                title: '恢复调度成功',
                                                content: '恢复调度成功',
                                                yes: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                },
                                                cancel: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                }
                                            });
                                        } else {
                                            layer.alert(sprintf('恢复调度失败: [%s]', result.msg), {icon: 5});
                                        }
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.msg(sprintf('恢复调度失败[%s]', result.msg), {icon: 5});
                                    }
                                });
                            }
                            break;
                        // 删除
                        case 'delete':
                            let deleted_status = check_data.filter(item => item.status === 0);
                            if (deleted_status.length > 0) {
                                layer.msg('存在已删除调度, 不能执行', {icon: 5});
                                break
                            } else {
                                let dispatch_id_arr = [];
                                check_data.forEach(item => dispatch_id_arr.push(item.dispatch_id));
                                layer.confirm('确定删除?', function (index) {
                                    // 关闭弹窗
                                    layer.close(index);
                                    $.ajax({
                                        url: BASE.uri.dispatch.action_api,
                                        data: JSON.stringify({dispatch_id: dispatch_id_arr}),
                                        contentType: "application/json; charset=utf-8",
                                        type: 'delete',
                                        success: function (result) {
                                            if (result.status === 200) {
                                                layer.open({
                                                    id: 'dispatch_delete_succeed',
                                                    title: '删除调度成功',
                                                    content: '删除调度成功',
                                                    yes: function () {
                                                        // 刷新页面
                                                        window.location.reload();
                                                    },
                                                    cancel: function () {
                                                        // 刷新页面
                                                        window.location.reload();
                                                    }
                                                });
                                            } else {
                                                layer.alert(sprintf('删除项目: [%s]', result.msg), {icon: 5});
                                            }
                                        },
                                        error: function (error) {
                                            let result = error.responseJSON;
                                            layer.alert(sprintf('删除项目失败: %s', result.msg))
                                        }
                                    });
                                });
                            }
                            break;
                    }
                })
            })
        },
        // 表格事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(dispatch-list)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    switch (event) {
                        // 立即执行
                        case 'run':
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '立即执行',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.dispatch.run + '?dispatch_id=' + data.dispatch_id
                            });
                            break;
                        // 暂停
                        case 'pause':
                            $.ajax({
                                url: BASE.uri.dispatch.action_api,
                                contentType: "application/json; charset=utf-8",
                                type: 'patch',
                                data: JSON.stringify({dispatch_id: [data.dispatch_id], 'action': 1}),
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.open({
                                            id: 'dispatch_pause_succeed',
                                            title: '暂停调度成功',
                                            content: '暂停调度id: ' + data.dispatch_id + '成功',
                                            yes: function () {
                                                // 刷新页面
                                                window.location.reload();
                                            },
                                            cancel: function () {
                                                // 刷新页面
                                                window.location.reload();
                                            }
                                        });
                                    } else {
                                        layer.alert(sprintf('暂停调度失败: [%s]', result.msg), {icon: 5});
                                    }
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.msg(sprintf('暂停调度失败[%s]', result.msg), {icon: 5});
                                }
                            });
                            break;
                        // 恢复
                        case 'resume':
                            $.ajax({
                                url: BASE.uri.dispatch.action_api,
                                contentType: "application/json; charset=utf-8",
                                type: 'patch',
                                data: JSON.stringify({dispatch_id: [data.dispatch_id], 'action': 2}),
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.open({
                                            id: 'dispatch_resume_succeed',
                                            title: '恢复调度成功',
                                            content: '恢复调度id: ' + data.dispatch_id + '成功',
                                            yes: function () {
                                                // 刷新页面
                                                window.location.reload();
                                            },
                                            cancel: function () {
                                                // 刷新页面
                                                window.location.reload();
                                            }
                                        });
                                    } else {
                                        layer.alert(sprintf('恢复调度失败: [%s]', result.msg), {icon: 5});
                                    }
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.msg(sprintf('恢复调度失败[%s]', result.msg), {icon: 5});
                                }
                            });
                            break;
                        // 修改
                        case 'update':
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '修改调度',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.dispatch.update + data.dispatch_id + '/',
                                end: function () {
                                    window.location.reload();
                                }
                            });
                            break;
                        // 删除
                        case 'delete':
                            layer.confirm('确定删除?', function (index) {
                                // 关闭弹窗
                                layer.close(index);
                                $.ajax({
                                    url: BASE.uri.dispatch.action_api,
                                    data: JSON.stringify({dispatch_id: [data.dispatch_id]}),
                                    contentType: "application/json; charset=utf-8",
                                    type: 'delete',
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.open({
                                                id: 'dispatch_delete_succeed',
                                                title: '删除调度成功',
                                                content: '删除调度id: ' + data.dispatch_id + '成功',
                                                yes: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                },
                                                cancel: function () {
                                                    // 刷新页面
                                                    window.location.reload();
                                                }
                                            });
                                        } else {
                                            layer.alert(sprintf('删除项目: [%s]', result.msg), {icon: 5});
                                        }

                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.alert(sprintf('删除项目%s失败: %s', data.job_id, result.msg))
                                    }
                                });
                            });
                            break;
                    }
                })
            })
        },
        element_init: function () {
            // 元素渲染刷新
            layui.use('element', function () {
                let element = layui.element;
                element.init();
            });
        },
        restart: function (field) {
            // 日期组件渲染
            let today = new Date().Format("yyyy-MM-dd");
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    max: today,
                    theme: '#393D49',
                    calendar: true,
                    range: true
                })
            });
        }
    };
    new Controller();
})();