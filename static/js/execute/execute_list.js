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
            menu_init('调度总览', '执行列表');
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
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#execute-list",
                    page: true,
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50, 100],
                    title: '日志列表',
                    url: BASE.uri.execute.list_api,
                    where: data,
                    cols: [[{
                        field: "exec_id",
                        title: "执行id",
                        width: '5%',
                        sort: true
                    }, {
                        field: "interface_id",
                        title: "任务流/任务id",
                        width: '8%'
                    }, {
                        field: "exec_type",
                        title: "执行类型",
                        width: '6%',
                        templet: function (data) {
                            if (data.exec_type === 1) {
                                return '<span class="layui-badge layui-bg-green">调度</span>';
                            } else {
                                return '<span class="layui-badge layui-bg-blue">手动</span>';
                            }
                        }
                    }, {
                        field: "dispatch_name",
                        title: "调度名称",
                        templet: function (data) {
                            if (data.exec_type === 1) {
                                return data.dispatch_name;
                            } else {
                                return '-';
                            }
                        }
                    }, {
                        field: "dispatch_desc",
                        title: "调度描述",
                        templet: function (data) {
                            if (data.exec_type === 1) {
                                return data.dispatch_desc;
                            } else {
                                return '-';
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
                        title: "时长"
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            html.push('<a class="layui-btn layui-btn-sm" lay-event="detail">执行详情</a>');
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
                // 事件监听
                that.table_data_event();
            });
        },
        // 表格事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(execute-list)', function (obj) {
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
                                    url: BASE.uri.execute.detail_api + data.exec_id + '/',
                                    type: 'delete',
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.msg('中止成功', {icon: 6});
                                            // 关闭自身iframe窗口
                                            setTimeout(function () {
                                                window.location.reload();
                                            }, 2000);
                                        } else {
                                            layer.msg(sprintf('中止失败[%s]', result.msg), {icon: 5});
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
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '断点重跑',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.execute.restart + data.exec_id + '/'
                            });
                        }
                        // 重置
                        else if (event === 'reset') {
                            $.ajax({
                                url: BASE.uri.execute.detail_api + data.exec_id + '/',
                                type: 'put',
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.msg('重置成功', {icon: 6});
                                        // 关闭自身iframe窗口
                                        setTimeout(function () {
                                            window.location.reload();
                                        }, 2000);
                                    } else {
                                        layer.msg(sprintf('重置失败[%s]', result.msg), {icon: 5});
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
                                url: BASE.uri.execute.detail_api + data.exec_id + '/',
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