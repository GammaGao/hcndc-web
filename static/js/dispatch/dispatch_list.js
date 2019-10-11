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
            // 接口ID渲染
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
        // 接口ID渲染
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
                        type: 'radio'
                    }, {
                        field: "dispatch_id",
                        title: "调度id",
                        width: '5%',
                        sort: true
                    }, {
                        field: "interface_id",
                        title: "接口id",
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
                                // 运行中
                            } else if (data.status === 1) {
                                html.push('<button class="layui-btn layui-btn-sm" lay-event="run">立即执行</button>');
                                html.push('<button class="layui-btn PREPARING layui-btn-sm" lay-event="pause">暂停</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                                // 暂停中
                            } else if (data.status === 2) {
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
                        case 'add':
                            layer.open({
                                id: 'dispatch_add',
                                btn: ['跳转', '取消'],
                                title: '跳转新增调度页面',
                                content: '确定新增调度?',
                                yes: function (index, layero) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.dispatch.add;
                                }
                            });
                            break;
                        case 'update':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行');
                            } else if (check_data.length > 1) {
                                layer.msg('只能同时编辑一个')
                            } else {
                                window.location.href = BASE.uri.dispatch.update + check_data[0].dispatch_id + '/';
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
                            layer.confirm('确定立即执行?', function (index) {
                                layer.close(index);
                                console.log(data);
                                $.ajax({
                                    url: BASE.uri.dispatch.detail_api + data.dispatch_id + '/',
                                    contentType: "application/json; charset=utf-8",
                                    type: 'post',
                                    success: function () {
                                        layer.open({
                                            id: 'dispatch_run_success',
                                            btn: ['跳转', '留在本页'],
                                            title: '立即执行调度成功',
                                            content: '是否跳转至执行日志?',
                                            yes: function (index) {
                                                layer.close(index);
                                                window.location.href = BASE.uri.execute.list;
                                            },
                                            btn2: function (index) {
                                                layer.close(index);
                                                // 刷新页面
                                                window.location.reload();
                                            }
                                        });
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.open({
                                            id: 'dispatch_run_error',
                                            title: '立即执行任务失败',
                                            content: sprintf('%s', result.msg)
                                        })
                                    }
                                });
                            });
                            break;
                        // 暂停
                        case 'pause':
                            $.ajax({
                                url: BASE.uri.dispatch.detail_api + data.dispatch_id + '/',
                                contentType: "application/json; charset=utf-8",
                                type: 'patch',
                                data: JSON.stringify({'action': 1}),
                                success: function () {
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
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.open({
                                        id: 'dispatch_pause_error',
                                        title: '暂停调度失败',
                                        content: sprintf('%s', result.msg)
                                    })
                                }
                            });
                            break;
                        // 恢复
                        case 'resume':
                            $.ajax({
                                url: BASE.uri.dispatch.detail_api + data.dispatch_id + '/',
                                contentType: "application/json; charset=utf-8",
                                type: 'patch',
                                data: JSON.stringify({'action': 2}),
                                success: function () {
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
                                },
                                error: function (error) {
                                    let result = error.responseJSON;
                                    layer.open({
                                        id: 'dispatch_resume_error',
                                        title: '恢复调度失败',
                                        content: sprintf('%s', result.msg)
                                    })
                                }
                            });
                            break;
                        // 修改
                        case 'update':
                            window.location.href = BASE.uri.dispatch.update + data.dispatch_id + '/';
                            break;
                        // 删除
                        case 'delete':
                            layer.confirm('确定删除?', function (index) {
                                // 关闭弹窗
                                layer.close(index);
                                $.ajax({
                                    url: BASE.uri.dispatch.detail_api + data.dispatch_id + '/',
                                    type: 'delete',
                                    success: function () {
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