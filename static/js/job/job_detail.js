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
                            'job_name': '任务名称',
                            'interface_name': '任务流名称',
                            'job_desc': '任务描述',
                            'job_index': '任务目录',
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
                        for (let item in res.data) {
                            if (item === 'is_deleted'){
                                res.data[item] = res.data[item] === 0 ? '否': '是'
                            }
                            if (item === 'prep_id'){
                                res.data[item] = res.data[item].join(', ');
                            }
                            if (fields[item]) {
                                data.push({'params': fields[item], 'value': res.data[item]})
                            }
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