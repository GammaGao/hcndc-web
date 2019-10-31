/**
 * Created by xx on 2018/12/18.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 参数菜单请求
            this.tree_index_request();
            // 任务表单事件注册
            this.form_event();
        },
        // 参数菜单请求
        tree_index_request: function () {
            let that = this;
            $.ajax({
                url: BASE.uri.params_index.list_api,
                type: 'get',
                success: function (result) {
                    layui.use('tree', function () {
                        let tree = layui.tree;
                        tree.render({
                            id: 'id',
                            elem: '#param_index_tree',
                            data: [result.data],
                            onlyIconControl: true,
                            accordion: true,
                            showCheckbox: true,
                            oncheck: function (obj) {
                                // 更改表单数据
                                $('input[name=parent_name]').attr('value', obj.data.id);
                                $('input[name=parent_name]').attr('mark', obj.data.mark);
                                $('input[name=parent_name]').val(obj.data.title);
                            }
                        })
                    })
                }
            });
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                // 表单保存
                form.on('submit(param-save)', function (data) {
                    data = data.field;
                    let parent_mark = $('input[name=parent_name]').attr('mark');
                    if (Number(parent_mark) === 1) {
                        layer.alert('该目录下禁止新建子目录', {icon: 5});
                        return
                    }
                    // 添加菜单目录
                    data.parent_id = $('input[name=parent_name]').attr('value');
                    if (Number(data.param_type) === 1 && Number(data.source_id) === 0) {
                        layer.msg('请选择数据源', {icon: 5, shift: 6});
                        return
                    }
                    $.ajax({
                        url: BASE.uri.params_index.add_api,
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
        }
    };
    new Controller();
})();