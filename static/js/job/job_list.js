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
            menu_init('任务总览', '任务列表');
            // 侧边栏样式切换
            this.tree_toggle();
            // 用户数据渲染
            this.user_info();
            // 元素事件注册
            this.element_event();
            // 接口ID渲染
            this.interface_list_id();
            // 表单搜索事件
            this.form_search();
            // 表格数据初始化
            this.table_data_load({});
            // 文件上传组件
            this.file_upload();
            // UI组件渲染
            this.restart('job_date');
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
        // 接口ID渲染
        interface_list_id: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        let form = layui.form;
                        let html = [];
                        html.push('<option value="0">请选择</option>');
                        for (let i in res.data) {
                            html.push('<option value="' + res.data[i].interface_id + '">' + res.data[i].interface_name + '</option>')
                        }
                        $('select[name=interface_id]').append(html.join(''));
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
                form.on('submit(job-search)', function (data) {
                    let job_date_list = data.field.job_date.split(' - ');
                    if (job_date_list.length === 2) {
                        let start_time = job_date_list[0] + ' 00:00:00';
                        data.field.start_time = new Date(start_time).getTime() / 1000;
                        let end_time = job_date_list[1] + ' 23:59:59';
                        data.field.end_time = new Date(end_time).getTime() / 1000;
                    } else {
                        data.field.start_time = 0;
                        data.field.end_time = 0;
                    }
                    delete data.field.job_date;
                    that.table_data_load(data.field);
                });
            });
        },
        // 表格组件渲染
        table_data_load: function (data) {
            // 事件监听
            let that = this;
            // 表头
            // let toolbar = ['<div class="layui-table-tool-temp">',
            //     '<div class="layui-inline" lay-event="add" title="添加">',
            //     '<i class="layui-icon layui-icon-add-1"></i>',
            //     '</div>',
            //     '<div class="layui-inline" lay-event="update" title="修改">',
            //     '<i class="layui-icon layui-icon-edit"></i>',
            //     '</div>',
            //     '<div class="layui-inline" lay-event="delete" title="删除">',
            //     '<i class="layui-icon layui-icon-delete"></i></div>',
            //     '</div>'
            // ];
            // 表格渲染
            layui.use('table', function () {
                let table = layui.table;
                table.render({
                    elem: "#job-list",
                    page: true,
                    // toolbar: toolbar.join(''),
                    toolbar: true,
                    limits: [10, 20, 30, 40, 50],
                    title: '任务列表',
                    url: BASE.uri.job.list_api,
                    where: data,
                    cols: [[{
                        field: "job_id",
                        title: "任务id",
                        width: "5%",
                        sort: true
                    }, {
                        field: "interface_id",
                        title: "接口id",
                        width: "5%"
                    }, {
                        field: "job_name",
                        title: "任务名称"
                    }, {
                        field: "job_desc",
                        title: "任务描述"
                    }, {
                        field: "server_id",
                        title: "服务器id",
                        width: "5%"
                    }, {
                        field: "server_dir",
                        title: "脚本目录"
                    }, {
                        field: "server_script",
                        title: "脚本命令"
                    }, {
                        field: "is_deleted",
                        title: "是否失效",
                        width: "8%",
                        sort: true,
                        templet: function (data) {
                            if (data.is_deleted === 0) {
                                return '<span class="layui-badge layui-bg-green">正常</span>'
                            } else {
                                return '<span class="layui-badge layui-bg-gray">删除</span>';
                            }
                        }
                    }, {
                        field: "operation",
                        title: "操作",
                        templet: function (data) {
                            let html = [];
                            html.push('<div class="layui-btn-group">');
                            if (data.is_deleted === 0) {
                                html.push('<button class="layui-btn layui-btn-sm" lay-event="detail">详情</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-danger layui-btn-sm" lay-event="delete">删除</button>');
                                html.push('<button class="layui-btn layui-btn-normal layui-btn-sm" lay-event="run">立即执行</button>');
                            } else {
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">详情</button>');
                                html.push('<button class="layui-btn layui-btn-warm layui-btn-sm" lay-event="update">修改</button>');
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">删除</button>');
                                html.push('<button class="layui-btn layui-btn-disabled layui-btn-sm" disabled="disabled">立即执行</button>');
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
                // 事件监听
                that.table_data_event();
            });
        },
        // 文件上传组件
        file_upload: function () {
            layui.use('upload', function () {
                let upload = layui.upload;
                // 允许上传的文件后缀
                upload.render({
                    elem: '#test4',
                    url: '/job/upload/',
                    // 普通文件
                    accept: 'file',
                    // 只允许上传压缩文件
                    exts: 'xlsx|xls|csv',
                    done: function (res) {
                        console.log(res)
                    }
                });
            })
        },
        // 表格事件监听
        table_data_event: function () {
            layui.use('table', function () {
                let table = layui.table;
                // 工具栏事件
                // table.on('toolbar(job-list)', function(obj){
                //     checkStatus = table.checkStatus(obj.config.id);
                //     data = checkStatus.data;
                //     console.execute(obj);
                //     console.execute(checkStatus);
                // });
                table.on('tool(job-list)', function (obj) {
                    let data = obj.data;
                    let event = obj.event;
                    let tr = obj.tr;
                    switch (event) {
                        // 详情
                        case 'detail':
                            window.location.href = BASE.uri.job.detail + data.job_id + '/';
                            break;
                        // 修改
                        case 'update':
                            window.location.href = BASE.uri.job.update + data.job_id + '/';
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
                                    url: BASE.uri.job.detail_api + data.job_id + '/',
                                    type: 'delete',
                                    success: function () {
                                        layer.alert('删除成功');
                                        tr.find('td[data-field="is_deleted"] div').html('<span class="layui-badge layui-bg-gray">删除</span>');
                                        tr.find('td[data-field="run"] div').html('<button class="layui-btn layui-btn-disabled layui-btn-xs" disabled="disabled">立即执行</button>');
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.alert(sprintf('删除项目%s失败: %s', data.job_id, result.msg))
                                    }
                                });
                            });
                            break;
                        // 执行
                        case 'run':
                            if (data.is_deleted !== 0) {
                                layer.alert('项目已失效');
                                return
                            }
                            layer.confirm('确定执行任务?', function (index) {
                                // 关闭弹窗
                                layer.close(index);
                                $.ajax({
                                    url: BASE.uri.job.run_api,
                                    contentType: "application/json; charset=utf-8",
                                    type: 'post',
                                    data: JSON.stringify({'job_id': data.job_id}),
                                    success: function () {
                                        layer.open({
                                            id: 'job_run_success',
                                            btn: ['跳转', '留在本页'],
                                            title: '立即执行任务成功',
                                            content: '是否跳转至执行日志?',
                                            yes: function (index) {
                                                layer.close(index);
                                                window.location.href = BASE.uri.execute.list;
                                            }
                                        });
                                    },
                                    error: function (error) {
                                        let result = error.responseJSON;
                                        layer.open({
                                            id: 'job_run_error',
                                            title: '立即执行任务失败',
                                            content: sprintf('%s', result.msg)
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