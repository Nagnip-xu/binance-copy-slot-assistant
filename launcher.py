# -*- coding: utf-8 -*-
"""可记录启动阶段异常的独立版入口。"""
import os
import sys
import traceback


APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
ERROR_LOG = os.path.join(APP_DIR, '启动错误.log')


def main():
    try:
        import app
        app.main()
    except Exception:
        detail = traceback.format_exc()
        try:
            with open(ERROR_LOG, 'w', encoding='utf-8') as handle:
                handle.write(detail)
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                '程序启动失败，详细信息已保存到：\n' + ERROR_LOG,
                '币安跟单抢位助手 · 启动失败',
                0x10,
            )
        except Exception:
            pass
        raise


if __name__ == '__main__':
    main()
