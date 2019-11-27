/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // Tab切换事件
            this.tab_change_event();
            // 表格数据初始化
            // this.table_data_load({});
            // // 执行任务拓扑结构渲染
            // this.exec_graph_init();
            // // 日志数据渲染
            // this.log_data_load();
            // UI组件渲染
            // this.restart('run_date');
        },
        // Tab切换事件
        tab_change_event: function () {
            let that = this;
            layui.use(['element'], function () {
                let element = layui.element;
                element.on('tab(detail-tab)', function (data) {
                    if (data.index === 0 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // TODO 添加任务流拓扑渲染
                        return ;
                    } else if (data.index === 1 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 执行任务拓扑结构渲染
                        return that.exec_graph_init();
                    } else if (data.index === 2 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 表格数据初始化
                        return that.table_data_load({});
                    } else if (data.index === 3 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 日志数据渲染
                        return that.log_data_load();
                    }
                });
            });
        },
        // 表格组件渲染
        table_data_load: function (data) {
            // 事件监听
            let that = this;
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#exec-detail",
                    page: false,
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50],
                    title: '日志详情',
                    url: BASE.uri.execute.detail_api + window.exec_id + '/',
                    where: data,
                    cols: [[{
                        field: "job_id",
                        title: "任务id",
                        width: '8%',
                        sort: true
                    }, {
                        field: "position",
                        title: "外部依赖",
                        width: '8%',
                        templet: function (data) {
                            if (data.position === 2) {
                                return '<span class="layui-badge layui-bg-green">是</span>';
                            } else {
                                return '-';
                            }
                        }
                    }, {
                        field: "insert_time",
                        title: "开始时间",
                        width: '15%'
                    }, {
                        field: "update_time",
                        title: "结束时间",
                        width: '15%'
                    }, {
                        field: "timedelta",
                        title: "时长",
                        width: '8%'
                    }, {
                        field: "status",
                        title: "状态",
                        width: '8%',
                        templet: function (data) {
                            switch (data.status) {
                                case 'ready':
                                    return '<span class="layui-badge READY">等待依赖任务完成</span>';
                                case 'preparing':
                                    return '<span class="layui-badge PREPARING">待运行</span>';
                                case 'running':
                                    return '<span class="layui-badge RUNNING">运行中</span>';
                                case 'succeeded':
                                    return '<span class="layui-badge SUCCEEDED">成功</span>';
                                case 'failed':
                                    return '<span class="layui-badge FAILED">失败</span>';
                                case '':
                                    return '';
                                default:
                                    return '<span class="layui-badge-rim">' + data.status + '</span>';
                            }
                        }
                    }, {
                        field: "timeline",
                        title: "时间线",
                        templet: function (data) {
                            let html = ['<div class="flow-progress">',
                                '<div class="flow-progress-bar %s" ',
                                'style="margin-left: ',
                                data.margin_left,
                                '; width: ',
                                data.width,
                                ';"></div></div>'].join('');
                            switch (data.status) {
                                case 'ready':
                                    return sprintf(html, 'READY');
                                case 'preparing':
                                    return sprintf(html, 'PREPARING');
                                case 'running':
                                    return sprintf(html, 'RUNNING');
                                case 'succeeded':
                                    return sprintf(html, 'SUCCEEDED');
                                case 'failed':
                                    return sprintf(html, 'FAILED');
                                default:
                                    return sprintf(html, '');
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            if (data.position === 2) {
                                return '';
                            } else {
                                return '<a class="layui-btn layui-btn-sm" lay-event="detail">详情日志</a>';
                            }
                        }
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200,
                        countName: 'total'
                    }
                });
                // 事件监听
                that.table_data_event();
            });
        },
        // 表格事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(exec-detail)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    if (event === 'detail') {
                        window.location.href = BASE.uri.execute.log + window.exec_id + '/' + data.job_id + '/';
                    }
                })
            })
        },
        // 执行任务拓扑结构渲染
        exec_graph_init: function () {
            $.ajax({
                url: BASE.uri.execute.graph_api,
                type: 'get',
                data: {'exec_id': window.exec_id},
                success: function (response) {
                    dom = document.getElementById('svg-div');
                    myChart = echarts.init(dom, 'light');
                    myChart.hideLoading();

                    graph = response.data;
                    categories = graph.categories;

                    option = {
                        title: {
                            text: '任务流中任务依赖',
                            subtext: '默认布局',
                            top: 'top',
                            left: 'right'
                        },
                        tooltip: {formatter: '任务: {b}'},
                        legend: [{
                            type: 'scroll',
                            left: 30,
                            orient: 'vertical',
                            data: categories.map(function (a) {
                                return a.name;
                            })
                        }],
                        color: ['#FFB800', '#F19153', '#3398CC', '#5CB85C', '#D9534F', '#1E9FFF', '#C9C9C9'],
                        series: [
                            {
                                type: 'graph',
                                layout: 'none',
                                data: graph.nodes,
                                links: graph.links,
                                categories: categories,
                                roam: true,
                                edgeSymbol: ['none', 'arrow'],
                                focusNodeAdjacency: true,
                                itemStyle: {
                                    normal: {
                                        borderColor: '#fff',
                                        borderWidth: 1,
                                        shadowBlur: 10,
                                        shadowColor: 'rgba(0, 0, 0, 0.3)'
                                    }
                                },
                                lineStyle: {
                                    color: 'source',
                                },
                            }
                        ]
                    };

                    myChart.setOption(option);
                },
                error: function (error) {
                    let result = error.responseJSON;
                    layer.alert(sprintf('任务依赖渲染失败: %s', result.msg))
                }
            })
        },
        // 日志数据渲染
        log_data_load: function () {
            // 日志数据请求
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#exec-log",
                    page: false,
                    toolbar: false,
                    title: '日志内容',
                    url: BASE.uri.execute.log_api,
                    where: {'exec_id': window.exec_id},
                    cols: [[{
                        field: "job_id",
                        title: "任务ID",
                        width: '8%'
                    }, {
                        field: "job_name",
                        title: "任务名称",
                        width: '15%'
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