/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        // Tab切换事件
        this.tab_change_event();
        // 任务依赖svg渲染
        this.job_prep_init();
        // 局部-任务流依赖svg渲染
        // this.local_interface_init();
        // // 全局-任务流依赖svg渲染
        // this.global_interface_init();
    };

    Controller.prototype = {
        // Tab切换事件
        tab_change_event: function () {
            let that = this;
            layui.use(['element'], function () {
                let element = layui.element;
                element.on('tab(detail-tab)', function (data) {
                    if (data.index === 0 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 任务依赖svg渲染
                        return that.job_prep_init();
                    } else if (data.index === 1 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 局部-任务流依赖svg渲染
                        return that.local_interface_init();
                    } else if (data.index === 2 && this.getAttribute('data-load') === '0') {
                        this.setAttribute('data-load', '1');
                        // 全局-任务流依赖svg渲染
                        return that.global_interface_init();
                    }
                });
            });
        },
        // 任务依赖svg渲染
        job_prep_init: function () {
            $.ajax({
                url: BASE.uri.interface.graph_api + window.interface_id + '/',
                data: {graph_type: 1},
                type: 'get',
                success: function (response) {
                    let dom = document.getElementById('svg-div');
                    let myChart = echarts.init(dom, 'default');
                    // myChart.hideLoading();

                    let graph = response.data;
                    let categories = graph.categories;

                    let option = {
                        title: {
                            text: '任务流任务依赖',
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
        // 局部-任务流依赖svg渲染
        local_interface_init: function () {
            $.ajax({
                url: BASE.uri.interface.graph_api + window.interface_id + '/',
                data: {graph_type: 2},
                type: 'get',
                success: function (response) {
                    let dom = document.getElementById('local-graph');
                    let myChart = echarts.init(dom, 'default');
                    // let myChart = echarts.init(dom, 'light');
                    // myChart.hideLoading();

                    let graph = response.data;
                    let categories = graph.categories;

                    let option = {
                        title: {
                            text: '局部-任务流依赖',
                            subtext: '默认布局',
                            top: 'top',
                            left: 'right'
                        },
                        tooltip: {formatter: '任务流: {b}'},
                        legend: [{
                            type: 'scroll',
                            left: 30,
                            orient: 'vertical',
                            data: categories.map(function (a) {
                                return a.name;
                            })
                        }],
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
        // 全局-任务流依赖svg渲染
        global_interface_init: function () {
            $.ajax({
                url: BASE.uri.interface.graph_api + window.interface_id + '/',
                data: {graph_type: 3},
                type: 'get',
                success: function (response) {
                    let dom = document.getElementById('global-graph');
                    let myChart = echarts.init(dom, 'default');
                    // let myChart = echarts.init(dom, 'light');
                    // myChart.hideLoading();

                    let graph = response.data;
                    let categories = graph.categories;

                    let option = {
                        title: {
                            text: '全局-任务流依赖',
                            subtext: '默认布局',
                            top: 'top',
                            left: 'right'
                        },
                        tooltip: {formatter: '任务流: {b}'},
                        legend: [{
                            type: 'scroll',
                            left: 30,
                            orient: 'vertical',
                            data: categories.map(function (a) {
                                return a.name;
                            })
                        }],
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