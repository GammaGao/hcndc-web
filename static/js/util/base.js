/**
 * Created by xx on 2018/10/19.
 */
// 字符串模板替换
let sprintf = function (str) {
    let args = arguments,
        flag = true,
        i = 1;

    str = str.replace(/%s/g, function () {
        let arg = args[i++];

        if (typeof arg === 'undefined') {
            flag = false;
            return '';
        }
        return arg;
    });
    return flag ? str : '';
};

// 日期格式化
Date.prototype.Format = function (fmt) {
    let o = {
        // 月
        "M+": this.getMonth() + 1,
        // 日
        "d+": this.getDate(),
        // 时
        "h+": this.getHours(),
        // 分
        "m+": this.getMinutes(),
        // 秒
        "s+": this.getSeconds(),
        // 季度
        "q+": Math.floor((this.getMonth() + 3) / 3),
        // 毫秒
        "S": this.getMilliseconds()
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (let k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
};

let BASE = {
    uri: {
        login: '/login/',
        login_api: '/login/api/',
        user_api: '/user/api/',
        user_menu_api: '/user/menu/api/',
        index: '/index/',
        interface: {
            'list': '/interface/',
            'list_api': '/interface/list/api/',
            'detail': '/interface/detail/',
            'detail_api': '/interface/detail/api/',
            'action_api': '/interface/action/api/',
            'update': '/interface/update/',
            'add': '/interface/add/',
            'add_api': '/interface/add/api/',
            'id_list_api': '/interface/id/list/api/',
            'graph_api': '/interface/graph/api/',
            'index_api': '/interface/index/api/'
        },
        job: {
            'list': '/job/',
            'list_api': '/job/list/api/',
            'detail': '/job/detail/',
            'detail_api': '/job/detail/api/',
            'action_api': '/job/action/api/',
            'update': '/job/update/',
            'add': '/job/add/',
            'add_api': '/job/add/api/',
            'id_list_api': '/job/list/all/api/',
            'run_api': '/job/run/api/',
            'index_api': '/job/index/api/'
        },
        dispatch: {
            'list': '/dispatch/',
            'search': '/dispatch/search/',
            'list_api': '/dispatch/list/api/',
            'detail': '/dispatch/detail/',
            'detail_api': '/dispatch/detail/api/',
            'action_api': '/dispatch/action/api/',
            'update': '/dispatch/update/',
            'add': '/dispatch/add/',
            'add_api': '/dispatch/add/api/',
            'alert_add_api': '/dispatch/alert/add/api/',
            'alert_detail_api': '/dispatch/alert/detail/api/',
            'run_api': '/dispatch/run/api/',
            'run': '/dispatch/run/'
        },
        execute: {
            'job': '/execute/job/',
            'job_api': '/execute/job/api/',
            'job_history': '/execute/job/history/',
            'job_history_api': '/execute/job/history/api/',
            'flow': '/execute/flow/',
            'flow_api': '/execute/flow/api/',
            'history': '/execute/flow/history/',
            'history_api': '/execute/flow/history/api/',
            'detail': '/execute/flow/detail/',
            'detail_api': '/execute/flow/detail/api/',
            'action_api': '/execute/action/api/',
            'log': '/execute/job/log/',
            'log_api': '/execute/job/log/api/',
            'graph_api': '/execute/graph/api/',
            'restart': '/execute/restart/',
            'interface_list_api': '/execute/interface/list/api/'
        },
        base: {
            'exec_list': '/base/',
            'exec_host_api': '/base/exec/host/list/api/',
            'exec_host_update': '/base/exec/host/update/',
            'exec_host_detail_api': '/base/exec/host/detail/api/',
            'exec_host_add': '/base/exec/host/add/',
            'exec_host_test_api': '/base/exec/host/test/api/',
            'exec_host_add_api': '/base/exec/host/add/api/',
            'exec_host_status_api': '/base/exec/host/status/list/api/',
            'alert_list': '/base/alert/',
            'alert_list_api': '/base/alert/list/api/',
            'alert_list_all_api': '/base/alert/list/all/api/',
            'alert_update_api': '/base/alert/update/',
            'alert_detail_api': '/base/alert/detail/api/',
            'alert_add': '/base/alert/add/',
            'alert_add_api': '/base/alert/add/api/'
        },
        datasource: {
            'list': '/datasource/',
            'list_api': '/datasource/list/api/',
            'test_api': '/datasource/test/api/',
            'add': '/datasource/add/',
            'add_api': '/datasource/add/api/',
            'update': '/datasource/update/',
            'detail_api': '/datasource/detail/api/',
            'id_list_api': '/datasource/list/all/api/'
        },
        ftp: {
            'list': '/ftp/',
            'list_api': '/ftp/list/api/',
            'test_api': '/ftp/test/api/',
            'add': '/ftp/add/',
            'add_api': '/ftp/add/api/',
            'update': '/ftp/update/',
            'detail_api': '/ftp/detail/api/',
            'id_list_api': '/ftp/list/all/api/'
        },
        ftp_event: {
            'list': '/ftp_event/',
            'list_api': '/ftp_event/list/api/',
            'detail': '/ftp_event/detail/',
            'detail_api': '/ftp_event/detail/api/',
            'action_api': '/ftp_event/action/api/',
            'update': '/ftp/event/update/',
            'add': '/ftp/event/add/',
            'add_api': '/ftp_event/add/api/',
            'alert_add_api': '/ftp_event/alert/add/api/',
            'alert_detail_api': '/ftp_event/alert/detail/api/',
            'run_api': '/ftp_event/run/api/',
            'run': '/ftp_event/run/'
        },
        params: {
            'list': '/params/',
            'list_api': '/params/list/api/',
            'add': '/params/add',
            'add_api': '/params/add/api/',
            'action_api': '/params/action/api/',
            'update': '/params/update/',
            'detail_api': '/params/detail/api/',
            'test_api': '/params/test/api/',
            'id_list_api': '/params/list/all/api/',
            'index_api': '/params/index/api/'
        },
        params_index: {
            'list_api': '/params_index/list/api/',
            'add': '/params_index/add/',
            'add_api': '/params_index/add/api/',
            'detail_api': '/params_index/detail/api/'
        },
        flow_alert_detail_api: '/flow/alert/api/',
        flow_list_api: '/flow/list/api/',
        flow_detail: '/flow/detail/',
        flow_update: '/flow/update/',
        flow_detail_api: '/flow/detail/api/',
        flow_add_api: '/flow/add/api/',
        flow_job_api: '/flow/job/api/'
    },
    item: [{
        'name': '任务流配置',
        'icon': '',
        'children': [{
            'name': ' 任务流列表',
            'uri': '/interface/',
            'icon': 'layui-icon layui-icon-template-1'
        }, {
            'name': ' 新增任务流',
            'uri': '/interface/add/',
            'icon': 'layui-icon layui-icon-add-circle'
        }]
    }, {
        'name': '任务配置',
        'icon': '',
        'children': [{
            'name': ' 任务列表',
            'uri': '/job/',
            'icon': 'layui-icon layui-icon-list'
        }, {
            'name': ' 新增任务',
            'uri': '/job/add/',
            'icon': 'layui-icon layui-icon-add-circle'
        }]
    }],
    dispatch: [{
        'name': '调度配置',
        'icon': '',
        'children': [{
            'name': ' 调度列表',
            'uri': '/dispatch/',
            'icon': 'layui-icon layui-icon-senior'
        }, {
            'name': ' 新增调度',
            'uri': '/dispatch/add/',
            'icon': 'layui-icon layui-icon-add-circle'
        }]
    }, {
        'name': '运行日志',
        'icon': '',
        'children': [{
            'name': ' 任务流日志',
            'uri': '/execute/list/',
            'icon': 'layui-icon layui-icon-file'
        }]
    }],
    base: [{
        'name': '执行服务器配置',
        'icon': '',
        'children': [{
            'name': ' 执行服务器列表',
            'uri': '/base/',
            'icon': 'layui-icon layui-icon-list'
        }, {
            'name': ' 新增执行服务器',
            'uri': '/base/exec/host/add/',
            'icon': 'layui-icon layui-icon-add-circle'
        }]
    }, {
        'name': '预警配置',
        'icon': '',
        'children': [{
            'name': ' 预警配置列表',
            'uri': '/base/alert/',
            'icon': 'layui-icon layui-icon-list'
        }, {
            'name': ' 新增预警配置',
            'uri': '/base/alert/add/',
            'icon': 'layui-icon layui-icon-add-circle'
        }]
    }]
};

let remakes = {
    'ready': '等待依赖任务完成',
    'preparing': '待运行',
    'running': '运行中',
    'succeeded': '成功',
    'failed': '失败'
};

// 初始化菜单栏
let menu_init = function (navbar_name, sidebar_name) {
    $.ajax({
        url: BASE.uri.user_menu_api,
        type: 'get',
        success: function (result) {
            // 初始化导航栏
            navbar_init(navbar_name, result);
            // 初始化侧边栏
            sidebar_init(navbar_name, sidebar_name, result);
        }
    });
};

// 初始化导航栏
let navbar_init = function (navbar_name, result) {
    if (result.status !== 200) {
        layer.alert('请重新登陆');
    } else {
        result.data.menu.forEach(function (element) {
            let item = sprintf('<li class="layui-nav-item"><a href="%s">%s</a></li>', element.url, element.menu_name);
            $('.layui-nav.layui-layout-left').append(item);
        })
    }
    // 更改当前样式
    if (navbar_name) {
        $('.layui-nav.layui-layout-left').children().each(function () {
            if ($(this).text().replace(/\s+/g, "") === navbar_name) {
                $(this).addClass('layui-this')
            }
        })
    }
};

// 初始化侧边栏
let sidebar_init = function (navbar_name, sidebar_name, result) {
    for (let k = 0; k < result.data.menu.length; k++) {
        // 获取该导航栏下菜单
        let menu = result.data.menu[k];
        if (navbar_name !== '' && menu.menu_name === navbar_name) {
            let html = [];
            for (let i = 0; i < menu.children.length; i++) {
                let items = menu.children[i];
                // 二级菜单
                if (items['url']) {
                    // 当前选中样式
                    if (sidebar_name === items['menu_name'].replace(/\s+/g, "")) {
                        html.push('<li class="layui-nav-item layui-this">');
                    } else {
                        html.push('<li class="layui-nav-item">');
                    }
                    html.push('<a href="', items['url'], '">');
                    html.push('<i class="', items['icon'], ' icon-size-medium"></i>');
                    html.push('<span > ', items['menu_name'], '</span>');
                    html.push('</a></li>');
                }
                // 一级菜单
                else {
                    html.push('<li class="layui-nav-item layui-nav-itemed">');
                    html.push('<a href="#">');
                    html.push('<i class="', items['icon'], ' icon-size-medium"></i>');
                    html.push('<span > ', items['menu_name'], '</span>');
                    html.push('</a>');
                    html.push('<dl class="layui-nav-child">');
                    // 二级菜单
                    for (let j = 0; j < items['children'].length; j++) {
                        let child_item = items['children'][j];
                        // 当前选中样式
                        if (sidebar_name === child_item['menu_name'].replace(/\s+/g, "")) {
                            html.push('<dd class="layui-this"><a href="', child_item['url'], '">');
                        } else {
                            html.push('<dd><a href="', child_item['url'], '">');
                        }
                        if (!!child_item['icon']) {
                            html.push('<i class="', child_item['icon'], '"></i>');
                        }
                        html.push('<span > ', child_item['menu_name'], '</span></a></dd>');
                    }
                    html.push('</dl></li>');
                }
            }
            $('ul[lay-filter=tree]').html(html.join(''));
            break
        }
    }
};