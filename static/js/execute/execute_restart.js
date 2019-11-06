/**
 * Created by xx on 2018/11/14.
 */
(function () {
    let Controller = function () {
        this.init();
    };

    Controller.prototype = {
        init: function () {
            // 表单提交
            this.form_event();
        },
        // 表单提交
        form_event: function () {
            layui.use('form', function () {
                let form = layui.form;
                form.on('submit(restart-save)', function (data) {
                    data = data.field;
                    data.prepose_rely  = data.prepose_rely || 0;
                    $.ajax({
                        url: BASE.uri.execute.detail_api + window.exec_id + '/',
                        contentType: "application/json; charset=utf-8",
                        type: 'post',
                        data: JSON.stringify(data),
                        success: function (result) {
                            if (result.status === 200) {
                                layer.msg('重跑成功', {icon: 6});
                                // 关闭自身iframe窗口
                                setTimeout(function () {
                                    window.location.reload();
                                }, 2000);
                            } else {
                                layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5});
                            }
                        },
                        error: function (error) {
                            let result = error.responseJSON;
                            layer.msg(sprintf('重跑失败[%s]', result.msg), {icon: 5});
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