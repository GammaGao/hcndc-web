/**
 * Created by xx on 2018/12/18.
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
            this.menu_load(BASE.base, '');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 预警配置表单初始化
            this.alert_form_init();
            // 预警表单提交注册
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
                    if (name == items[i]['name'].replace(/\s+/g, "")) {
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
                        if (name == items[i]['children'][j]['name'].replace(/\s+/g, "")) {
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
        // 预警配置表单初始化
        alert_form_init: function () {
            $.ajax({
                url: BASE.uri.base.alert_detail_api + window.conf_id + '/',
                type: 'get',
                success: function (result) {
                    let data = result.data;
                    layui.use('form', function () {
                        let form = layui.form;
                        form.val('alert_conf_detail', {
                            'alert_channel': data.alert_channel,
                            'conf_name': data.conf_name,
                            'param_host': data.param_host,
                            'param_port': data.param_port,
                            'param_config': data.param_config,
                            'param_pass': data.param_pass,
                            'is_deleted': data.is_deleted === 1
                        });
                        // 钉钉隐藏该选项
                        if (data.alert_channel === 2){
                            $('input[name=param_host]').parent().parent().css('display', 'none');
                            $('input[name=param_port]').parent().parent().css('display', 'none');
                            $('input[name=param_pass]').parent().parent().css('display', 'none');
                        }
                        form.render();
                    })
                }
            });
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(alert-save)', function (data) {
                    data = data.field;
                    data.is_deleted = data.is_deleted ? 1 : 0;
                    data.param_port = data.param_port ? data.param_port : 0;
                    $.ajax({
                        url: BASE.uri.base.alert_detail_api + window.conf_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            layer.open({
                                id: 'alert_update_success',
                                btn: ['返回列表', '留在本页'],
                                title: '修改预警配置成功',
                                content: sprintf('状态: %s', result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.base.alert_list;
                                }
                            })
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'alert_update_error',
                                title: '修改预警配置失败',
                                content: sprintf('状态: %s', result.msg)
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