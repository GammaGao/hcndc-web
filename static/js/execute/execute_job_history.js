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
            menu_init('调度总览', '任务监控');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
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
            // 请求参数赋值
            data.job_id = window.job_id;
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#execute-job-history",
                    page: true,
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50, 100],
                    title: '执行历史日志列表',
                    url: BASE.uri.execute.job_history_api,
                    where: data,
                    cols: [[{
                        field: "exec_id",
                        title: "执行id",
                        width: '5%',
                        sort: true
                    }, {
                        field: "job_name",
                        title: "任务名称",
                        width: '8%',
                    }, {
                        field: "job_index",
                        title: "任务目录",
                        width: '8%',
                    }, {
                        field: "exec_type",
                        title: "执行类型",
                        width: '5%',
                        templet: function (data) {
                            if (data.exec_type === 1) {
                                return '<span class="layui-badge layui-bg-green">自动</span>';
                            } else if (data.exec_type === 2) {
                                return '<span class="layui-badge layui-bg-blue">手动</span>';
                            } else {
                                return '-'
                            }
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
                            if (data.status === 'ready') {
                                return '<span class="layui-badge layui-bg-orange">等待依赖任务完成</span>';
                            } else if (data.status === 'preparing') {
                                return '<span class="layui-badge layui-bg-orange">待运行</span>';
                            } else if (data.status === 'running') {
                                return '<span class="layui-badge layui-bg-blue">运行中</span>';
                            } else if (data.status === 'succeeded') {
                                return '<span class="layui-badge layui-bg-green">成功</span>';
                            } else if (data.status === 'failed') {
                                return '<span class="layui-badge">失败</span>';
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
                        width: '8%',
                        templet: function (data) {
                            if (data.timedelta) {
                                return data.timedelta
                            } else {
                                return '-'
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            if (data.exec_id) {
                                let html = [];
                                html.push('<div class="layui-btn-group">');
                                html.push('<a class="layui-btn layui-btn-sm" lay-event="detail">详情日志</a>');
                                html.push('</div>');
                                return html.join('');
                            } else {
                                return ''
                            }
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
                table.on('tool(execute-job-history)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    // 执行详情
                    if (event === 'detail') {
                        layer.open({
                            type: 2,
                            anim: 5,
                            title: '任务日志',
                            maxmin: true,
                            area: ['60%', '80%'],
                            content: BASE.uri.execute.log + data.exec_id + '/' + window.job_id + '/' + 0 + '/'
                        });
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
                    type: 'datetime',
                    range: true
                })
            });
        }
    };
    new Controller();
})();