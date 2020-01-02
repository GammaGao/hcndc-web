/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 提示按钮
            this.tooltip_init();
            // 任务流ID渲染
            this.interface_list_id();
            // FTP配置ID渲染
            this.ftp_list_id();
            // 任务表单事件注册
            this.form_event();
            // UI组件渲染
            this.restart('date_time');
            // 数据初始化赋值
            this.form_data_init();
        },
        // 提示按钮
        tooltip_init: function () {
            $("#sub").hover(function () {
                openMsg();
            }, function () {
                layer.close(subtips);
            });

            function openMsg() {
                let msg = [
                    '支持正则表达式:',
                    '%y 两位数的年份表示(00-99)',
                    '%Y 四位数的年份表示(0000-9999)',
                    '%m 月份(01-12)',
                    '%d 月内中的一天(01-31)',
                    '%H 24小时制小时数(00-23)',
                    '%I 12小时制小时数(01-12)',
                    '%M 分钟数(00-59)',
                    '%S 秒(00-59)'
                ];
                subtips = layer.tips(msg.join('<br>'), '#sub', {tips: 1, time: 30000});
            }
        },
        // 任务流ID渲染
        interface_list_id: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    for (let i = 0; i < res.data.length; i++) {
                        html.push(sprintf('<option value="%s">%s(%s)</option>',
                            res.data[i].interface_id,
                            res.data[i].interface_id,
                            res.data[i].interface_name
                        ))
                    }
                    $('select[xm-select=interface_id]').append(html.join(''));
                    formSelects.render('job_prep');
                }
            })
        },
        // FTP配置ID渲染
        ftp_list_id: function () {
            $.ajax({
                url: BASE.uri.ftp.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        for (let i = 0; i < res.data.length; i++) {
                            html.push(sprintf(
                                '<option value="%s">%s(%s)</option>',
                                res.data[i].ftp_id,
                                res.data[i].ftp_id,
                                res.data[i].ftp_name
                            ))
                        }
                        $('select[name=ftp_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(ftp-event-update)', function (data) {
                    data = data.field;
                    data.old_status = window.old_status;
                    data.new_status = Number(data.status);
                    $.ajax({
                        url: BASE.uri.ftp_event.detail_api + window.ftp_event_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('修改成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5, shift: 6});
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
        // 日期组件渲染
        restart: function (field) {
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    format: 'yyyy-MM-dd',
                    calendar: true,
                    range: false
                })
            });
        },
        // 数据初始化赋值
        form_data_init: function () {
            $.ajax({
                url: BASE.uri.ftp_event.detail_api + window.ftp_event_id + '/',
                type: 'get',
                success: function (result) {
                    let data = result.data;
                    // 详情填充
                    window.old_status = data.status;
                    layui.use(['form', 'laydate'], function () {
                        // 详情参数初始化
                        let form = layui.form;
                        let formSelects = layui.formSelects;
                        form.val('ftp_event_detail', {
                            'event_name': data.event_name,
                            'event_desc': data.event_desc,
                            'ftp_id': data.ftp_id,
                            'data_path': data.data_path,
                            'file_name': data.file_name,
                            'start_time': data.start_time,
                            'end_time': data.end_time,
                            'date_time': data.date_time,
                            'interval_value': data.interval_value,
                            'status': data.status
                        });
                        form.render();
                        // 数据日期参数初始化
                        if (data.date_time) {
                            let laydate = layui.laydate;
                            laydate.render({
                                elem: 'input[name=date_time]',
                                value: data.date_time
                            })
                        }
                        // 前置任务流依赖初始化
                        formSelects.value('interface_id', data.interface_id);
                    });
                }
            });
        }
    };

    new Controller();
})();