/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 导航栏样式加载
            this.navigate_load('基础配置');
            // 侧边栏数据渲染
            this.menu_load(BASE.base, '执行服务器列表');
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
        navigate_load: function (name) {
            $('.layui-nav.layui-layout-left').children().each(function () {
                if ($(this).text().replace(/\s+/g, "") == name) {
                    $(this).addClass('layui-this')
                }
            })
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
        menu_load: function (items, name) {
            let html = [];
            for (let i in items) {
                if (items[i]['uri']) {
                    if (name === items[i]['name'].replace(/\s+/g, "")) {
                        html.push('<li class="layui-nav-item layui-this">');
                    } else {
                        html.push('<li class="layui-nav-item">');
                    }
                    html.push('<a href="', items[i]['uri'], '">');
                    html.push('<i class="', items[i]['icon'], ' icon-size-medium"></i>');
                    html.push('<span >', items[i]['name'], '</span>');
                    html.push('</a></li>');
                } else {
                    html.push('<li class="layui-nav-item layui-nav-itemed">');
                    html.push('<a href="#">');
                    html.push('<i class="', items[i]['icon'], ' icon-size-medium"></i>');
                    html.push('<span >', items[i]['name'], '</span>');
                    html.push('</a>');
                    html.push('<dl class="layui-nav-child">');
                    for (let j in items[i]['children']) {
                        if (name === items[i]['children'][j]['name'].replace(/\s+/g, "")) {
                            html.push('<dd class="layui-this"><a href="', items[i]['children'][j]['uri'], '">');
                        } else {
                            html.push('<dd><a href="', items[i]['children'][j]['uri'], '">');
                        }

                        if (!!items[i]['children'][j]['icon']) {
                            html.push('<i class="', items[i]['children'][j]['icon'], '"></i>');
                        }
                        html.push('<span >', items[i]['children'][j]['name'], '</span></a></dd>');
                    }
                    html.push('</dl></li>');
                }
            }
            $('ul[lay-filter=tree]').html(html.join(''));
            // 元素渲染
            this.element_init();
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
                    elem: "#host-list",
                    page: true,
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50],
                    title: '任务列表',
                    url: BASE.uri.base.exec_host_api,
                    where: data,
                    cols: [[{
                        field: "server_id",
                        title: "服务器id",
                        sort: true
                    }, {
                        field: "server_host",
                        title: "服务器IP"
                    }, {
                        field: "server_name",
                        title: "服务器名称"
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
                            html.push('<a class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</a>');
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
                table.on('tool(host-list)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    if (event === 'update') {
                        window.location.href = BASE.uri.base.exec_host_update + data.server_id + '/';
                    } else if (event === 'delete') {
                        if (data.is_deleted !== 0) {
                            layer.alert('项目已失效');
                            return
                        }
                        layer.confirm('确定删除?', function (index) {
                            // 关闭弹窗
                            layer.close(index);
                            $.ajax({
                                url: BASE.uri.base.exec_host_detail_api + data.server_id + '/',
                                type: 'delete',
                                success: function () {
                                    layer.alert('删除成功');
                                    tr.find('td[data-field="is_deleted"] div').html('<span class="layui-badge layui-bg-gray">删除</span>');
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