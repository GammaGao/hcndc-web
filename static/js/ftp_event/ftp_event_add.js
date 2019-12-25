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
                form.on('submit(ftp-event-save)', function (data) {
                    data = data.field;
                    console.log(data);
                    $.ajax({
                        url: BASE.uri.ftp_event.add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('新增成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5, shift: 6});
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
        }
    };

    new Controller();
})();