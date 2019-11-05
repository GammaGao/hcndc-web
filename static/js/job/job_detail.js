/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 任务详情渲染
            this.job_data_init();
        },
        // 任务详情渲染
        job_data_init: function () {
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#job-detail",
                    page: false,
                    toolbar: false,
                    title: '任务详情',
                    url: BASE.uri.job.detail_api + window.job_id + '/',
                    cols: [[{
                        field: "params",
                        title: "参数名",
                        width: '40%'
                    }, {
                        field: "value",
                        title: "内容值",
                        width: '50%'
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200
                    },
                    parseData: function (res) {
                        let fields = {
                            'job_id': '任务id',
                            'interface_id': '任务流id',
                            'job_name': '任务名称',
                            'job_desc': '任务描述',
                            'server_id': '服务器id',
                            'server_name': '服务器名称',
                            'server_host': '服务器IP',
                            'server_dir': '脚本路径',
                            'server_script': '脚本命令',
                            'return_code': '执行成功返回码',
                            'is_deleted': '是否删除',
                            'prep_id': '依赖任务'
                        };
                        let data = [];
                        for (let i in res.data) {
                            if (i === 'is_deleted'){
                                res.data[i] = res.data[i] === 0 ? '否': '是'
                            }
                            if (i === 'prep_id'){
                                res.data[i] = res.data[i].join(', ');
                            }
                            data.push({'params': fields[i], 'value': res.data[i]})
                        }
                        return {
                            "status": res.status,
                            "msg": res.msg,
                            "data": data
                        };
                    }
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