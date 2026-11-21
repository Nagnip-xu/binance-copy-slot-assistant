# -*- coding: utf-8 -*-
"""币安页面注入、提交控制和状态读取。"""
import json
import time

import browser_control
import cdp


ENTRY_ORIGIN = 'https://www.bsmkweb.cc'

SETTING_URL = (
    ENTRY_ORIGIN + '/zh-CN/copy-trading/copy-setting'
    '?portfolioId={trader_id}&type=FIXED_RATIO'
)

HOOK_SCRIPT = r"""
(function () {
  try {
    if (window.__copySlotRequire) return 'already';
    var chunks = window.webpackChunkcopytrader_ui;
    if (!chunks) return 'webpack-not-ready';
    chunks.push([['copy-slot-independent-' + Date.now()], {}, function (require) {
      window.__copySlotRequire = require;
    }]);
    return window.__copySlotRequire ? 'ok' : 'hook-failed';
  } catch (error) {
    return 'hook-error:' + String(error && error.message || error);
  }
})()
"""

INSTALL_TEMPLATE = r"""
(function () {
  try {
    if (!window.__copySlotRequire) return 'missing-hook';
    var submitModule;
    try { submitModule = window.__copySlotRequire(26159); }
    catch (error) { return 'module-26159-unavailable'; }
    if (!submitModule || typeof submitModule.jT !== 'function') {
      return 'module-26159-jT-unavailable';
    }

    if (window.__copySlotState) window.__copySlotState.running = false;
    var state = {
      version: %(version)d,
      running: true,
      count: 0,
      ok: 0,
      errors: 0,
      busy: 0,
      inFlight: 0,
      rateLimit: %(rate)d,
      nextAt: Date.now(),
      startedAt: Date.now(),
      lastMessage: '',
      success: null
    };
    window.__copySlotState = state;
    var body = %(body)s;

    function delay(ms) {
      return new Promise(function (resolve) { setTimeout(resolve, ms); });
    }

    async function reserveSlot() {
      while (state.running && window.__copySlotState === state) {
        var now = Date.now();
        var interval = 1000 / Math.max(1, Number(state.rateLimit) || 1);
        if (!state.nextAt || state.nextAt < now - 1000) state.nextAt = now;
        if (now >= state.nextAt) {
          state.nextAt = Math.max(now, state.nextAt) + interval;
          return true;
        }
        await delay(Math.max(5, Math.min(50, state.nextAt - now)));
      }
      return false;
    }

    async function worker() {
      while (state.running && window.__copySlotState === state) {
        if (!(await reserveSlot())) return;
        if (!state.running || window.__copySlotState !== state) return;
        state.inFlight++;
        try {
          var result = await submitModule.jT(body);
          state.count++;
          if (result) {
            state.lastMessage = result.message
              ? String(result.message).slice(0, 120)
              : (result.success ? 'SUCCESS' : 'no-message');
          }
          if (result && result.success) {
            state.ok++;
            state.success = JSON.stringify(result).slice(0, 500);
            state.running = false;
          } else if (result && result.message) {
            var message = String(result.message);
            if (message.indexOf('正忙') >= 0 || message.indexOf('稍后') >= 0) state.busy++;
            else if (message.indexOf('满') < 0) state.errors++;
          }
        } catch (error) {
          state.count++;
          state.errors++;
          state.lastMessage = 'EXC:' + String(error && error.message || error).slice(0, 100);
        } finally {
          state.inFlight = Math.max(0, state.inFlight - 1);
        }
      }
    }

    for (var i = 0; i < %(workers)d; i++) worker();
    return 'installed';
  } catch (error) {
    return 'install-error:' + String(error && error.message || error);
  }
})()
"""

READ_STATE_SCRIPT = r"""
(function () {
  try {
    var state = window.__copySlotState || null;
    var text = document.body ? document.body.innerText : '';
    return JSON.stringify({
      badPage: location.href.indexOf('chromewebdata') >= 0,
      page429: text.indexOf('HTTP ERROR 429') >= 0,
      inaccessible: text.indexOf('无法访问') >= 0,
      copyPage: location.href.indexOf('copy-setting') >= 0,
      hook: typeof window.__copySlotRequire !== 'undefined',
      installed: !!state,
      version: state ? state.version : null,
      count: state ? state.count : 0,
      ok: state ? state.ok : 0,
      errors: state ? state.errors : 0,
      busy: state ? state.busy : 0,
      inFlight: state ? state.inFlight : 0,
      rateLimit: state ? state.rateLimit : 0,
      running: state ? !!state.running : false,
      message: state ? (state.lastMessage || '') : '',
      success: state ? state.success : null
    });
  } catch (error) {
    return JSON.stringify({readError: String(error && error.message || error)});
  }
})()
"""

