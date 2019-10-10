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
            menu_init('任务总览', '接口列表');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 接口查询事件注册
            this.form_event();
            // 表格数据初始化
            this.table_data_load({});
            // UI组件渲染
            this.restart('interface_date');
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
        form_event: function () {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(interface-search)', function (data) {
                    let interface_date_list = data.field.interface_date.split(' - ');
                    if (interface_date_list.length === 2) {
                        let start_time = interface_date_list[0] + ' 00:00:00';
                        data.field.start_time = new Date(start_time).getTime() / 1000;
                        let end_time = interface_date_list[1] + ' 23:59:59';
                        data.field.end_time = new Date(end_time).getTime() / 1000;
                    } else {
                        data.field.start_time = 0;
                        data.field.end_time = 0;
                    }
                    delete data.field.interface_date;
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
                '<div class="layui-inline" lay-event="add" title="添加接口"><i class="layui-icon layui-icon-add-1"></i></div>',
                '<div class="layui-inline" lay-event="update" title="修改接口"><i class="layui-icon layui-icon-edit"></i></div>',
                '</div>'
            ].join('');
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#interface-list",
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50],
                    title: '任务列表',
                    url: BASE.uri.interface.list_api,
                    where: data,
                    cols: [[{
                        type: 'radio',
                        fixed: 'left'
                    }, {
                        field: "interface_id",
                        title: "接口id",
                        sort: true
                    }, {
                        field: "interface_name",
                        title: "接口名称"
                    }, {
                        field: "interface_desc",
                        title: "接口描述"
                    }, {
                        field: "retry",
                        title: "重试次数"
                    }, {
                        field: "is_deleted",
                        title: "是否失效",
                        sort: true,
                        templet: function (data) {
                            if (data.is_deleted === 0) {
                                return '<span class="layui-badge layui-bg-green">正常</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-gray">删除</span>';
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            html.push('<a class="layui-btn layui-btn-sm" lay-event="detail">任务依赖</a>');
                            html.push('<a class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</a>');
                            if (data.is_deleted === 0) {
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                            } else {
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" lay-event="delete" disabled="disabled">删除</button>');
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
            layui.use('table', function () {
                let table = layui.table;
                table.on('toolbar(interface-list)', function (obj) {
                    // 工具栏事件监听
                    let check_status = table.checkStatus(obj.config.id);
                    let check_data = check_status.data;
                    switch (obj.event) {
                        case 'add':
                            layer.open({
                                id: 'interface_add',
                                btn: ['跳转', '取消'],
                                title: '跳转新增接口页面',
                                content: '确定新增接口?',
                                yes: function (index, layero) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.interface.add;
                                }
                            });
                            break;
                        case 'update':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行')
                            } else if (check_data.length > 1) {
                                layer.msg('只能同时编辑一个')
                            } else {
                                window.location.href = BASE.uri.interface.update + check_data[0].interface_id + '/';
                            }
                            break;
                    }
                })
            })
        },
        // 自定义事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(interface-list)', function (obj) {
                    // 自定义事件监控
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    if (event === 'detail') {
                        window.location.href = BASE.uri.interface.detail + data.interface_id + '/';
                    } else if (event === 'update') {
                        window.location.href = BASE.uri.interface.update + data.interface_id + '/';
                    } else if (event === 'delete') {
                        if (data.is_deleted !== 0) {
                            layer.alert('项目已失效');
                            return
                        }
                        layer.confirm('确定删除?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.interface.detail_api + data.interface_id + '/',
                                type: 'delete',
                                success: function () {
                                    layer.alert('删除成功');
                                    $(tr.find('td[data-field="operation"] div button')).addClass('layui-btn-disabled');
                                    tr.find('td[data-field="is_deleted"] div').html('<span class="layui-badge layui-bg-gray">删除</span>');
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.alert(sprintf('删除接口%s失败: %s', data.interface_id, result.msg))
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