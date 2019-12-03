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
            menu_init('调度总览', '手动执行任务日志');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 任务ID渲染
            this.job_list_id();
            // 表单搜索事件
            this.form_search();
            // 表格数据初始化
            this.table_data_load({});
            // UI组件渲染
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
        // 任务ID渲染
        job_list_id: function () {
            $.ajax({
                url: BASE.uri.job.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        html.push('<option value="0">请选择</option>');
                        for (let i in res.data) {
                            html.push('<option value="' + res.data[i].job_id + '">' + res.data[i].job_name + '</option>')
                        }
                        $('select[name=job_id]').append(html.join(''));
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
                form.on('submit(execute-search)', function (data) {
                    let run_date = data.field.run_date.split(' - ');
                    if (run_date.length === 2) {
                        data.field.start_time = new Date(run_date[0]).getTime() / 1000;
                        data.field.end_time = new Date(run_date[1]).getTime() / 1000;
                    } else {
                        data.field.start_time = 0;
                        data.field.end_time = 0;
                    }
                    delete data.field.run_date;
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
                    elem: "#execute-job",
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50, 100],
                    title: '日志列表',
                    url: BASE.uri.execute.job_api,
                    where: data,
                    cols: [[{
                        type: 'checkbox'
                    }, {
                        field: "exec_id",
                        title: "执行id",
                        width: '5%',
                        sort: true
                    }, {
                        field: "job_name",
                        title: "任务名称",
                        width: '8%',
                        sort: true
                    }, {
                        field: "exec_type",
                        title: "执行类型",
                        width: '5%',
                        templet: function () {
                            return '<span class="layui-badge layui-bg-green">手动</span>';
                        }
                    }, {
                        field: "server_host",
                        title: "服务器ip",
                        width: '8%'
                    }, {
                        field: "server_dir",
                        title: "脚本目录",
                        width: '8%'
                    }, {
                        field: "server_script",
                        title: "脚本命令",
                        width: '8%'
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
                            } else {
                                return '<span class="layui-badge">失败</span>';
                            }
                        }
                    }, {
                        field: "insert_time",
                        title: "开始时间"
                    }, {
                        field: "update_time",
                        title: "结束时间"
                    }, {
                        field: "timedelta",
                        title: "时长",
                        width: '8%'
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            html.push('<a class="layui-btn layui-btn-sm" lay-event="detail">详情日志</a>');
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
                                html.push('<a class="layui-btn layui-btn-sm layui-btn-primary" lay-event="start" style="background-color: #5FB878">启动</a>');
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
                table.on('toolbar(execute-job)', function (obj) {
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
                                                // 关闭自身iframe窗口
                                                setTimeout(function () {
                                                    window.location.reload();
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
                                                    window.location.reload();
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
                                                // 关闭自身iframe窗口
                                                setTimeout(function () {
                                                    window.location.reload();
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
                                            // 关闭自身iframe窗口
                                            setTimeout(function () {
                                                window.location.reload();
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
                table.on('tool(execute-job)', function (obj) {
                        let data = obj.data;
                        let event = obj.event;
                        let tr = obj.tr;
                        // 执行详情
                        if (event === 'detail') {
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '执行详情',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.execute.detail + data.exec_id + '/'
                            });
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
                                            // 关闭自身iframe窗口
                                            setTimeout(function () {
                                                window.location.reload();
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
                                            // 关闭自身iframe窗口
                                            setTimeout(function () {
                                                window.location.reload();
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
                                        // 关闭自身iframe窗口
                                        setTimeout(function () {
                                            window.location.reload();
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
                                        // 关闭自身iframe窗口
                                        setTimeout(function () {
                                            window.location.reload();
                                        }, 2000);
                                    } else {
                                        layer.msg(sprintf('启动失败[%s]', result.msg), {icon: 5});
                                    }
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.alert(sprintf('启动失败: %s', result.msg))
                                }
                            })
                        }
                    }
                )
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
                    type: 'datetime',
                    range: true
                })
            });
        }
    };
    new Controller();
})();