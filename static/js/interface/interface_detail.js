/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 菜单样式加载
            menu_init('任务总览', '');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 任务依赖svg渲染
            this.job_prep_init();
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
        // 任务列表渲染
        job_list_init: function () {
            $.ajax({
                url: BASE.uri.job.id_list_api,
                type: 'get',
                data: {'interface_id': window.interface_id},
                success: function (res) {
                    let data = res.data;
                    layui.use('form', function () {
                        // 内容渲染
                        let form = layui.form;
                        let html = [];
                        for (let i in data) {
                            html.push(sprintf(
                                '<option value="%s">%s</option>',
                                data[i].job_name,
                                data[i].job_name
                            ))
                        }
                        $('select[name="job-list"]').append(html.join(''));
                        form.render('select');
                        // 点击事件监听
                        form.on('select(job-list)', function (data) {
                            // 清除已有样式
                            $('rect').css({'stroke-width': 1, 'stroke': '#CCC'});
                            // 新增选中样式
                            let $svg_text = $("text:contains('" + data.value + "')");
                            for (let i = 0; i < $svg_text.length; i++) {
                                if ($svg_text.eq(i).html() === data.value) {
                                    $svg_text.eq(i).prev().css({'stroke-width': 3, 'stroke': '#39b3d7'});
                                    break
                                }
                            }
                        });
                    });
                },
                error: function (error) {
                    let result = error.responseJSON;
                    layer.alert(sprintf('任务列表渲染失败: %s', result.msg))
                }
            })
        },
        // 任务依赖svg渲染
        job_prep_init: function () {
            $.ajax({
                url: BASE.uri.interface.graph_api + window.interface_id + '/',
                type: 'get',
                success: function (response) {
                    dom = document.getElementById('svg-div');
                    myChart = echarts.init(dom, 'light');
                    myChart.hideLoading();

                    graph = response.data;
                    categories = graph.categories;

                    option = {
                        title: {
                            text: '接口任务依赖',
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