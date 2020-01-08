/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 提示按钮
            this.tooltip_init();
            // 事件组件渲染
            this.restart('run_date');
            // 表单初始化赋值
            this.form_init();
            // 表单提交
            this.form_event();
        },
        // 提示按钮
        tooltip_init: function () {
            $("#sub").hover(function () {
                openMsg();
            }, function () {
                layer.close(subtips);
            });

            function openMsg() {
                let msg = ['%y 两位数的年份表示(00-99)',
                    '%Y 四位数的年份表示(000-9999)',
                    '%m 月份(01-12)',
                    '%d 月内中的一天(0-31)',
                    '%H 24小时制小时数(0-23)',
                    '%I 12小时制小时数(01-12)',
                    '%M 分钟数(00=59)',
                    '%S 秒(00-59)'];
                subtips = layer.tips(msg.join('<br>'), '#sub', {tips: 1, time: 30000});
            }
        },
        // 表单初始化赋值
        form_init: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.val('ftp_event_start', {
                    'date_format': '%Y%m%d'
                });
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(start-save)', function (data) {
                    data = data.field;
                    data.ftp_event_id = window.ftp_event_id.split(',').map(item => Number(item));
                    layer.confirm('确定运行?', function (index) {
                        // 关闭弹窗
                        layer.close(index);
                        $.ajax({
                            url: BASE.uri.ftp_event.action_api,
                            contentType: "application/json; charset=utf-8",
                            type: 'post',
                            data: JSON.stringify(data),
                            success: function (result) {
                                if (result.status === 200) {
                                    layer.msg('启动成功', {icon: 6});
                                    // 关闭自身iframe窗口
                                    setTimeout(function () {
                                        let index = parent.layer.getFrameIndex(window.name);
                                        parent.layer.close(index);
                                    }, 2000);
                                } else {
                                    layer.msg(sprintf('启动失败[%s]', result.msg), {icon: 5, shift: 6});
                                }
                            },
                            error: function (error) {
                                let result = error.responseJSON;
                                layer.msg(sprintf('启动失败[%s]', result.msg), {icon: 5, shift: 6});
                            }
                        });
                    });
                });
            });
        },
        restart: function (field) {
            // 昨天日期
            let now_date = new Date();
            now_date.setTime(now_date.getTime() - 24 * 60 * 60 * 1000);
            let month = now_date.getMonth() + 1 < 10 ? '0' + (now_date.getMonth() + 1) : now_date.getMonth() + 1;
            let day = now_date.getDate() < 10 ? '0' + now_date.getDate() : now_date.getDate();
            let yesterday = now_date.getFullYear() + "-" + month + "-" + day;
            // 日期组件渲染
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    value: yesterday,
                    calendar: true
                })
            });
        }
    };
    new Controller();
})();
