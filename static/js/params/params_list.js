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
            menu_init('任务总览', '参数配置');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 参数目录渲染
            this.param_index_init();
            // 数据源ID渲染
            this.datasource_list_id();
            // 表单搜索事件
            this.form_search();
            // 表格数据初始化
            this.table_data_load({});
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
                    click: this.userLoginOut,
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
        // 参数目录渲染
        param_index_init: function () {
            $.ajax({
                url: BASE.uri.params.index_api,
                type: 'get',
                success: function (result) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    html.push('<option value="">全部</option>');
                    for (let i = 0; i < result.data.length; i++) {
                        let item = result.data[i];
                        html.push('<option value="' + item.param_index + '">' + item.param_index + '</option>')
                    }
                    $('select[xm-select=param_index]').append(html.join(''));
                    formSelects.render('param_index');
                }
            });
        },
        // 数据源ID渲染
        datasource_list_id: function () {
            $.ajax({
                url: BASE.uri.datasource.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        html.push('<option value="0">请选择</option>');
                        for (let i = 0; i < res.data.length; i++) {
                            html.push('<option value="' + res.data[i].source_id + '">' + res.data[i].source_name + '</option>')
                        }
                        $('select[name=source_id]').append(html.join(''));
                        form.render('select');
                    })
                }
            })
        },
        // 表单搜索
        form_search: function () {
            let that = this;
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(params-search)', function (data) {
                    that.table_data_load(data.field);
                });
            });
        },
        // 表格组件渲染
        table_data_load: function (data) {
            // 事件监听
            let that = this;
            // 自定义左侧工具栏
            let toolbar_div = [
                '<div class="layui-table-tool-temp">',
                '<div class="layui-inline" lay-event="add" title="添加参数"><i class="layui-icon layui-icon-add-1"></i></div>',
                '<div class="layui-inline" lay-event="update" title="修改参数"><i class="layui-icon layui-icon-edit"></i></div>',
                '<div class="layui-inline" lay-event="delete" title="删除参数"><i class="layui-icon layui-icon-delete"></i></div>',
                '<div class="layui-inline" lay-event="upload" title="上传参数文件" id="param-upload"><i class="layui-icon layui-icon-upload"></i></div>',
                '<div class="layui-inline" lay-event="download" title="下载参数模板"><i class="layui-icon layui-icon-download-circle"></i></div>',
                '</div>'
            ].join('');
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#params-list",
                    page: true,
                    toolbar: toolbar_div,
                    limits: [10, 20, 30, 40, 50],
                    title: '参数列表',
                    url: BASE.uri.params.list_api,
                    where: data,
                    cols: [[{
                        type: 'checkbox'
                    }, {
                        field: "param_id",
                        title: "参数id",
                        width: "8%",
                        sort: true
                    }, {
                        field: "param_type",
                        title: "参数类型",
                        templet: function (data) {
                            if (data.param_type === 0) {
                                return '<span class="layui-badge layui-bg-green">静态参数</span>'
                            } else if (data.param_type === 1) {
                                return '<span class="layui-badge layui-bg-blue">SQL参数</span>';
                            } else if (data.param_type === 2) {
                                return '<span class="layui-badge layui-bg-cyan">上下文参数</span>';
                            } else {
                                return '<span class="layui-badge layui-bg-gray">未知</span>';
                            }
                        }
                    }, {
                        field: "param_name",
                        title: "参数名称"
                    }, {
                        field: "param_value",
                        title: "参数值"
                    }, {
                        field: "param_index",
                        title: "参数目录"
                    }, {
                        field: "source_name",
                        title: "数据源名称",
                        templet: function (data) {
                            if (data.source_name === null) {
                                return '-'
                            } else {
                                return data.source_name;
                            }
                        }
                    }, {
                        field: "is_deleted",
                        title: "是否失效",
                        width: "8%",
                        sort: true,
                        templet: function (data) {
                            if (data.is_deleted === 0) {
                                return '<span class="layui-badge layui-bg-green">正常</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-gray">失效</span>';
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            // [上下文参数]不可修改, 删除
                            if (data.param_type === 0 || data.param_type === 1) {
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                            }
                            html.push('</div>');
                            return html.join('');
                        }
                    }]],
                    response: {
                        statusName: 'status',
                        statusCode: 200,
                        countName: 'total'
                    }
                });
                // 工具栏事件监听
                that.toolbar_data_event();
                // 自定义事件监听
                that.table_data_event();
            });
        },
        // 工具栏事件监听
        toolbar_data_event: function () {
            // 上传事件注册
            layui.use('upload', function () {
                let upload = layui.upload;
                // 允许上传的文件后缀
                upload.render({
                    elem: '#param-upload',
                    url: '/params/upload/',
                    // 普通文件
                    accept: 'file',
                    auto: false,
                    // 只允许上传压缩文件
                    exts: 'xlsx|xls|csv',
                    // 限制文件大小，单位 KB
                    size: 5000,
                    choose: function (obj) {
                        //确认框
                        layer.confirm('确定上传文件吗？', {icon: 3, title: '提示'}, function (index) {
                            // 读取本地文件
                            obj.preview(function (index, file) {
                                // 单个重传
                                obj.upload(index, file);
                            });
                            layer.close(index);
                        });
                    },
                    done: function (res) {
                        // 成功上传
                        if (res.status && res.status === 200) {
                            layer.msg("成功", {icon: 6});
                        }
                        // 上传参数错误
                        else if (res.status && res.status === 401) {
                            let err_msg = res.data.err_msg;
                            let msg = err_msg.join('</br>');
                            layer.alert(msg, {icon: 5, shift: 6});
                        }
                        // 文件类型错误
                        else {
                            layer.alert(res.msg);
                        }
                    },
                    error: function (error) {
                        let result = error.responseJSON;
                        layer.alert(result.msg)
                    }
                });
            });
            // 工具栏事件注册
            layui.use('table', function () {
                let table = layui.table;
                table.on('toolbar(params-list)', function (obj) {
                    // 工具栏事件监听
                    let check_status = table.checkStatus(obj.config.id);
                    console.log(check_status);
                    let check_data = check_status.data;
                    switch (obj.event) {
                        // 新增
                        case 'add':
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '新增参数页面',
                                maxmin: true, //开启最大化最小化按钮
                                area: ['60%', '80%'],
                                content: BASE.uri.params.add,
                                end: function (index) {
                                    $(".layui-laypage-btn").click();
                                    layer.close(index);
                                }
                            });
                            break;
                        // 修改
                        case 'update':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行', {icon: 5, shift: 6});
                            } else if (check_data.length > 1) {
                                layer.msg('只能同时编辑一个', {icon: 5, shift: 6})
                            } else {
                                let data = check_data[0];
                                // 判断可编辑状态
                                if (data.param_type === 2) {
                                    layer.msg('[上下文参数]不可删改', {icon: 5, shift: 6});
                                    return
                                }
                                layer.open({
                                    type: 2,
                                    anim: 5,
                                    title: '修改参数页面',
                                    maxmin: true, //开启最大化最小化按钮
                                    area: ['60%', '80%'],
                                    content: BASE.uri.params.update + check_data[0].param_id + '/',
                                    end: function (index) {
                                        $(".layui-laypage-btn").click();
                                        layer.close(index);
                                    }
                                });
                            }
                            break;
                        // 删除
                        case 'delete':
                            if (check_data.length === 0) {
                                layer.msg('请选择一行');
                            } else {
                                let param_id_arr = [];
                                check_data.forEach(item => param_id_arr.push(item.param_id));
                                layer.confirm('确定删除参数?', function (index) {
                                    layer.close(index);
                                    $.ajax({
                                        url: BASE.uri.params.action_api,
                                        data: JSON.stringify({param_id_arr: param_id_arr}),
                                        contentType: "application/json; charset=utf-8",
                                        type: 'delete',
                                        success: function (result) {
                                            if (result.status === 200) {
                                                layer.open({
                                                    title: '删除成功',
                                                    content: '删除成功',
                                                    yes: function (index) {
                                                        // 刷新页面
                                                        $(".layui-laypage-btn").click();
                                                        layer.close(index);
                                                    }
                                                })
                                            } else {
                                                layer.alert(sprintf('删除失败: [%s]', result.msg), {
                                                    icon: 5,
                                                    shift: 6,
                                                    end: function (index) {
                                                        layer.close(index);
                                                    }
                                                });
                                            }
                                        },
                                        error: function (error) {
                                            let result = error.responseJSON;
                                            layer.msg(sprintf('删除失败[%s]', result.msg), {
                                                icon: 5,
                                                shift: 6,
                                                end: function () {
                                                    layer.close(index);
                                                }
                                            });
                                        }
                                    });
                                });
                            }
                            break;
                        // 下载
                        case 'download':
                            window.location.href = '/params/download/';
                    }
                })
            })
        },
        // 表格事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                table.on('tool(params-list)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    switch (event) {
                        // 修改
                        case 'update':
                            // 判断可编辑状态
                            if (data.param_type === 2) {
                                layer.msg('该参数不可删改', {icon: 5, shift: 6});
                                return
                            }
                            layer.open({
                                type: 2,
                                anim: 5,
                                title: '修改参数页面',
                                maxmin: true, //开启最大化最小化按钮
                                area: ['60%', '80%'],
                                content: BASE.uri.params.update + data.param_id + '/',
                                end: function (index) {
                                    $(".layui-laypage-btn").click();
                                    layer.close(index);
                                }
                            });
                            break;
                        // 删除
                        case 'delete':
                            if (data.is_deleted !== 0) {
                                layer.alert('项目已失效');
                                return
                            }
                            layer.confirm('确定删除?', function (index) {
                                // 关闭弹窗
                                layer.close(index);
                                $.ajax({
                                    url: BASE.uri.params.detail_api + data.param_id + '/',
                                    type: 'delete',
                                    success: function (result) {
                                        if (result.status === 200) {
                                            layer.msg('删除成功', {icon: 6});
                                            $(".layui-laypage-btn").click();
                                        } else {
                                            layer.alert(sprintf('删除失败: [%s]', result.msg), {
                                                icon: 5,
                                                shift: 6,
                                                end: function () {
                                                    $(".layui-laypage-btn").click();
                                                }
                                            });
                                        }
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.alert(sprintf('删除项目失败: %s', result.msg), {
                                            icon: 5,
                                            shift: 6,
                                            end: function () {
                                                $(".layui-laypage-btn").click();
                                            }
                                        })
                                    }
                                });
                            });
                            break;
                    }
                })
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
            let today = new Date().Format("yyyy-MM-dd");
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    max: today,
                    theme: '#393D49',
                    calendar: true,
                    range: true
                })
            });
        }
    };
    new Controller();
})();