/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    // cron表达式表单初始化
    let cronFormInit = function () {
        // 分钟选择
        this._minute = [];
        // 时选择
        this._hour = [];
        // 日选择
        this._day = [];
        // 月选择
        this._month = [];
        // 周选择
        this._week_drop = ['mon', 'tue'];
        this._week = [];
        // cron表达式数组
        this.cron_arr = ['*', '*', '*', '*', '*'];
        // 主方法
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 菜单样式加载
            menu_init('调度总览', '');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 调度表单提交事件
            this.form_event();
            // 接口ID渲染
            this.interface_list_id();
            // 调度预警事件注册
            this.dispatch_alert_event_init();
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
        // 接口ID渲染
        interface_list_id: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        for (let i in res.data) {
                            html.push(sprintf(
                                '<option value="%s">%s(%s)</option>',
                                res.data[i].interface_id,
                                res.data[i].interface_id,
                                res.data[i].interface_name
                            ))
                        }
                        $('select[name=interface_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(dispatch-save)', function () {
                    let data = {};
                    data.interface_id = $('select[name=interface_id]').val();
                    data.dispatch_name = $('input[name=dispatch_name]').val();
                    data.dispatch_desc = $('textarea[name=dispatch_desc]').val();
                    data.minute = $('input[name=cron-minute]').val();
                    data.hour = $('input[name=cron-hour]').val();
                    data.day = $('input[name=cron-day]').val();
                    data.month = $('input[name=cron-month]').val();
                    data.week = $('input[name=cron-week]').val();

                    if (!data.interface_id) {
                        layer.alert('接口id不能为空');
                        return
                    }
                    if (!data.dispatch_name) {
                        layer.alert('调度名称不能为空');
                        return
                    }
                    if ([data.minute, data.hour, data.day, data.month, data.week].filter(x => x === '*').length === 5) {
                        layer.alert('请配置运行时间');
                        return
                    }
                    $.ajax({
                        url: BASE.uri.dispatch.add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            window.dispatch_id = result.data.id;
                            layer.open({
                                id: 'dispatch_add_success',
                                btn: ['返回列表', '留在本页'],
                                title: '新增调度成功',
                                content: sprintf('调度id: %s, 状态: %s', result.data.id, result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.dispatch.list;
                                }
                            });
                            // 禁止多次提交
                            $('button[lay-filter=flow-save]').attr('class', 'layui-btn layui-btn-disabled');
                            $('button[lay-filter=flow-save]').attr('disabled', 'disabled');
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'dispatch_add_error',
                                title: '新增调度失败',
                                content: sprintf('%s', result.msg)
                            })
                        }
                    });
                });
            });
        },
        // 调度预警事件初始化
        dispatch_alert_event_init: function () {
            let that = this;
            let config_list = {};
            $.ajax({
                url: BASE.uri.base.alert_list_all_api,
                type: 'get',
                success: function (result) {
                    for (let i in result.data) {
                        if (!config_list[result.data[i].alert_channel]) {
                            config_list[result.data[i].alert_channel] = []
                        }
                        config_list[result.data[i].alert_channel].push({
                            'id': result.data[i].id,
                            'conf_name': result.data[i].conf_name,
                            'param_config': result.data[i].param_config
                        })
                    }
                    that.alert_form_event(config_list);
                }
            });
        },
        // 预警表单初始化
        alert_form_event: function (config_list) {
            layui.use('form', function () {
                let form = layui.form;
                // 监听开关-成功
                form.on('switch(alert_s_button)', function (data) {
                    $('select[name="channel_s"]').attr("disabled", !data.elem.checked);
                    $('select[name="conf_name_s"]').attr("disabled", !data.elem.checked);
                    form.render();
                });
                // 广播渠道联动配置名称-成功
                form.on('select(channel_s)', function (data) {
                    let channel = Number(data.value);
                    let config = config_list[channel];
                    $('select[name="conf_name_s"]').html('<option value="">请选择</option>');
                    for (let i in config) {
                        let option = $("<option>").val(config[i].id).text(config[i].conf_name);
                        $('select[name="conf_name_s"]').append(option);
                    }
                    $('input[name="conf_value_s"]').val('');
                    form.render();
                });
                // 配置名称联动配置参数-成功
                form.on('select(conf_name_s)', function (data) {
                    let channel = Number($('select[name="channel_s"]').val());
                    let index = Number(data.value);
                    let param = {};
                    for (let i in config_list[channel]) {
                        if (config_list[channel][i].id == index) {
                            param = config_list[channel][i]
                        }
                    }
                    $('input[name="conf_value_s"]').val(param.param_config);
                    form.render();
                });
                // 监听开关-失败
                form.on('switch(alert_f_button)', function (data) {
                    $('select[name="channel_f"]').attr("disabled", !data.elem.checked);
                    $('select[name="conf_name_f"]').attr("disabled", !data.elem.checked);
                    form.render();
                });
                // 广播渠道联动配置名称-失败
                form.on('select(channel_f)', function (data) {
                    let channel = Number(data.value);
                    let config = config_list[channel];
                    $('select[name="conf_name_f"]').html('<option value="">请选择</option>');
                    for (let i in config) {
                        let option = $("<option>").val(config[i].id).text(config[i].conf_name);
                        $('select[name="conf_name_f"]').append(option);
                    }
                    $('input[name="conf_value_f"]').val('');
                    form.render();
                });
                // 配置名称联动配置参数-失败
                form.on('select(conf_name_f)', function (data) {
                    let channel = Number($('select[name="channel_f"]').val());
                    let index = Number(data.value);
                    let param = {};
                    for (let i in config_list[channel]) {
                        if (config_list[channel][i].id == index) {
                            param = config_list[channel][i]
                        }
                    }
                    $('input[name="conf_value_f"]').val(param.param_config);
                    form.render();
                });
                // 提交按钮
                form.on('submit(alert-save)', function (data) {
                    data = data.field;
                    data.alert_s_button = data.alert_s_button ? 1 : 0;
                    data.alert_f_button = data.alert_f_button ? 1 : 0;
                    // 参数验证
                    if (!data.alert_s_button && !data.alert_f_button){
                        layer.open({title: '预警配置', content: '预警配置不得为空', icon: 5});
                        return
                    }
                    if (data.alert_s_button) {
                        if (!data.channel_s) {
                            layer.open({title: '预警配置-成功', content: '预警渠道不得为空', icon: 5});
                            return
                        }
                        if (!data.conf_name_s) {
                            layer.open({title: '预警配置-成功', content: '配置名称不得为空', icon: 5});
                            return
                        }
                        if (!data.conf_value_s) {
                            layer.open({title: '预警配置-成功', content: '配置参数不得为空', icon: 5});
                            return
                        }
                    }
                    if (data.alert_f_button) {
                        if (!data.channel_f) {
                            layer.open({title: '预警配置-失败', content: '预警渠道不得为空', icon: 5});
                            return
                        }
                        if (!data.conf_name_f) {
                            layer.open({title: '预警配置-失败', content: '配置名称不得为空', icon: 5});
                            return
                        }
                        if (!data.conf_value_f) {
                            layer.open({title: '预警配置-失败', content: '配置参数不得为空', icon: 5});
                            return
                        }
                    }
                    if (!window.dispatch_id) {
                        layer.open({title: '预警配置添加失败', content: '执行流id不存在, 请先保存执行流', icon: 5});
                        return
                    }
                    let params = {
                        dispatch_id: window.dispatch_id,
                        alert_s: data.alert_s_button,
                        alert_f: data.alert_f_button,
                        conf_id_s: Number(data.conf_name_s),
                        conf_id_f: Number(data.conf_name_f),
                        send_mail_s: data.send_mail_s,
                        send_mail_f: data.send_mail_f
                    };
                    $.ajax({
                        url: BASE.uri.dispatch.alert_add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(params),
                        success: function (result) {
                            layer.open({
                                id: 'dispatch_alert_add_success',
                                btn: ['返回列表', '留在本页'],
                                title: '新增调度预警成功',
                                content: sprintf('调度id: %s, 状态: %s', window.dispatch_id, result.msg),
                                yes: function (index) {
                                    layer.close(index);
                                    window.location.href = BASE.uri.dispatch.list;
                                },
                                btn2: function (index) {
                                    layer.close(index);
                                }
                            });
                            // 禁止多次提交
                            $('button[lay-filter=alert-save]').attr('class', 'layui-btn layui-btn-disabled');
                            $('button[lay-filter=alert-save]').attr('disabled', 'disabled');
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.open({
                                id: 'dispatch_alert_add_error',
                                title: '新增调度预警失败',
                                content: sprintf('调度id: %s, 状态: %s', window.dispatch_id, result.msg)
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
        },
        restart: function (field) {
            // 日期组件渲染
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    calendar: true,
                    range: true
                })
            });
        }
    };

    cronFormInit.prototype = {
        init: function () {
            this.minute_event();
            this.hour_event();
            this.day_event();
            this.month_event();
            this.week_event();
            // cron查询
            this.cron_search();
        },
        // cron查询
        cron_search: function () {
            $('#cron-search').on({
                'click': function () {
                    $.ajax({
                        url: BASE.uri.dispatch.search,
                        type: 'get',
                        data: {
                            sched: [
                                $('input[name=cron-minute]').val(),
                                $('input[name=cron-hour]').val(),
                                $('input[name=cron-day]').val(),
                                $('input[name=cron-month]').val(),
                                $('input[name=cron-week]').val()
                            ].join(' ')
                        },
                        success: function (result) {
                            $('#cron-search-result').html('');
                            let html = [];
                            for (let i in result.data) {
                                html.push(sprintf('<li class="layui-nav-item">%s</li>', result.data[i]))
                            }
                            $('#cron-search-result').html(html.join(''));
                        }
                    });
                }
            });
        },
        // 分方法
        minute_event: function () {
            let that = this;
            // click事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('radio(minute)', function (data) {
                    if (data.value === '0') {
                        that.disable_input('#minute-cycle-1', '#minute-cycle-2');
                        that.disable_input('#minute-loop-1', '#minute-loop-2');
                        that.disable_click('.minuteList input');
                        that.select_none(0);
                    } else if (data.value === '1') {
                        that.disable_input('#minute-loop-1', '#minute-loop-2');
                        that.disable_click('.minuteList input');
                        that.select_cycle('#minute-cycle-1', '#minute-cycle-2', 0)
                    } else if (data.value === '2') {
                        that.disable_input('#minute-cycle-1', '#minute-cycle-2');
                        that.disable_click('.minuteList input');
                        that.select_loop('#minute-loop-1', '#minute-loop-2', 0)
                    } else if (data.value === '3') {
                        that.disable_input('#minute-cycle-1', '#minute-cycle-2');
                        that.disable_input('#minute-loop-1', '#minute-loop-2');
                        that.select_click('.minuteList input', 0)
                    }
                    that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
                });
            });
            // change事件
            // 周期
            $('#minute-cycle-1').change(function () {
                that.cron_arr[0] = $('#minute-cycle-1').val() + '-' + $('#minute-cycle-2').val();
                that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
            });
            $('#minute-cycle-2').change(function () {
                that.cron_arr[0] = $('#minute-cycle-1').val() + '-' + $('#minute-cycle-2').val();
                that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
            });
            // 循环
            $('#minute-loop-1').change(function () {
                that.cron_arr[0] = $('#minute-loop-1').val() + '/' + $('#minute-loop-2').val();
                that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
            });
            $('#minute-loop-2').change(function () {
                that.cron_arr[0] = $('#minute-loop-1').val() + '/' + $('#minute-loop-2').val();
                that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
            });
            // 指定
            layui.use('form', function () {
                let form = layui.form;
                form.on('checkbox(minute)', function (data) {
                    if (data.elem.checked) {
                        that._minute.push(data.value)
                    } else {
                        let index = that._minute.indexOf(data.value);
                        if (index > -1) {
                            that._minute.splice(index, 1)
                        }
                    }
                    that._minute.sort((x, y) => Number(x) - Number(y));
                    that.cron_arr[0] = that._minute.join(',');
                    that.change_cron_value('input[name=cron-minute]', that.cron_arr[0])
                });
            })
        },
        // 时方法
        hour_event: function () {
            let that = this;
            // click事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('radio(hour)', function (data) {
                    if (data.value === '0') {
                        that.disable_input('#hour-cycle-1', '#hour-cycle-2');
                        that.disable_input('#hour-loop-1', '#hour-loop-2');
                        that.disable_click('.hourList input');
                        that.select_none(1);
                    } else if (data.value === '1') {
                        that.disable_input('#hour-loop-1', '#hour-loop-2');
                        that.disable_click('.hourList input');
                        that.select_cycle('#hour-cycle-1', '#hour-cycle-2', 1)
                    } else if (data.value === '2') {
                        that.disable_input('#hour-cycle-1', '#hour-cycle-2');
                        that.disable_click('.hourList input');
                        that.select_loop('#hour-loop-1', '#hour-loop-2', 1)
                    } else if (data.value === '3') {
                        that.disable_input('#hour-cycle-1', '#hour-cycle-2');
                        that.disable_input('#hour-loop-1', '#hour-loop-2');
                        that.select_click('.hourList input', 1)
                    }
                    that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
                });
            });
            // change事件
            // 周期
            $('#hour-cycle-1').change(function () {
                that.cron_arr[1] = $('#hour-cycle-1').val() + '-' + $('#hour-cycle-2').val();
                that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
            });
            $('#hour-cycle-2').change(function () {
                that.cron_arr[1] = $('#hour-cycle-1').val() + '-' + $('#hour-cycle-2').val();
                that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
            });
            // 循环
            $('#hour-loop-1').change(function () {
                that.cron_arr[1] = $('#hour-loop-1').val() + '/' + $('#hour-loop-2').val();
                that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
            });
            $('#hour-loop-2').change(function () {
                that.cron_arr[1] = $('#hour-loop-1').val() + '/' + $('#hour-loop-2').val();
                that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
            });
            // 指定
            layui.use('form', function () {
                let form = layui.form;
                form.on('checkbox(hour)', function (data) {
                    if (data.elem.checked) {
                        that._hour.push(data.value)
                    } else {
                        let index = that._hour.indexOf(data.value);
                        if (index > -1) {
                            that._hour.splice(index, 1)
                        }
                    }
                    that._hour.sort((x, y) => Number(x) - Number(y));
                    that.cron_arr[1] = that._hour.join(',');
                    that.change_cron_value('input[name=cron-hour]', that.cron_arr[1])
                });
            })
        },
        // 日方法
        day_event: function () {
            let that = this;
            // click事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('radio(day)', function (data) {
                    if (data.value === '0') {
                        that.disable_input('#day-cycle-1', '#day-cycle-2');
                        that.disable_input('#day-loop-1', '#day-loop-2');
                        that.disable_click('.dayList input');
                        that.select_none(2);
                    } else if (data.value === '1') {
                        that.disable_input('#day-loop-1', '#day-loop-2');
                        that.disable_click('.dayList input');
                        that.select_cycle('#day-cycle-1', '#day-cycle-2', 2)
                    } else if (data.value === '2') {
                        that.disable_input('#day-cycle-1', '#day-cycle-2');
                        that.disable_click('.dayList input');
                        that.select_loop('#day-loop-1', '#day-loop-2', 2)
                    } else if (data.value === '3') {
                        that.disable_input('#day-cycle-1', '#day-cycle-2');
                        that.disable_input('#day-loop-1', '#day-loop-2');
                        that.select_click('.dayList input', 2)
                    }
                    that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
                });
            });
            // change事件
            // 周期
            $('#day-cycle-1').change(function () {
                that.cron_arr[2] = $('#day-cycle-1').val() + '-' + $('#day-cycle-2').val();
                that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
            });
            $('#day-cycle-2').change(function () {
                that.cron_arr[2] = $('#day-cycle-1').val() + '-' + $('#day-cycle-2').val();
                that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
            });
            // 循环
            $('#day-loop-1').change(function () {
                that.cron_arr[2] = $('#day-loop-1').val() + '/' + $('#day-loop-2').val();
                that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
            });
            $('#day-loop-2').change(function () {
                that.cron_arr[2] = $('#day-loop-1').val() + '/' + $('#day-loop-2').val();
                that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
            });
            // 指定
            layui.use('form', function () {
                let form = layui.form;
                form.on('checkbox(day)', function (data) {
                    if (data.elem.checked) {
                        that._day.push(data.value)
                    } else {
                        let index = that._day.indexOf(data.value);
                        if (index > -1) {
                            that._day.splice(index, 1)
                        }
                    }
                    that._day.sort((x, y) => Number(x) - Number(y));
                    that.cron_arr[2] = that._day.join(',');
                    that.change_cron_value('input[name=cron-day]', that.cron_arr[2])
                });
            })
        },
        // 月方法
        month_event: function () {
            let that = this;
            // click事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('radio(month)', function (data) {
                    if (data.value === '0') {
                        that.disable_input('#month-cycle-1', '#month-cycle-2');
                        that.disable_input('#month-loop-1', '#month-loop-2');
                        that.disable_click('.monthList input');
                        that.select_none(3);
                    } else if (data.value === '1') {
                        that.disable_input('#month-loop-1', '#month-loop-2');
                        that.disable_click('.monthList input');
                        that.select_cycle('#month-cycle-1', '#month-cycle-2', 3)
                    } else if (data.value === '2') {
                        that.disable_input('#month-cycle-1', '#month-cycle-2');
                        that.disable_click('.monthList input');
                        that.select_loop('#month-loop-1', '#month-loop-2', 3)
                    } else if (data.value === '3') {
                        that.disable_input('#month-cycle-1', '#month-cycle-2');
                        that.disable_input('#month-loop-1', '#month-loop-2');
                        that.select_click('.monthList input', 3)
                    }
                    that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
                });
            });
            // change事件
            // 周期
            $('#month-cycle-1').change(function () {
                that.cron_arr[3] = $('#month-cycle-1').val() + '-' + $('#month-cycle-2').val();
                that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
            });
            $('#month-cycle-2').change(function () {
                that.cron_arr[3] = $('#month-cycle-1').val() + '-' + $('#month-cycle-2').val();
                that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
            });
            // 循环
            $('#month-loop-1').change(function () {
                that.cron_arr[3] = $('#month-loop-1').val() + '/' + $('#month-loop-2').val();
                that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
            });
            $('#month-loop-2').change(function () {
                that.cron_arr[3] = $('#month-loop-1').val() + '/' + $('#month-loop-2').val();
                that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
            });
            // 指定
            layui.use('form', function () {
                let form = layui.form;
                form.on('checkbox(month)', function (data) {
                    if (data.elem.checked) {
                        that._month.push(data.value)
                    } else {
                        let index = that._month.indexOf(data.value);
                        if (index > -1) {
                            that._month.splice(index, 1)
                        }
                    }
                    that._month.sort((x, y) => Number(x) - Number(y));
                    that.cron_arr[3] = that._month.join(',');
                    that.change_cron_value('input[name=cron-month]', that.cron_arr[3])
                });
            })
        },
        // 周方法
        week_event: function () {
            let that = this;
            // click事件
            layui.use('form', function () {
                let form = layui.form;
                form.on('radio(week)', function (data) {
                    if (data.value === '0') {
                        that.disable_drop('#week-list-1', '#week-list-2');
                        that.disable_click('.weekList input');
                        that.select_none(4);
                    } else if (data.value === '1') {
                        that.disable_click('.weekList input');
                        that.select_drop('#week-list-1', '#week-list-2', 4)
                    } else if (data.value === '2') {
                        that.disable_drop('#week-list-1', '#week-list-2');
                        that.select_click('.weekList input', 4)
                    }
                    that.change_cron_value('input[name=cron-week]', that.cron_arr[4])
                });
            });
            // change事件
            // 列表
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(week-list-1)', function (data) {
                    that._week_drop[0] = data.value;
                    that.cron_arr[4] = that._week_drop.join('-');
                    that.change_cron_value('input[name=cron-week]', that.cron_arr[4])
                });
                form.on('select(week-list-2)', function (data) {
                    that._week_drop[1] = data.value;
                    that.cron_arr[4] = that._week_drop.join('-');
                    that.change_cron_value('input[name=cron-week]', that.cron_arr[4])
                });
            });
            // 指定
            layui.use('form', function () {
                let form = layui.form;
                form.on('checkbox(week)', function (data) {
                    if (data.elem.checked) {
                        that._week.push(data.value)
                    } else {
                        let index = that._week.indexOf(data.value);
                        if (index > -1) {
                            that._week.splice(index, 1)
                        }
                    }
                    that._week.sort((x, y) => {
                        _index = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
                        return _index.indexOf(x) - _index.indexOf(y)
                    });
                    that.cron_arr[4] = that._week.join(',');
                    that.change_cron_value('input[name=cron-week]', that.cron_arr[4])
                });
            })
        },
        // 改变表达式值
        change_cron_value: function (elem, value) {
            // 时赋值
            if (elem === 'input[name=cron-hour]') {
                if ($('input[name=cron-minute]').val() === '*') {
                    $('input[name=cron-minute]').val('0')
                }
            }
            // 日赋值
            else if (elem === 'input[name=cron-day]') {
                if ($('input[name=cron-minute]').val() === '*') {
                    $('input[name=cron-minute]').val('0')
                }
                if ($('input[name=cron-hour]').val() === '*') {
                    $('input[name=cron-hour]').val('0')
                }
                $('input[name=cron-week]').val('*');
            }
            // 月赋值
            else if (elem === 'input[name=cron-month]') {
                if ($('input[name=cron-minute]').val() === '*') {
                    $('input[name=cron-minute]').val('0')
                }
                if ($('input[name=cron-hour]').val() === '*') {
                    $('input[name=cron-hour]').val('0')
                }
            }
            // 周赋值
            else if (elem === 'input[name=cron-week]') {
                if ($('input[name=cron-minute]').val() === '*') {
                    $('input[name=cron-minute]').val('0')
                }
                if ($('input[name=cron-hour]').val() === '*') {
                    $('input[name=cron-hour]').val('0')
                }
                $('input[name=cron-day]').val('*')
            }
            $(elem).val(value);
        },
        // 选中默认
        select_none: function (index) {
            this.cron_arr[index] = '*';
        },
        // 选中周期
        select_cycle: function (elem_1, elem_2, index) {
            $(elem_1).attr('disabled', false);
            $(elem_2).attr('disabled', false);
            this.cron_arr[index] = $(elem_1).val() + '-' + $(elem_2).val();
        },
        // 选中循环
        select_loop: function (elem_1, elem_2, index) {
            $(elem_1).attr('disabled', false);
            $(elem_2).attr('disabled', false);
            this.cron_arr[index] = $(elem_1).val() + '/' + $(elem_2).val();
        },
        // 选中指定
        select_click: function (elem, index) {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                $(elem).attr('disabled', false);
                form.render();
            });
            that.cron_arr[index] = '*';
        },
        // 选中列表
        select_drop: function (elem1, elem2, index) {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                $(elem1).attr('disabled', false);
                $(elem2).attr('disabled', false);
                form.render()
            });
            that.cron_arr[index] = $(elem1).val() + '-' + $(elem2).val();
        },
        // 禁止input
        disable_input: function (elem_1, elem_2) {
            $(elem_1).attr('disabled', true);
            $(elem_2).attr('disabled', true);
        },
        // 禁止指定
        disable_click: function (elem) {
            layui.use('form', function () {
                let form = layui.form;
                $(elem).attr('disabled', true);
                $(elem + ':checked').prop('checked', false);
                form.render();
            });
        },
        // 禁止下拉
        disable_drop: function (elem1, elem2) {
            layui.use('form', function () {
                let form = layui.form;
                $(elem1).attr('disabled', true);
                $(elem2).attr('disabled', true);
                form.render();
            })
        }
    };

    new Controller();
    new cronFormInit();
})();