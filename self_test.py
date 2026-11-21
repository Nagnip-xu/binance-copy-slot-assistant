# -*- coding: utf-8 -*-
"""独立版离线自检；不联网、不启动浏览器、不提交跟单。"""
import ast
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import browser_control
import config
import engine


def check_syntax():
    for name in ('app.py', 'browser_control.py', 'cdp.py', 'config.py', 'engine.py', 'launcher.py', 'self_test.py'):
        path = os.path.join(ROOT, name)
        with open(path, 'r', encoding='utf-8') as handle:
            ast.parse(handle.read(), filename=path)


def check_config():
    normalized = config.normalize({
        'amount': '300',
        'rate_limit': 999,
        'cdp_port': '9222',
        'browser': 'EDGE',
    })
    assert normalized['amount'] == 300.0
    assert normalized['rate_limit'] == 50
    assert normalized['cdp_port'] == 9222
    assert normalized['browser'] == 'edge'
    assert normalized['auto_start'] is False


def check_submit_body():
    body = engine.build_submit_body('123456789', 300)
    assert body['leadPortfolioId'] == '123456789'
    assert body['investAmount'] == 300.0
    assert body['copyModel'] == 'FIXED_RATIO'
    assert body['mirrorMode'] == 'BETTER'
    assert body['investAsset'] == 'USDT'
    assert body['enableAutoInvest'] is False
    assert body['totalStopLossUsdt'] == 0


def check_entry_url():
    assert engine.ENTRY_ORIGIN == 'https://www.bsmkweb.cc'
    assert engine.SETTING_URL.startswith(
        'https://www.bsmkweb.cc/zh-CN/copy-trading/copy-setting'
    )
    assert 'portfolioId={trader_id}' in engine.SETTING_URL


def check_injection_rendering():
    rendered = engine.INSTALL_TEMPLATE % {
        'version': 123,
        'rate': 11,
        'workers': 6,
        'body': '{"leadPortfolioId":"123"}',
    }
    assert 'window.__copySlotRequire(26159)' in rendered
    assert 'submitModule.jT(body)' in rendered
    assert 'rateLimit: 11' in rendered
    assert 'for (var i = 0; i < 6; i++)' in rendered
    assert 'state.running = false' in rendered


def check_browser_detection():
    assert browser_control.kind_from_path(r'C:\Program Files\Microsoft\Edge\Application\msedge.exe') == 'edge'
    assert browser_control.kind_from_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe') == 'chrome'
    assert browser_control.kind_from_path(r'D:\Quark\quark.exe') == 'quark'


def check_python_bootstrap():
    bootstrap_path = os.path.join(ROOT, 'bootstrap_python.ps1')
    with open(bootstrap_path, 'rb') as handle:
        assert handle.read(3) == b'\xef\xbb\xbf'
    with open(bootstrap_path, 'r', encoding='utf-8-sig') as handle:
        bootstrap = handle.read()
    assert 'https://www.python.org/ftp/python/3.11.9/' in bootstrap
    assert 'Get-AuthenticodeSignature' in bootstrap
    assert 'Python Software Foundation' in bootstrap
    assert 'Include_tcltk=1' in bootstrap
    assert 'PrependPath=0' in bootstrap

    for name in ('START.cmd', '启动独立版.bat', '启动-调试模式.bat', '运行离线自检.bat'):
        with open(os.path.join(ROOT, name), 'rb') as handle:
            raw_source = handle.read()
        assert b'\r\n' in raw_source
        assert b'\n' not in raw_source.replace(b'\r\n', b'')
        with open(os.path.join(ROOT, name), 'r', encoding='utf-8-sig') as handle:
            source = handle.read()
        assert 'bootstrap_python.ps1' in source


def check_no_original_license_dependency():
    for name in ('app.py', 'browser_control.py', 'cdp.py', 'config.py', 'engine.py'):
        with open(os.path.join(ROOT, name), 'r', encoding='utf-8') as handle:
            source = handle.read()
        assert 'import license' not in source
        assert 'activation_ui' not in source
        assert 'TRIAL_SECONDS' not in source


def main():
    checks = [
        ('源码语法', check_syntax),
        ('安全默认配置', check_config),
        ('跟单提交参数', check_submit_body),
        ('免代理入口地址', check_entry_url),
        ('注入脚本生成', check_injection_rendering),
        ('浏览器识别', check_browser_detection),
        ('Python 自动下载引导', check_python_bootstrap),
        ('无原授权依赖', check_no_original_license_dependency),
    ]
    for label, check in checks:
        check()
        print('[通过] ' + label)
    print('独立版离线自检全部通过；未联网、未启动浏览器、未提交真实跟单。')


if __name__ == '__main__':
    main()
