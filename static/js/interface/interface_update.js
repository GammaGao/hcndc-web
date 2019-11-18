/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 表单验证规则
            this.form_verify();
            // 数据初始化赋值
            this.form_data_init();
            // 表单提交
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
                            return '任务流目录中不得出现逗号字符","'
                        }
                    }
                })
            })
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(interface-save)', function (data) {
                    data = data.field;
                    $.ajax({
                        url: BASE.uri.interface.detail_api + window.interface_id + '/',
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
        // 数据初始化赋值
        form_data_init: function () {
            $.ajax({
                url: BASE.uri.interface.detail_api + window.interface_id + '/',
                type: 'get',
                success: function (result) {
                    let data = result.data.detail;
                    layui.use('form', function () {
                        let form = layui.form;
                        form.val('interface_detail', {
                            'interface_name': data.interface_name,
                            'interface_desc': data.interface_desc,
                            'interface_index': data.interface_index,
                            'retry': data.retry,
                            'is_deleted': data.is_deleted === 1
                        });
                        form.render();
                    })
                }
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