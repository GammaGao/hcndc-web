/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 任务流列表请求
            this.interface_list_req();
            // 表单验证规则
            this.form_verify();
            // 表单提交
            this.form_event();
            // 日期组件渲染
            this.restart('run_time');
        },
        // 任务流列表请求
        interface_list_req: function () {
            $.ajax({
                url: BASE.uri.interface.id_list_api,
                type: 'get',
                success: function (res) {
                    let formSelects = layui.formSelects;
                    let html = [];
                    for (let i = 0; i < res.data.length; i++) {
                        html.push(sprintf(
                            '<option value="%s">%s(%s)</option>',
                            res.data[i].interface_id,
                            res.data[i].interface_id,
                            res.data[i].interface_name
                        ))
                    }
                    $('select[xm-select=parent_interface]').append(html.join(''));
                    formSelects.render('parent_interface');
                }
            })
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
                // 表单验证
                form.on('submit(interface-save)', function (data) {
                    data = data.field;
                    // 任务流表单验证
                    $.ajax({
                        url: BASE.uri.interface.add_api,
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('新增成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    let index = parent.layer.getFrameIndex(window.name);
                                    parent.layer.close(index);
                                }, 2000);
                            } else {
                                layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('新增失败[%s]', result.msg), {icon: 5});
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
        },
        // 日期组件渲染
        restart: function (field) {
            layui.use('laydate', function () {
                let laydate = layui.laydate;
                laydate.render({
                    elem: sprintf('input[name=%s]', field),
                    theme: '#393D49',
                    format: 'yyyy-MM-dd',
                    calendar: true,
                    range: false
                })
            });
        }
    };
    new Controller();
})();