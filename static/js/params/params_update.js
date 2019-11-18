/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 表单验证规则
            this.form_verify();
            // 参数列表请求
            this.param_list_id();
            // 参数类型样式更改
            this.param_type_change();
            // 任务表单事件注册
            this.form_event();
        },
        // 表单验证
        form_verify: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.verify({
                    // 多选目录验证规则
                    index_verify: function (value, item) {
                        if (!value) {
                            return '必填项不能为空'
                        }
                        if (/,/.test(value)) {
                            return '任务目录中不得出现逗号字符","'
                        }
                    }
                })
            })
        },
        // 参数列表请求
        param_list_id: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.datasource.id_list_api,
                type: 'get',
                success: function (res) {
                    layui.use('form', function () {
                        // 渲染数据源列表请求
                        let form = layui.form;
                        let html = [];
                        html.push('<option value="0">请选择</option>');
                        for (let i = 0; i < res.data.length; i++) {
                            html.push('<option value="' + res.data[i].source_id + '">' + res.data[i].source_name + '</option>')
                        }
                        $('select[name=source_id]').append(html.join(''));
                        form.render('select');
                        // 参数详情请求
                        that.param_detail_request();
                    })
                }
            })
        },
        // 参数详情请求
        param_detail_request: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.params.detail_api + window.param_id + '/',
                type: 'get',
                success: function (result) {
                    if (result.status === 200) {
                        that.param_detail_init(result.data)
                    } else {
                        layer.alert('请求参数详情API异常', {icon: 5});
                    }
                }
            });
        },
        // 参数详情初始化
        param_detail_init: function (data) {
            layui.use('form', function () {
                let form = layui.form;
                form.val('param_detail', {
                    'index_name': data.index_name,
                    'param_type': data.param_type,
                    'param_name': data.param_name,
                    'param_index': data.param_index,
                    'source_id': data.source_id,
                    'param_value': data.param_value,
                    'param_desc': data.param_desc,
                    'param_mark': data.param_mark,
                    'is_deleted': data.is_deleted === 1
                });
                // 数据源选择 && 数据源SQL测试
                if (Number(data.param_type) === 1) {
                    $('select[name=source_id]').parent().parent().parent().removeAttr('style');
                    $('button[lay-filter=param-test]').removeAttr('style');
                    $('input[name=param_value]').attr('placeholder', 'SQL参数')
                } else {
                    $('select[name=source_id]').parent().parent().parent().css('display', 'none');
                    $('button[lay-filter=param-test]').css('display', 'none');
                    $('input[name=param_value]').attr('placeholder', '静态参数值')
                }
                form.render();
            });
        },
        // 参数类型样式更改
        param_type_change: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('select(param_type)', function (data) {
                    // 数据源选择 && 数据源SQL测试
                    if (Number(data.param_type) === 1) {
                        $('select[name=source_id]').parent().parent().parent().removeAttr('style');
                        $('button[lay-filter=param-test]').removeAttr('style');
                        $('input[name=param_value]').attr('placeholder', 'SQL参数')
                    } else {
                        $('select[name=source_id]').parent().parent().parent().css('display', 'none');
                        $('button[lay-filter=param-test]').css('display', 'none');
                        $('input[name=param_value]').attr('placeholder', '静态参数值')
                    }
                    form.render('select');
                });
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 参数测试
                form.on('submit(param-test)', function (data) {
                    data = data.field;
                    if (Number(data.param_type) === 1 && Number(data.source_id) === 0) {
                        layer.msg('请选择数据源', {icon: 5, shift: 6});
                        return
                    }
                    $.ajax({
                        url: BASE.uri.params.test_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg(sprintf('成功, 参数值[%s]', result.data.text), {icon: 6});
                            } else {
                                layer.alert(sprintf('测试失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.alert(sprintf('测试失败[%s]', result.msg), {icon: 5});
                        }
                    });
                });
                // 表单保存
                form.on('submit(param-update)', function (data) {
                    data = data.field;
                    // 添加菜单目录
                    data.index_id = $('input[name=index_name]').attr('value');
                    if (Number(data.param_type) === 1 && Number(data.source_id) === 0) {
                        layer.msg('请选择数据源', {icon: 5, shift: 6});
                        return
                    }
                    $.ajax({
                        url: BASE.uri.params.detail_api + window.param_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'put',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('修改成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('修改失败[%s]', result.msg), {icon: 5});
                        }
                    });
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