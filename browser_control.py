# -*- coding: utf-8 -*-
"""浏览器发现、启动及本机调试端口管理。"""
import json
import os
import subprocess
import time
import urllib.request

from config import APP_DIR
from cdp import CDPClient


BROWSER_LABELS = {
    'edge': 'Edge',
    'chrome': 'Chrome',
    'quark': '夸克',
    'auto': '自动',
    'custom': '自定义浏览器',
}

EXECUTABLE_NAMES = {
    'edge': 'msedge.exe',
    'chrome': 'chrome.exe',
    'quark': 'quark.exe',
}


def kind_from_path(path):
    name = os.path.basename(path or '').lower()
    if 'msedge' in name or name == 'edge.exe':
        return 'edge'
    if 'chrome' in name:
        return 'chrome'
    if 'quark' in name:
        return 'quark'
    return 'custom'


def _candidate_paths():
    local = os.environ.get('LOCALAPPDATA', '')
    pf = os.environ.get('ProgramFiles', r'C:\Program Files')
    pf86 = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
    return {
        'edge': [
            os.path.join(pf86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(pf, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        ],
        'chrome': [
            os.path.join(pf, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(pf86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(local, 'Google', 'Chrome', 'Application', 'chrome.exe'),
        ],
        'quark': [
            os.path.join(local, 'Programs', 'Quark', 'quark.exe'),
            os.path.join(pf, 'Quark', 'quark.exe'),
            os.path.join(pf86, 'Quark', 'quark.exe'),
            os.path.join(pf, 'QuarkBrowser', 'quark.exe'),
        ],
    }


def _registry_path(executable_name):
    if not executable_name:
        return None
    try:
        import winreg
        keys = [
            'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\' + executable_name,
            'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths\\' + executable_name,
        ]
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for key_name in keys:
                try:
                    with winreg.OpenKey(hive, key_name) as key:
                        value, _ = winreg.QueryValueEx(key, '')
                    if value and os.path.isfile(value):
                        return value
                except OSError:
                    continue
    except Exception:
        pass
    return None


def find_browser(cfg):
    manual = str(cfg.get('browser_exe') or '').strip()
    if manual and os.path.isfile(manual):
        return kind_from_path(manual), manual
    wanted = str(cfg.get('browser') or 'edge').lower()
    order = ['edge', 'chrome', 'quark'] if wanted == 'auto' else [wanted] + [
        item for item in ('edge', 'chrome', 'quark') if item != wanted
    ]
    candidates = _candidate_paths()
    for kind in order:
        for path in candidates.get(kind, []):
            if path and os.path.isfile(path):
                return kind, path
        registered = _registry_path(EXECUTABLE_NAMES.get(kind, ''))
        if registered:
            return kind, registered
    return None, None


def profile_dir(kind):
    base = os.environ.get('LOCALAPPDATA') or APP_DIR
    path = os.path.join(base, 'BinanceCopySlotIndependent', 'profile_' + kind)
    os.makedirs(path, exist_ok=True)
    return path


def browser_args(kind, port):
    args = [
        '--remote-debugging-address=127.0.0.1',
        '--remote-debugging-port=%d' % int(port),
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--no-first-run',
    ]
    if kind != 'quark':
        args.extend([
            '--user-data-dir=' + profile_dir(kind),
            '--no-default-browser-check',
        ])
    return args


def _json_url(port, path, timeout=4):
    with urllib.request.urlopen('http://127.0.0.1:%d%s' % (int(port), path), timeout=timeout) as reply:
        return json.loads(reply.read())


def cdp_alive(port):
    try:
        _json_url(port, '/json/version', timeout=2)
        return True
    except Exception:
        return False


def list_pages(port):
    try:
        return _json_url(port, '/json', timeout=4)
    except Exception:
        return []


def browser_kind_on_port(port):
    try:
        info = _json_url(port, '/json/version', timeout=2)
    except Exception:
        return None
    marker = (str(info.get('Browser', '')) + ' ' + str(info.get('User-Agent', ''))).lower()
    if 'edg/' in marker:
        return 'edge'
    if 'quark' in marker:
        return 'quark'
    if 'chrome' in marker:
        return 'chrome'
    return 'unknown'


def launch_browser(executable, kind, port):
    return subprocess.Popen([executable] + browser_args(kind, port), close_fds=True)


def stop_managed_browser(kind, port):
    if kind == 'quark':
        subprocess.run(
            ['taskkill', '/F', '/T', '/IM', os.path.basename(EXECUTABLE_NAMES['quark'])],
            capture_output=True,
            timeout=15,
        )
        return
    if kind not in EXECUTABLE_NAMES:
        try:
            info = _json_url(port, '/json/version', timeout=3)
            client = CDPClient(info['webSocketDebuggerUrl'], timeout=5)
            try:
                client.request('Browser.close', timeout=5)
            finally:
                client.close()
        except Exception:
            pass
        return
    profile_name = os.path.basename(profile_dir(kind))
    executable_name = EXECUTABLE_NAMES.get(kind, '')
    script = (
        "Get-CimInstance Win32_Process -Filter \"Name='%s'\" | "
        "Where-Object { $_.CommandLine -like '*%s*' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    ) % (executable_name, profile_name)
    subprocess.run(
        ['powershell', '-NoProfile', '-Command', script],
        capture_output=True,
        timeout=20,
    )


def wait_for_cdp(port, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if cdp_alive(port):
            return True
        time.sleep(1)
    return False


def create_target(port, url):
    info = _json_url(port, '/json/version', timeout=5)
    client = CDPClient(info['webSocketDebuggerUrl'], timeout=12)
    try:
        result = client.request('Target.createTarget', {'url': url}, timeout=12)
        return result.get('targetId')
    finally:
        client.close()


def close_target(port, target_id):
    try:
        with urllib.request.urlopen(
                'http://127.0.0.1:%d/json/close/%s' % (int(port), target_id), timeout=4):
            return True
    except Exception:
        return False
