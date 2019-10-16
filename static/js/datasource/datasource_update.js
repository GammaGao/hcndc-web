/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 菜单样式加载
            menu_init('任务总览', '');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 数据源配置表单选择器监听
            this.select_form_event();
            // 数据源详情请求
            this.datasource_detail_request();
            // 任务表单事件注册
            this.form_event();
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
        // 数据源表单选择器监听
        select_form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(source_type)', function (data) {
                    // hive / impala 认证方式
                    if (Number(data.value) < 4) {
                        $('select[name=auth_type]').parent().parent().parent().css('display', 'none');
                    } else {
                        $('select[name=auth_type]').parent().parent().parent().removeAttr('style');
                    }
                    form.render();
                });
            })
        },
        // 数据源详情请求
        datasource_detail_request: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.datasource.detail_api +  window.source_id + '/',
                type: 'get',
                success: function (result) {
                    if (result.status === 200) {
                        that.datasource_detail_init(result.data)
                    } else {
                        layer.alert('请求数据源详情API异常', {icon: 5});
                    }
                }
            });
        },
        // 数据源详情初始化
        datasource_detail_init: function (data) {
            layui.use('form', function () {
                let form = layui.form;
                form.val('datasource_detail', {
                    'source_name': data.source_name,
                    'source_type': data.source_type,
                    'source_host': data.source_host,
                    'source_port': data.source_port,
                    'source_user': data.source_user,
                    'source_password': data.source_password,
                    'source_desc': data.source_desc,
                    'is_deleted': data.is_deleted === 1
                });
                form.render();
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 测试连接
                form.on('submit(datasource-test)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.datasource.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.alert(result.msg, {icon: 6});
                            } else {
                                layer.alert(result.msg, {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('连接服务器失败: [%s]', result.msg), {icon: 2});
                        }
                    })
                });
                // 保存表单
                form.on('submit(datasource-update)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.datasource.detail_api +  window.source_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            layer.open({
                                id: 'datasource_update_success',
                                btn: ['返回列表', '留在本页'],
                                title: '修改数据源成功',
                                content: sprintf('数据源id: %s, 状态: %s', result.data.source_id, result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.datasource.list;
                                }
                            })
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'datasource_update_error',
                                title: '修改数据源失败',
                                content: sprintf('数据源id: %s, 状态: %s', data.source_id, result.msg)
                            })
                        }
                    });
                });
            });
        },
        element_init: function () {
            // 元素渲染刷新
            layui.use('element', function () {
                let element = layui.element;
                element.init();
            });
        }
    };
    new Controller();
})();