STOP_SCRIPT = r"""
(function () {
  if (!window.__copySlotState) return 'not-installed';
  window.__copySlotState.running = false;
  return 'stopped:' + window.__copySlotState.count;
})()
"""


def build_submit_body(trader_id, amount):
    return {
        'disposalStrategy': 'SELL_ALL',
        'enableAutoInvest': False,
        'leverageMode': 'FOLLOW_LEAD',
        'marginMode': 'FOLLOW_LEAD',
        'investAmount': float(amount),
        'copyModel': 'FIXED_RATIO',
        'costPerOrder': 0,
        'investAsset': 'USDT',
        'mirrorMode': 'BETTER',
        'totalStopLossUsdt': 0,
        'followNewSymbols': True,
        'canTradFi': True,
        'leadPortfolioId': str(trader_id),
    }


def find_setting_page(port, trader_id=None):
    pages = browser_control.list_pages(port)
    candidates = []
    for page in pages:
        url = page.get('url') or ''
        if page.get('type') != 'page' or 'copy-setting' not in url or 'chromewebdata' in url:
            continue
        if trader_id and ('portfolioId=' + str(trader_id)) not in url:
            continue
        candidates.append(page)
    return candidates[0] if candidates else None


def close_copy_pages(port):
    for page in browser_control.list_pages(port):
        if page.get('type') == 'page' and 'copy-setting' in (page.get('url') or ''):
            cdp.discard(page.get('webSocketDebuggerUrl'))
            browser_control.close_target(port, page.get('id'))


def open_setting_page(port, trader_id):
    close_copy_pages(port)
    url = SETTING_URL.format(trader_id=str(trader_id))
    return browser_control.create_target(port, url)


def wait_for_setting_page(port, trader_id, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        page = find_setting_page(port, trader_id)
        if page:
            try:
                state = read_state(page['webSocketDebuggerUrl'])
                if state.get('copyPage') and not state.get('badPage'):
                    return page
            except Exception:
                pass
        time.sleep(2)
    return None


def install(websocket_url, trader_id, amount, rate_limit, workers=6, version=None):
    version = int(version if version is not None else time.time() * 1000) % 1000000000
    client = cdp.get_client(websocket_url)
    hook_result = client.evaluate(HOOK_SCRIPT, timeout=12)
    if hook_result not in ('ok', 'already'):
        return False, str(hook_result), version
    script = INSTALL_TEMPLATE % {
        'version': version,
        'rate': max(1, min(50, int(rate_limit))),
        'workers': max(1, min(12, int(workers))),
        'body': json.dumps(build_submit_body(trader_id, amount), ensure_ascii=False),
    }
    result = client.evaluate(script, timeout=15)
    return result == 'installed', str(result), version


def read_state(websocket_url):
    try:
        raw = cdp.get_client(websocket_url).evaluate(READ_STATE_SCRIPT, timeout=10)
        return json.loads(raw) if raw else {'readError': 'empty-state'}
    except Exception as error:
        cdp.discard(websocket_url)
        return {'readError': str(error)[:120]}


def stop(websocket_url):
    try:
        return cdp.get_client(websocket_url).evaluate(STOP_SCRIPT, timeout=8)
    except Exception as error:
        cdp.discard(websocket_url)
        return 'stop-error:' + str(error)[:100]


def reload_page(websocket_url):
    try:
        client = cdp.get_client(websocket_url)
        client.request('Page.enable', timeout=5)
        client.request('Page.reload', {'ignoreCache': False}, timeout=8)
        cdp.discard(websocket_url)
        return True
    except Exception:
        cdp.discard(websocket_url)
        return False


def fetch_room(websocket_url, trader_id):
    script = r"""
(async function () {
  try {
    var response = await fetch(
      '/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/copy-traders',
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({pageNumber: 1, pageSize: 1, portfolioId: '%s'})
      }
    );
    var text = await response.text();
    if (!response.ok) return JSON.stringify({ok: false, error: 'HTTP ' + response.status});
    var data = JSON.parse(text);
    var payload = data && data.data || {};
    var total = payload.total;
    if (total === undefined || total === null) total = payload.totalCount;
    return JSON.stringify({ok: total !== undefined && total !== null, total: total});
  } catch (error) {
    return JSON.stringify({ok: false, error: String(error && error.message || error)});
  }
})()
""" % str(trader_id)
    try:
        raw = cdp.get_client(websocket_url).evaluate(script, timeout=15)
        return json.loads(raw) if raw else {'ok': False, 'error': 'empty-response'}
    except Exception as error:
        return {'ok': False, 'error': str(error)[:100]}
