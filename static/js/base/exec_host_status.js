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
            menu_init('基础配置', '执行服务器状态');
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
        // 表单搜索
        form_search: function () {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(host-search)', function (data) {
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
                    elem: "#host-status",
                    page: true,
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50],
                    title: '执行服务器状态列表',
                    url: BASE.uri.base.exec_host_status_api,
                    where: data,
                    cols: [[{
                        field: "server_id",
                        title: "服务器id",
                        width: '6%',
                        sort: true
                    }, {
                        field: "server_host",
                        title: "服务器IP"
                    }, {
                        field: "server_name",
                        title: "服务器名称"
                    }, {
                        field: "core_num",
                        title: "内核数",
                        width: '5%',
                        templet: function (data) {
                            if (data.core_num === null) {
                                return '-'
                            } else {
                                return data.core_num
                            }
                        }
                    }, {
                        field: "system_version",
                        title: "系统版本",
                        templet: function (data) {
                            if (data.system_version === null) {
                                return '-'
                            } else {
                                return data.system_version
                            }
                        }
                    }, {
                        field: "disk_all",
                        title: "磁盘总量",
                        templet: function (data) {
                            if (data.disk_all === null) {
                                return '-'
                            } else {
                                return data.disk_all
                            }
                        }
                    }, {
                        field: "disk_used",
                        title: "已使用磁盘",
                        templet: function (data) {
                            if (data.disk_used === null) {
                                return '-'
                            } else {
                                return data.disk_used
                            }
                        }
                    }, {
                        field: "memory_all",
                        title: "内存总量",
                        templet: function (data) {
                            if (data.memory_all === null) {
                                return '-'
                            } else {
                                return data.memory_all
                            }
                        }
                    }, {
                        field: "memory_used",
                        title: "已使用内存",
                        templet: function (data) {
                            if (data.memory_used === null) {
                                return '-'
                            } else {
                                return data.memory_used
                            }
                        }
                    }, {
                        field: "last_ping_time",
                        title: "上一次检测时间",
                        templet: function (data) {
                            if (data.last_ping_time === null) {
                                return '-'
                            } else {
                                return data.last_ping_time
                            }
                        }
                    }, {
                        field: "process_status",
                        title: "进程状态",
                        width: '6%',
                        templet: function (data) {
                            if (data.process_status === null) {
                                return '-'
                            } else if (data.process_status === 0) {
                                return '<span class="layui-badge layui-bg-green">正常</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-red">异常</span>';
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        width: '5%',
                        templet: function () {
                            return '<a class="layui-btn layui-btn-normal layui-btn-sm" lay-event="test">检测</a>';
                        }
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200,
                        countName: 'total'
                    }
                });
                // 事件监听
                that.table_data_event(data);
            });

        },
        // 表格事件监听
        table_data_event: function (form_data) {
            let that = this;
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(host-status)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    if (event === 'test') {
                        layer.confirm('确定检测执行服务器状态?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.base.exec_host_test_api,
                                contentType: "application/json; charset=utf-8",
                                type: 'post',
                                data: JSON.stringify({'server_host': data.server_host}),
                                success: function (result) {
                                    let msg = [
                                        '连接成功</br>',
                                        '系统: ', result.data.system, '</br>',
                                        'CPU内核数: ', result.data.cpu, '</br>',
                                        '硬盘总量: ', result.data.disk.total, ', 使用量: ', result.data.disk.used, '</br>',
                                        '内存总量', result.data.memory.total, ', 使用量: ', result.data.memory.used, '</br>',
                                    ];
                                    layer.alert(msg.join(''), {icon: 6});
                                    // 刷新页面
                                    that.table_data_load(form_data);
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.msg(sprintf('连接服务器失败: [%s]', result.msg), {icon: 2});
                                }
                            });

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