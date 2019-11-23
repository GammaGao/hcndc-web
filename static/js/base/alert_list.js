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
            menu_init('基础配置', '预警配置列表');
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
                form.on('submit(alert-search)', function (data) {
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
                '<div class="layui-inline" lay-event="add" title="添加预警配置"><i class="layui-icon layui-icon-add-1"></i></div>',
                '<div class="layui-inline" lay-event="update" title="修改预警配置"><i class="layui-icon layui-icon-edit"></i></div>',
                '</div>'
            ].join('');
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#alert-list",
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50],
                    title: '任务列表',
                    url: BASE.uri.base.alert_list_api,
                    where: data,
                    cols: [[{
                        type: 'radio'
                    }, {
                        field: "id",
                        title: "配置id",
                        sort: true
                    }, {
                        field: "alert_channel",
                        title: "预警渠道",
                        templet: function (data) {
                            if (data.alert_channel === 1) {
                                return '<span class="layui-badge layui-bg-green">邮件</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-blue">钉钉</span>'
                            }
                        }
                    }, {
                        field: "conf_name",
                        title: "预警配置名称"
                    }, {
                        field: "param_host",
                        title: "邮箱域名",
                        templet: function (data) {
                            if (data.alert_channel === 2) {
                                return '-'
                            } else {
                                return data.param_host
                            }
                        }
                    }, {
                        field: "param_port",
                        title: "邮箱端口",
                        templet: function (data) {
                            if (data.alert_channel === 2) {
                                return '-'
                            } else {
                                return data.param_port
                            }
                        }
                    }, {
                        field: "param_config",
                        title: "预警配置参数"
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
                        templet: function () {
                            let html = [];
                            html.push('<a class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</a>');
                            html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
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
                table.on('toolbar(alert-list)', function (obj) {
                    // 工具栏事件监听
                    let check_status = table.checkStatus(obj.config.id);
                    let check_data = check_status.data;
                    switch (obj.event) {
                        case 'add':
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '新增预警配置',
                                maxmin: true,
                                area: ['60%', '80%'],
                                content: BASE.uri.base.alert_add,
                                end: function () {
                                    window.location.reload();
                                }
                            });
                            break;
                        case 'update':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行')
                            } else if (check_data.length > 1) {
                                layer.msg('只能同时编辑一个')
                            } else {
                                layer.open({
                                    type: 2,
                                    anim: 5,
                                    title: '修改预警配置',
                                    maxmin: true,
                                    area: ['60%', '80%'],
                                    content: BASE.uri.base.alert_update_api + check_data[0].id + '/',
                                    end: function () {
                                        window.location.reload();
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
                table.on('tool(alert-list)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    if (event === 'update') {
                        layer.open({
                            type: 2,
                            anim: 5,
                            title: '修改预警配置',
                            maxmin: true,
                            area: ['60%', '80%'],
                            content: BASE.uri.base.alert_update_api + data.id + '/',
                            end: function () {
                                window.location.reload();
                            }
                        });
                    } else if (event === 'delete') {
                        if (data.is_deleted !== 0) {
                            layer.alert('项目已失效');
                            return
                        }
                        layer.confirm('确定删除?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.base.alert_detail_api + data.id + '/',
                                type: 'delete',
                                success: function (result) {
                                    if (result.status === 200) {
                                        layer.msg('删除成功', {icon: 6});
                                        $(tr.find('td[data-field="operation"] div button')).addClass('layui-btn-disabled');
                                        tr.find('td[data-field="is_deleted"] div').html('<span class="layui-badge layui-bg-gray">删除</span>');
                                    } else {
                                        layer.alert(sprintf('删除失败: [%s]', result.msg), {icon: 5, shift: 6});
                                    }

                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.alert(sprintf('删除项目失败: %s', result.msg))
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