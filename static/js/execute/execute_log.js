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
            // 日志数据请求
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#exec-job-log",
                    page: true,
                    toolbar: true,
                    limit: 100,
                    limits: [100, 200, 300, 400, 500],
                    title: '日志内容',
                    url: BASE.uri.execute.log_api,
                    where: {'exec_id': window.exec_id, 'job_id': window.job_id},
                    cols: [[{
                        field: "level",
                        title: "日志级别",
                        width: '8%'
                    }, {
                        field: "message",
                        title: "日志信息"
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200,
                        countName: 'total'
                    }
                });
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