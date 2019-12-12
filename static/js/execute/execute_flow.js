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
            menu_init('调度总览', '任务流监控');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 任务流ID渲染
            this.interface_list_id();
            // 任务流目录数据初始化
            this.interface_index_init();
            // 表单搜索事件
            this.form_search();
            // 表格数据初始化
            this.table_data_load({});
            // 日期组件渲染
            this.restart('run_date');
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
                        html.push('<option value="0"></option>');
                        for (let i in res.data) {
                            html.push('<option value="' + res.data[i].interface_id + '">' + res.data[i].interface_name + '</option>')
                        }
                        $('select[name=interface_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 任务流目录数据初始化
        interface_index_init: function () {
            $.ajax({
                url: BASE.uri.interface.index_api,
                type: 'get',
                success: function (result) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    html.push('<option value="">全部</option>');
                    for (let i = 0; i < result.data.length; i++) {
                        let item = result.data[i];
                        html.push('<option value="' + item.interface_index + '">' + item.interface_index + '</option>')
                    }
                    $('select[xm-select=interface_index]').append(html.join(''));
                    formSelects.render('interface_index');
                }
            });
        },
        // 表单搜索
        form_search: function () {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(execute-search)', function (data) {
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
                '<div class="layui-inline" lay-event="stop" title="中止"><i class="layui-icon layui-icon-pause"></i></div>',
                '<div class="layui-inline" lay-event="restart" title="断点重跑"><i class="layui-icon layui-icon-next"></i></div>',
                '<div class="layui-inline" lay-event="start" title="启动"><i class="layui-icon layui-icon-play"></i></div>',
                '<div class="layui-inline" lay-event="reset" title="重置"><i class="layui-icon layui-icon-refresh"></i></div>',
                '</div>'
            ].join('');
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#execute-flow",
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50, 100],
                    title: '日志列表',
                    url: BASE.uri.execute.flow_api,
                    where: data,
                    cols: [[{
                        type: 'checkbox'
                    }, {
                        field: "interface_id",
                        title: "任务流id",
                        width: '6%',
                        sort: true
                    }, {
                        field: "interface_name",
                        title: "任务流名称",
                        width: '8%',
                        sort: true
                    }, {
                        field: "interface_index",
                        title: "任务流目录"
                    }, {
                        field: "dispatch_id",
                        title: "是否调度",
                        width: '6%',
                        templet: function (data) {
                            if (data.dispatch_id) {
                                return '<span class="layui-badge layui-bg-green">是</span>';
                            } else {
                                return '<span class="layui-badge">否</span>';
                            }
                        }
                    }, {
                        field: "run_time",
                        title: "数据日期",
                        width: '6%',
                        templet: function (data) {
                            if (data.run_time) {
                                return data.run_time
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "insert_time",
                        title: "开始时间",
                        templet: function (data) {
                            if (data.insert_time) {
                                return data.insert_time
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "update_time",
                        title: "结束时间",
                        templet: function (data) {
                            if (data.update_time) {
                                return data.update_time
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "timedelta",
                        title: "时长",
                        templet: function (data) {
                            if (data.timedelta) {
                                return data.timedelta
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "status",
                        title: "运行状态",
                        width: '6%',
                        templet: function (data) {
                            if (data.status === 0) {
                                return '<span class="layui-badge layui-bg-green">成功</span>';
                            } else if (data.status === 1) {
                                return '<span class="layui-badge layui-bg-blue">运行中</span>';
                            } else if (data.status === 2) {
                                return '<span class="layui-badge layui-bg-orange">中断</span>';
                            } else if (data.status === 3) {
                                return '<span class="layui-badge-rim">就绪</span>';
                            } else if (data.status === -1) {
                                return '<span class="layui-badge">失败</span>';
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            if (data.dispatch_id) {
                                html.push('<a class="layui-btn layui-btn-sm" lay-event="history">历史日志</a>');
                            }
                            // 运行中
                            if (data.status === 1) {
                                html.push('<a class="layui-btn layui-btn-sm layui-btn-warm" lay-event="stop">中止</a>');
                            }
                            // 失败或中断
                            else if (data.status === 2 || data.status === -1) {
                                html.push('<a class="layui-btn layui-btn-sm layui-btn-normal" lay-event="restart">断点重跑</a>');
                                html.push('<a class="layui-btn layui-btn-sm layui-btn-primary" lay-event="reset">重置</a>');
                            }
                            // 就绪
                            else if (data.status === 3) {
                                html.push('<a class="layui-btn layui-btn-sm SUCCEEDED" lay-event="start">启动</a>');
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
                // 事件监听
                that.table_data_event();
            });
        },
        // 工具栏事件监听
        toolbar_data_event: function () {
            // 工具栏事件注册
            layui.use('table', function () {
                let table = layui.table;
                table.on('toolbar(execute-flow)', function (obj) {
                    // 工具栏事件监听
                    let check_status = table.checkStatus(obj.config.id);
                    let check_data = check_status.data;
                    switch (obj.event) {
                        // 中止
                        case 'stop':
                            let stop_status = check_data.filter(item => item.status !== 1);
                            if (stop_status.length > 0) {
                                layer.msg('存在非[运行中]执行任务, 不能执行', {icon: 5, shift: 6});
                                break
                            } else {
                                let execute_arr = [];
                                check_data.forEach(item => execute_arr.push(item.exec_id));
                                layer.confirm('确定中止?', function (index) {
                                    // 关闭弹窗
                                    layer.close(index);
                                    $.ajax({
                                        url: BASE.uri.execute.action_api,
                                        contentType: "application/json; charset=utf-8",
                                        data: JSON.stringify({exec_id: execute_arr}),
                                        type: 'delete',
                                        success: function (result) {
                                            if (result.status === 200) {
                                                layer.msg('中止成功', {icon: 6});
                                                // 刷新页面
                                                setTimeout(function () {
                                                    $(".layui-laypage-btn").click();
                                                }, 2000);
                                            } else {
                                                layer.msg(sprintf('中止失败[%s]', result.msg), {icon: 5, shift: 6});
                                            }
                                        },
                                        error: function (error) {
                                            let result = error.responseJSON;
                                            layer.alert(sprintf('中止失败: %s', result.msg))
                                        }
                                    })
                                })
                            }
                            break;
                        // 断点重跑
                        case 'restart':
                            let restart_status = check_data.filter(item => item.status !== 2 && item.status !== -1);
                            if (restart_status.length > 0) {
                                layer.msg('存在非[失败]或[中断]执行任务, 不能执行', {icon: 5, shift: 6});
                                break
                            } else {
                                let execute_arr = [];
                                check_data.forEach(item => execute_arr.push(item.exec_id));
                                layer.confirm('确定断点重跑?', function (index) {
                                    // 关闭弹窗
                                    layer.close(index);
                                    $.ajax({
                                        url: BASE.uri.execute.action_api,
                                        contentType: "application/json; charset=utf-8",
                                        data: JSON.stringify({exec_id: execute_arr, prepose_rely: 0}),
                                        type: 'post',
                                        success: function (result) {
                                            if (result.status === 200) {
                                                layer.msg('重跑成功', {icon: 6});
                                                // 关闭自身iframe窗口
                                                setTimeout(function () {
                                                    $(".layui-laypage-btn").click();
                                                }, 2000);
                                            } else {
                                                layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5, shift: 6});
                                            }
                                        },
                                        error: function (error) {
                                            let result = error.responseJSON;
                                            layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5, shift: 6});
                                        }
                                    });
                                })
                            }
                            break;
                        // 重置
                        case 'reset':
                            let reset_status = check_data.filter(item => item.status !== 2 && item.status !== -1);
                            if (reset_status.length > 0) {
                                layer.msg('存在非[失败]或[中断]执行任务, 不能执行', {icon: 5, shift: 6});
                                break
                            } else {
                                let execute_arr = [];
                                check_data.forEach(item => execute_arr.push(item.exec_id));
                                layer.confirm('确定重置?', function (index) {
                                    // 关闭弹窗
                                    layer.close(index);
                                    $.ajax({
                                        url: BASE.uri.execute.action_api,
                                        contentType: "application/json; charset=utf-8",
                                        data: JSON.stringify({exec_id: execute_arr}),
                                        type: 'put',
                                        success: function (result) {
                                            if (result.status === 200) {
                                                layer.msg('重置成功', {icon: 6});
                                                // 刷新页面
                                                setTimeout(function () {
                                                    $(".layui-laypage-btn").click();
                                                }, 2000);
                                            } else {
                                                layer.msg(sprintf('重置失败[%s]', result.msg), {icon: 5, shift: 6});
                                            }
                                        },
                                        error: function (error) {
                                            let result = error.responseJSON;
                                            layer.alert(sprintf('重置失败: %s', result.msg))
                                        }
                                    });
                                })
                            }
                            break;
                        // 启动
                        case 'start':
                            let start_status = check_data.filter(item => item.status !== 3);
                            if (start_status.length > 0) {
                                layer.msg('存在非[就绪]执行任务, 不能执行', {icon: 5, shift: 6});
                                break
                            } else {
                                let execute_arr = [];
                                check_data.forEach(item => execute_arr.push(item.exec_id));
                                $.ajax({
                                    url: BASE.uri.execute.action_api,
                                    contentType: "application/json; charset=utf-8",
                                    type: 'patch',
                                    data: JSON.stringify({exec_id: execute_arr}),
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.msg('启动成功', {icon: 6});
                                            // 刷新页面
                                            setTimeout(function () {
                                                $(".layui-laypage-btn").click();
                                            }, 2000);
                                        } else {
                                            layer.msg(sprintf('启动失败[%s]', result.msg), {icon: 5, shift: 6});
                                        }
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.alert(sprintf('启动失败: %s', result.msg))
                                    }
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
                table.on('tool(execute-flow)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    console.log(data);
                    // 历史日志
                    if (event === 'history') {
                        if (data.dispatch_id) {
                            window.location.href = BASE.uri.execute.history + data.dispatch_id + '/';
                        } else {
                            layer.msg('历史日志不存在', {icon: 5, shift: 6});
                        }
                    }
                    // 中止
                    else if (event === 'stop') {
                        layer.confirm('确定中止?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.execute.action_api,
                                contentType: "application/json; charset=utf-8",
                                data: JSON.stringify({exec_id: [data.exec_id]}),
                                type: 'delete',
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.msg('中止成功', {icon: 6});
                                        // 刷新页面
                                        setTimeout(function () {
                                            $(".layui-laypage-btn").click();
                                        }, 2000);
                                    } else {
                                        layer.msg(sprintf('中止失败[%s]', result.msg), {icon: 5, shift: 6});
                                    }
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.alert(sprintf('中止失败: %s', result.msg))
                                }
                            })
                        })
                    }
                    // 断点重跑
                    else if (event === 'restart') {
                        // layer.open({
                        //     type: 2,
                        //     anim: 5,
                        //     title: '断点重跑',
                        //     maxmin: true,
                        //     area: ['60%', '80%'],
                        //     content: BASE.uri.execute.restart + data.exec_id + '/'
                        // });
                        layer.confirm('确定断点重跑?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.execute.action_api,
                                contentType: "application/json; charset=utf-8",
                                data: JSON.stringify({exec_id: [data.exec_id]}),
                                type: 'post',
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.msg('重跑成功', {icon: 6});
                                        // 刷新页面
                                        setTimeout(function () {
                                            $(".layui-laypage-btn").click();
                                        }, 2000);
                                    } else {
                                        layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5, shift: 6});
                                    }
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5, shift: 6});
                                }
                            });
                        })
                    }
                    // 重置
                    else if (event === 'reset') {
                        $.ajax({
                            url: BASE.uri.execute.action_api,
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify({exec_id: [data.exec_id]}),
                            type: 'put',
                            success: function (result) {
                                if (result.status === 200) {
                                    layer.msg('重置成功', {icon: 6});
                                    // 刷新页面
                                    setTimeout(function () {
                                        $(".layui-laypage-btn").click();
                                    }, 2000);
                                } else {
                                    layer.msg(sprintf('重置失败[%s]', result.msg), {icon: 5, shift: 6});
                                }
                            },
                            error: function (error) {
                                let result = error.responseJSON;
                                layer.alert(sprintf('重置失败: %s', result.msg))
                            }
                        })
                    }
                    // 启动
                    else if (event === 'start') {
                        $.ajax({
                            url: BASE.uri.execute.action_api,
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify({exec_id: [data.exec_id]}),
                            type: 'patch',
                            success: function (result) {
                                if (result.status === 200) {
                                    layer.msg('启动成功', {icon: 6});
                                    // 刷新页面
                                    setTimeout(function () {
                                        $(".layui-laypage-btn").click();
                                    }, 2000);
                                } else {
                                    layer.msg(sprintf('启动失败[%s]', result.msg), {icon: 5, shift: 6});
                                }
                            },
                            error: function (error) {
                                let result = error.responseJSON;
                                layer.alert(sprintf('启动失败: %s', result.msg))
                            }
                        })
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
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    type: 'date',
                    // range: true
                })
            });
        }
    };
    new Controller();
})();