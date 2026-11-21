# -*- coding: utf-8 -*-
"""独立版配置读写。"""
import json
import os


APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, 'config.json')

DEFAULT_CONFIG = {
    'trader_id': '5075281354358777856',
    'trader_name': '熬鹰资本',
    'amount': 300.0,
    'rate_limit': 11,
    'browser': 'edge',
    'browser_exe': '',
    'cdp_port': 9222,
    'auto_start': False,
    'direct_submit': False,
    'refresh_enabled': True,
    'refresh_minutes': 45,
}


def normalize(raw):
    cfg = dict(DEFAULT_CONFIG)
    if isinstance(raw, dict):
        cfg.update(raw)
    cfg['trader_id'] = str(cfg.get('trader_id') or '').strip()
    cfg['trader_name'] = str(cfg.get('trader_name') or '').strip()
    try:
        cfg['amount'] = max(0.01, float(cfg.get('amount', 300)))
    except (TypeError, ValueError):
        cfg['amount'] = 300.0
    try:
        cfg['rate_limit'] = max(1, min(50, int(float(cfg.get('rate_limit', 11)))))
    except (TypeError, ValueError):
        cfg['rate_limit'] = 11
    browser = str(cfg.get('browser') or 'edge').lower()
    cfg['browser'] = browser if browser in ('edge', 'chrome', 'quark', 'auto', 'custom') else 'edge'
    cfg['browser_exe'] = str(cfg.get('browser_exe') or '').strip().strip('"').strip("'")
    try:
        port = int(cfg.get('cdp_port', 9222))
        cfg['cdp_port'] = port if 1024 <= port <= 65535 else 9222
    except (TypeError, ValueError):
        cfg['cdp_port'] = 9222
    cfg['auto_start'] = bool(cfg.get('auto_start', False))
    cfg['direct_submit'] = bool(cfg.get('direct_submit', False))
    cfg['refresh_enabled'] = bool(cfg.get('refresh_enabled', True))
    try:
        cfg['refresh_minutes'] = max(0, min(1440, int(float(cfg.get('refresh_minutes', 45)))))
    except (TypeError, ValueError):
        cfg['refresh_minutes'] = 45
    return cfg


def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as handle:
            return normalize(json.load(handle))
    except Exception:
        return normalize({})


def save_config(cfg):
    data = normalize(cfg)
    temp_file = CONFIG_FILE + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(temp_file, CONFIG_FILE)
    return data
