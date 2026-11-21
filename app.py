# -*- coding: utf-8 -*-
"""独立版桌面界面与运行状态机。"""
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

# 随包 Python 的 ._pth 开启了隔离模式，需显式加入程序目录。
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import browser_control
import cdp
import config as config_store
import engine


BG = '#1b1e24'
PANEL = '#23272f'
ENTRY = '#2c313a'
FG = '#d8dee8'
MUTED = '#8b95a5'
GREEN = '#4ec97a'
YELLOW = '#e0a055'
RED = '#e05555'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = config_store.load_config()
        self.title('币安跟单抢位助手 · 独立版')
        self.geometry('850x680')
        self.minsize(760, 600)
        self.configure(bg=BG)
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max(0, (screen_width - 850) // 2)
        y = max(0, (screen_height - 680) // 2)
        self.geometry('850x680+%d+%d' % (x, y))
        self.attributes('-topmost', True)
        self.after(1500, lambda: self.attributes('-topmost', False))
        self.after(50, self._bring_to_front)

        self.run_event = threading.Event()
        self.reinstall_event = threading.Event()
        self.worker = None
        self.current_page = None
        self.current_browser_kind = None
        self.current_browser_exe = None
        self.last_count = None
        self.last_count_time = None
        self.measured_rate = 0.0
        self.last_refresh = time.time()
        self.room_total = None
        self.won = False
        self._status_busy = False
        self._room_busy = False
        self._closing = False

        self.direct_var = tk.BooleanVar(value=bool(self.cfg.get('direct_submit', False)))
        self.refresh_var = tk.BooleanVar(value=bool(self.cfg.get('refresh_enabled', True)))
        self.browser_var = tk.StringVar(value=str(self.cfg.get('browser', 'edge')))

        self._build_ui()
        self.protocol('WM_DELETE_WINDOW', self.close_app)
        self.after(1000, self.status_tick)
        self.after(5000, self.room_tick)

        self.say('独立版已就绪；不含原程序授权或15分钟试用限制')
        if not self.direct_var.get():
            self.say('当前为仅监控模式，不会提交真实跟单')
        if self.cfg.get('auto_start'):
            self.say('配置已开启自动启动，3秒后开始')
            self.after(3000, self.start)

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            pass

    def _build_ui(self):
        top = tk.Frame(self, bg=PANEL)
        top.pack(fill='x', padx=10, pady=(10, 6))

        self.trader_entry = self._field(top, '交易员ID', self.cfg['trader_id'], 0, 25)
        self.name_entry = self._field(top, '名称', self.cfg['trader_name'], 1, 13)
        self.amount_entry = self._field(top, '金额(USDT)', self.cfg['amount'], 2, 10)

        tk.Label(top, text='速率(次/秒)', bg=PANEL, fg=MUTED,
                 font=('Microsoft YaHei UI', 9)).grid(row=0, column=3, sticky='w', padx=8, pady=(8, 2))
        rate_frame = tk.Frame(top, bg=PANEL)
        rate_frame.grid(row=1, column=3, padx=8, pady=(0, 8))
        self.rate_entry = tk.Entry(rate_frame, bg=ENTRY, fg=FG, insertbackground=FG,
                                   relief='flat', font=('Consolas', 11), width=5, justify='center')
        self.rate_entry.insert(0, str(self.cfg['rate_limit']))
        self.rate_entry.pack(side='left')
        self._small_button(rate_frame, '−', lambda: self.change_rate(-1))
        self._small_button(rate_frame, '+', lambda: self.change_rate(1))
        self.rate_entry.bind('<Return>', lambda _event: self.apply_rate())
        self.rate_entry.bind('<FocusOut>', lambda _event: self.apply_rate())

        self.rate_warning = tk.Label(top, text='', bg=PANEL, fg=YELLOW,
                                     font=('Microsoft YaHei UI', 8))
        self.rate_warning.grid(row=2, column=3, sticky='w', padx=8)
        self._update_rate_warning(self.cfg['rate_limit'])

        tk.Label(top, text='浏览器', bg=PANEL, fg=MUTED,
                 font=('Microsoft YaHei UI', 9)).grid(row=2, column=0, sticky='w', padx=8, pady=(0, 8))
        browser_frame = tk.Frame(top, bg=PANEL)
        browser_frame.grid(row=2, column=1, columnspan=2, sticky='w', padx=8, pady=(0, 8))
        for kind, label in (('edge', 'Edge'), ('chrome', 'Chrome'), ('quark', '夸克'), ('auto', '自动')):
            tk.Radiobutton(
                browser_frame,
                text=label,
                value=kind,
                variable=self.browser_var,
                command=self.browser_changed,
                bg=PANEL,
                fg=FG,
                selectcolor='#3a5a8b',
                activebackground=PANEL,
                activeforeground='white',
                highlightthickness=0,
                bd=0,
            ).pack(side='left', padx=(0, 8))
        tk.Button(browser_frame, text='选择程序…', command=self.pick_browser,
                  bg='#3a4048', fg=FG, relief='flat', cursor='hand2').pack(side='left')

        stats = tk.Frame(self, bg=PANEL)
        stats.pack(fill='x', padx=10, pady=6)
        self.page_label = self._stat(stats, '页面状态', '等待启动…')
        self.component_label = self._stat(stats, '提交组件', '未安装')
        self.rate_label = self._stat(stats, '实测速率', '0.0 次/秒')
        self.count_label = self._stat(stats, '提交次数', '0')
        self.room_label = self._stat(stats, '房间人数', '—')
        self.message_label = self._stat(stats, '最近响应', '—')
        self.refresh_label = self._stat(stats, '自动刷新', '—')

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill='x', padx=10, pady=4)
        self.start_button = self._button(buttons, '▶ 启动', self.start, '#2e8b57')
        self.stop_button = self._button(buttons, '■ 停止', self.stop, '#8b3a3a')
        self.reopen_button = self._button(buttons, '↻ 重开浏览器', self.reopen_browser, '#3a5a8b')
        self.direct_button = self._button(buttons, '', self.toggle_direct, '#444444')
        self.refresh_button = self._button(buttons, '', self.toggle_refresh, '#4a5058')
        self._update_direct_button()
        self._update_refresh_button()

        tk.Label(self, text='运行日志', bg=BG, fg=MUTED,
                 font=('Microsoft YaHei UI', 9)).pack(anchor='w', padx=14)
        self.log_text = tk.Text(self, bg='#14171c', fg='#9fb0c5', relief='flat',
                                font=('Consolas', 9), height=17)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(2, 10))
        self.log_text.configure(state='disabled')

    def _field(self, parent, label, value, column, width):
        tk.Label(parent, text=label, bg=PANEL, fg=MUTED,
                 font=('Microsoft YaHei UI', 9)).grid(row=0, column=column, sticky='w', padx=8, pady=(8, 2))
        entry = tk.Entry(parent, bg=ENTRY, fg=FG, insertbackground=FG,
                         relief='flat', font=('Consolas', 10), width=width)
        entry.insert(0, str(value))
        entry.grid(row=1, column=column, padx=8, pady=(0, 8))
        return entry

    def _small_button(self, parent, text, command):
        tk.Button(parent, text=text, command=command, bg='#3a4048', fg=FG,
                  relief='flat', width=2, cursor='hand2').pack(side='left', padx=2)

    def _button(self, parent, text, command, color):
        button = tk.Button(parent, text=text, command=command, bg=color, fg='white',
                           relief='flat', padx=12, pady=6, cursor='hand2',
                           font=('Microsoft YaHei UI', 9))
        button.pack(side='left', padx=4)
        return button

    def _stat(self, parent, label, value):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill='x', padx=8, pady=1)
        tk.Label(row, text=label, bg=PANEL, fg=MUTED, width=10, anchor='w',
                 font=('Microsoft YaHei UI', 9)).pack(side='left')
        result = tk.Label(row, text=value, bg=PANEL, fg=FG, anchor='w', justify='left',
                          font=('Consolas', 10))
        result.pack(side='left', fill='x', expand=True)
        return result

    def ui(self, callback):
        if self._closing:
            return
        try:
            self.after(0, callback)
        except Exception:
            pass

    def say(self, message):
        line = '[%s] %s' % (time.strftime('%H:%M:%S'), message)
        try:
            with open(os.path.join(config_store.APP_DIR, 'independent.log'), 'a', encoding='utf-8') as handle:
                handle.write(line + '\n')
        except Exception:
            pass

        def append():
            self.log_text.configure(state='normal')
            self.log_text.insert('end', line + '\n')
            self.log_text.see('end')
            self.log_text.configure(state='disabled')
        self.ui(append)

    def set_status(self, label, text, color=FG):
        self.ui(lambda: label.configure(text=text, fg=color))

    def _read_form(self):
        trader_id = self.trader_entry.get().strip()
        if not trader_id.isdigit():
            raise ValueError('交易员ID必须是纯数字')
        try:
            amount = float(self.amount_entry.get().strip())
        except ValueError:
            raise ValueError('金额必须是数字')
        if amount <= 0:
            raise ValueError('金额必须大于0')
        try:
            rate = int(float(self.rate_entry.get().strip()))
        except ValueError:
            raise ValueError('速率必须是数字')
        if not 1 <= rate <= 50:
            raise ValueError('速率必须在1到50之间')
        self.cfg.update({
            'trader_id': trader_id,
            'trader_name': self.name_entry.get().strip(),
            'amount': amount,
            'rate_limit': rate,
            'browser': self.browser_var.get(),
            'direct_submit': self.direct_var.get(),
            'refresh_enabled': self.refresh_var.get(),
        })
        self.cfg = config_store.save_config(self.cfg)
        return self.cfg

    def change_rate(self, delta):
        try:
            current = int(float(self.rate_entry.get().strip()))
        except ValueError:
            current = 11
        value = max(1, min(50, current + delta))
        self.rate_entry.delete(0, 'end')
        self.rate_entry.insert(0, str(value))
        self.apply_rate()

    def apply_rate(self):
        try:
            rate = max(1, min(50, int(float(self.rate_entry.get().strip()))))
        except ValueError:
            return
        self.rate_entry.delete(0, 'end')
        self.rate_entry.insert(0, str(rate))
        old = self.cfg.get('rate_limit')
        self.cfg['rate_limit'] = rate
        config_store.save_config(self.cfg)
        self._update_rate_warning(rate)
        if old != rate and self.run_event.is_set() and self.direct_var.get():
            self.reinstall_event.set()
            self.say('速率调整为 %d 次/秒，正在重新加载提交组件' % rate)

    def _update_rate_warning(self, rate):
        if rate > 14:
            text, color = '⚠ 高频率，容易触发429', RED
        elif rate > 11:
            text, color = '建议不超过11次/秒', YELLOW
        else:
            text, color = '', YELLOW
        self.rate_warning.configure(text=text, fg=color)

    def browser_changed(self):
        self.cfg['browser'] = self.browser_var.get()
        self.cfg['browser_exe'] = ''
        config_store.save_config(self.cfg)
        self.say('浏览器已选择：%s' % browser_control.BROWSER_LABELS.get(self.browser_var.get(), self.browser_var.get()))

    def pick_browser(self):
        path = filedialog.askopenfilename(
            title='选择 Chromium 浏览器程序',
            filetypes=[('可执行程序', '*.exe'), ('全部文件', '*.*')],
        )
        if not path:
            return
        kind = browser_control.kind_from_path(path)
        self.cfg['browser_exe'] = path
        self.cfg['browser'] = kind
        self.browser_var.set(kind)
        config_store.save_config(self.cfg)
        self.say('已选择浏览器：%s' % path)

    def _update_direct_button(self):
        enabled = self.direct_var.get()
        self.direct_button.configure(
            text='真实提交: %s' % ('ON' if enabled else 'OFF'),
            bg='#5a4a8b' if enabled else '#444444',
        )

    def toggle_direct(self):
        new_value = not self.direct_var.get()
        if new_value:
            confirmed = messagebox.askyesno(
                '确认真实提交',
                '开启后会使用浏览器中的币安账户提交真实跟单，可能转入USDT并产生亏损。\n\n确认开启吗？',
                icon='warning',
            )
            if not confirmed:
                return
        self.direct_var.set(new_value)
        self.cfg['direct_submit'] = new_value
        config_store.save_config(self.cfg)
        self._update_direct_button()
        if new_value:
            self.say('真实提交已开启')
            if self.run_event.is_set():
                self.reinstall_event.set()
        else:
            self.say('真实提交已关闭，正在停止网页提交循环')
            self._stop_page_async()

    def _update_refresh_button(self):
        enabled = self.refresh_var.get()
        minutes = self.cfg.get('refresh_minutes', 45)
        self.refresh_button.configure(
            text='自动刷新: %d分 %s' % (minutes, 'ON' if enabled else 'OFF'),
            bg='#4a5058' if enabled else '#3a3a3a',
        )

    def toggle_refresh(self):
        self.refresh_var.set(not self.refresh_var.get())
        self.cfg['refresh_enabled'] = self.refresh_var.get()
        config_store.save_config(self.cfg)
        self.last_refresh = time.time()
        self._update_refresh_button()
        self.say('自动刷新已%s' % ('开启' if self.refresh_var.get() else '关闭'))

    def start(self):
        if self.run_event.is_set() and self.worker and self.worker.is_alive():
            self.say('当前已经在运行')
            return
        try:
            self._read_form()
        except ValueError as error:
            messagebox.showerror('配置错误', str(error))
            return
        self.won = False
        self.last_count = None
        self.last_count_time = None
        self.reinstall_event.set()
        self.run_event.set()
        self.worker = threading.Thread(target=self.run_loop, daemon=True)
        self.worker.start()
        mode = '真实提交' if self.direct_var.get() else '仅监控'
        self.say('开始运行：%s / %s / %s' % (self.cfg['trader_name'], self.cfg['trader_id'], mode))

    def stop(self):
        self.run_event.clear()
        self.reinstall_event.clear()
        self.say('正在停止')
        self._stop_page_async()
        self.set_status(self.rate_label, '0.0 次/秒（已停止）', YELLOW)

    def _stop_page_async(self):
        page = self.current_page

        def work():
            if page and page.get('webSocketDebuggerUrl'):
                result = engine.stop(page['webSocketDebuggerUrl'])
                self.say('网页提交循环：%s' % result)
        threading.Thread(target=work, daemon=True).start()

    def ensure_browser(self):
        kind, executable = browser_control.find_browser(self.cfg)
        if not executable:
            return False, '没有找到可用浏览器，请使用“选择程序”指定浏览器'
        port = self.cfg['cdp_port']
        if browser_control.cdp_alive(port):
            owner = browser_control.browser_kind_on_port(port)
            matches = owner == kind or (kind == 'quark' and owner in ('chrome', 'unknown'))
            if not matches:
                return False, '调试端口%d已被%s占用，请关闭对应浏览器或更换端口' % (port, owner)
            self.current_browser_kind = kind
            self.current_browser_exe = executable
            return True, '%s调试端口已连接' % browser_control.BROWSER_LABELS.get(kind, kind)
        process = browser_control.launch_browser(executable, kind, port)
        self.current_browser_kind = kind
        self.current_browser_exe = executable
        self.say('已启动%s，进程号%d' % (browser_control.BROWSER_LABELS.get(kind, kind), process.pid))
        if not browser_control.wait_for_cdp(port, timeout=40):
            return False, '浏览器已启动，但调试端口没有就绪'
        return True, '%s已就绪' % browser_control.BROWSER_LABELS.get(kind, kind)

    def ensure_page(self, force=False):
        port = self.cfg['cdp_port']
        page = None if force else engine.find_setting_page(port, self.cfg['trader_id'])
        if page:
            self.current_page = page
            return page
        self.say('正在打开币安跟单设置页')
        engine.open_setting_page(port, self.cfg['trader_id'])
        page = engine.wait_for_setting_page(port, self.cfg['trader_id'], timeout=90)
        self.current_page = page
        return page

    def run_loop(self):
        ok, message = self.ensure_browser()
        self.say(message)
        if not ok:
            self.run_event.clear()
            self.set_status(self.page_label, message, RED)
            return
        page = self.ensure_page()
        if not page:
            self.say('跟单页面未能加载，请检查网络和登录状态')
            self.run_event.clear()
            return
        websocket_url = page['webSocketDebuggerUrl']
        self.last_refresh = time.time()
        last_repair = 0

        while self.run_event.is_set() and not self._closing:
            state = engine.read_state(websocket_url)
            if state.get('success'):
                self.run_event.clear()
                self.reinstall_event.clear()
                self._notify_success(state['success'])
                break
            if state.get('readError') or state.get('badPage') or state.get('page429') or state.get('inaccessible'):
                if time.time() - last_repair > 15:
                    last_repair = time.time()
                    reason = state.get('readError') or ('429' if state.get('page429') else '页面异常')
                    self.say('页面异常：%s，尝试重新打开' % reason)
                    page = self.ensure_page(force=True)
                    if page:
                        websocket_url = page['webSocketDebuggerUrl']
                        self.reinstall_event.set()
                time.sleep(2)
                continue

            refresh_seconds = int(self.cfg.get('refresh_minutes', 45)) * 60
            if self.refresh_var.get() and refresh_seconds > 0 and time.time() - self.last_refresh >= refresh_seconds:
                self.say('到达定时刷新时间，正在刷新页面')
                self.last_refresh = time.time()
                if engine.reload_page(websocket_url):
                    time.sleep(5)
                    page = engine.wait_for_setting_page(
                        self.cfg['cdp_port'], self.cfg['trader_id'], timeout=60)
                else:
                    page = self.ensure_page(force=True)
                if page:
                    websocket_url = page['webSocketDebuggerUrl']
                    self.current_page = page
                self.reinstall_event.set()
                continue

            if not self.direct_var.get():
                if state.get('running'):
                    engine.stop(websocket_url)
                time.sleep(2)
                continue

            should_install = (
                self.reinstall_event.is_set()
                or not state.get('hook')
                or not state.get('installed')
                or not state.get('running')
            )
            if should_install:
                self.reinstall_event.clear()
                ok, detail, _version = engine.install(
                    websocket_url,
                    self.cfg['trader_id'],
                    self.cfg['amount'],
                    self.cfg['rate_limit'],
                )
                if ok:
                    self.say('真实提交组件安装成功，速率%d次/秒' % self.cfg['rate_limit'])
                else:
                    self.say('提交组件安装失败：%s' % detail)
                    time.sleep(5)
                    continue
            time.sleep(2)
        self.say('运行线程已停止')

    def status_tick(self):
        if self._closing:
            return
        if not self._status_busy:
            self._status_busy = True
            threading.Thread(target=self._status_work, daemon=True).start()
        self.after(2000, self.status_tick)

    def _status_work(self):
        try:
            port = self.cfg['cdp_port']
            if not browser_control.cdp_alive(port):
                self.set_status(self.page_label, '未连接浏览器', RED)
                self.set_status(self.component_label, '未安装', MUTED)
                return
            page = engine.find_setting_page(port, self.cfg.get('trader_id'))
            if not page:
                self.set_status(self.page_label, '没有币安跟单页', YELLOW)
                return
            self.current_page = page
            state = engine.read_state(page['webSocketDebuggerUrl'])
            if state.get('readError'):
                self.set_status(self.page_label, '读取失败', RED)
                return
            if state.get('page429'):
                self.set_status(self.page_label, '❌ 429限流', RED)
            elif state.get('inaccessible') or state.get('badPage'):
                self.set_status(self.page_label, '❌ 页面无法访问', RED)
            else:
                self.set_status(self.page_label, '✅ 正常', GREEN)
            component = []
            if state.get('hook'):
                component.append('hook')
            if state.get('installed'):
                component.append('提交v%s' % state.get('version'))
            self.set_status(self.component_label, ' + '.join(component) if component else '未安装',
                            GREEN if state.get('running') else YELLOW)
            count = int(state.get('count') or 0)
            now = time.time()
            if self.last_count is not None and self.last_count_time and now > self.last_count_time:
                self.measured_rate = max(0.0, (count - self.last_count) / (now - self.last_count_time))
            self.last_count, self.last_count_time = count, now
            self.set_status(self.count_label, str(count))
            self.set_status(self.rate_label, '%.1f 次/秒' % self.measured_rate,
                            GREEN if self.measured_rate >= 5 else YELLOW)
            self.set_status(self.message_label, str(state.get('message') or '—')[:100],
                            RED if 'EXC:' in str(state.get('message')) else FG)
            if state.get('success') and not self.won:
                self._notify_success(state['success'])
            if self.refresh_var.get():
                total = int(self.cfg.get('refresh_minutes', 45)) * 60
                left = max(0, total - int(time.time() - self.last_refresh))
                self.set_status(self.refresh_label, '下次 %02d:%02d' % (left // 60, left % 60))
            else:
                self.set_status(self.refresh_label, '已关闭', MUTED)
        finally:
            self._status_busy = False

    def room_tick(self):
        if self._closing:
            return
        if not self._room_busy and self.current_page:
            self._room_busy = True
            threading.Thread(target=self._room_work, daemon=True).start()
        self.after(60000, self.room_tick)

    def _room_work(self):
        try:
            page = self.current_page
            if not page:
                return
            result = engine.fetch_room(page['webSocketDebuggerUrl'], self.cfg['trader_id'])
            if not result.get('ok'):
                self.set_status(self.room_label, '读取失败：%s' % result.get('error', '未知'), YELLOW)
                return
            total = int(result['total'])
            previous = self.room_total
            if previous is not None and total != previous:
                if total > previous:
                    self.say('👤 房间人数增加：%d → %d' % (previous, total))
                else:
                    self.say('🚪 房间人数减少：%d → %d，可能出现空位' % (previous, total))
                self.bell()
            self.room_total = total
            self.set_status(self.room_label, '%d 人' % total)
        finally:
            self._room_busy = False

    def _notify_success(self, detail):
        if self.won:
            return
        self.won = True
        self.run_event.clear()
        self.say('🎉 已成功取得跟单位置：%s' % str(detail)[:250])
        self.bell()
        self.ui(lambda: messagebox.showinfo('抢位成功', '已经成功取得跟单位置。\n\n' + str(detail)[:300]))

    def bell(self):
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    def reopen_browser(self):
        self.stop()

        def work():
            kind = self.current_browser_kind or self.cfg.get('browser', 'edge')
            self.say('正在关闭独立浏览器实例')
            try:
                browser_control.stop_managed_browser(kind, self.cfg['cdp_port'])
            except Exception as error:
                self.say('关闭浏览器失败：%s' % str(error)[:100])
            cdp.discard()
            self.current_page = None
            time.sleep(2)
            self.say('浏览器已关闭，点击“启动”重新打开')
        threading.Thread(target=work, daemon=True).start()

    def close_app(self):
        if self._closing:
            return
        self._closing = True
        self.run_event.clear()
        try:
            if self.current_page:
                engine.stop(self.current_page['webSocketDebuggerUrl'])
        except Exception:
            pass
        cdp.discard()
        try:
            kind = self.current_browser_kind
            if kind:
                browser_control.stop_managed_browser(kind, self.cfg['cdp_port'])
        except Exception:
            pass
        self.destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
