/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 日志数据渲染
            this.log_data_load();
            // UI组件渲染
            // this.restart('run_date');
        },
        // 日志数据渲染
        log_data_load: function () {
            $.ajax({
                url: BASE.uri.execute.log_api,
                type: 'get',
                data: {'exec_id': window.exec_id, 'job_id': window.job_id},
                success: function (res) {
                    let data = res.data;
                    let $exec_log = $('#exec-log');
                    for (let i = 0; i < data.length; i++){
                        let html = [];
                        html.push('<li class="layui-timeline-item">');
                        if (data[i].level === 'INFO'){
                            html.push('<i class="layui-icon layui-timeline-axis INFO">&#xe63f;</i>');
                        } else if (data[i].level === 'ERROR'){
                            html.push('<i class="layui-icon layui-timeline-axis ERROR">&#xe63f;</i>');
                        } else {
                            html.push('<i class="layui-icon layui-timeline-axis">&#xe63f;</i>');
                        }
                        html.push('<div class="layui-timeline-content layui-text">');
                        html.push('<div class="layui-timeline-title"><ul>');
                        if (data[i].level === 'INFO'){
                            html.push('<li>等级: 正常</li>');
                        } else if (data[i].level === 'ERROR'){
                            html.push('<li>等级: 异常</li>');
                        } else {
                            html.push('<li>等级: ' + data[i].level + '</li>');
                        }
                        html.push('<li>消息: '+ data[i].message + '</li>');
                        // html.push('<li>时间: '+ data[i].time + '</li>');
                        html.push('</div></div></li>');
                        $exec_log.append(html.join(''));
                    }
                },
                error: function (error) {
                    let result = error.responseJSON;
                    layer.alert(sprintf('退出登陆失败: %s', result.msg))
                }
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
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    type: 'datetime',
                    range: true
                })
            });
        }
    };
    new Controller();
})();