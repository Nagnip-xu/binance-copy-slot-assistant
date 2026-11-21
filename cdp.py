# -*- coding: utf-8 -*-
"""最小化 Chrome DevTools Protocol 客户端。"""
import json
import threading
import time

import websocket


class CDPError(RuntimeError):
    pass


class CDPClient(object):
    def __init__(self, websocket_url, timeout=12):
        self.websocket_url = websocket_url
        self.timeout = timeout
        self._lock = threading.RLock()
        self._socket = None
        self._next_id = 0

    def _connect(self):
        if self._socket is not None and getattr(self._socket, 'connected', False):
            return
        self.close()
        self._socket = websocket.create_connection(
            self.websocket_url,
            timeout=self.timeout,
            suppress_origin=True,
        )

    def request(self, method, params=None, timeout=None):
        with self._lock:
            self._connect()
            self._next_id += 1
            request_id = self._next_id
            message = {'id': request_id, 'method': method}
            if params is not None:
                message['params'] = params
            try:
                self._socket.send(json.dumps(message))
                self._socket.settimeout(timeout or self.timeout)
                deadline = time.time() + (timeout or self.timeout)
                while time.time() < deadline:
                    reply = json.loads(self._socket.recv())
                    if reply.get('id') != request_id:
                        continue
                    if reply.get('error'):
                        raise CDPError(str(reply['error']))
                    return reply.get('result') or {}
                raise CDPError('%s timed out' % method)
            except Exception:
                self.close()
                raise

    def evaluate(self, expression, await_promise=True, timeout=None):
        result = self.request(
            'Runtime.evaluate',
            {
                'expression': expression,
                'returnByValue': True,
                'awaitPromise': bool(await_promise),
            },
            timeout=timeout,
        )
        if result.get('exceptionDetails'):
            desc = result['exceptionDetails'].get('exception', {}).get('description', '')
            raise CDPError(desc or 'JavaScript evaluation failed')
        return result.get('result', {}).get('value')

    def close(self):
        sock, self._socket = self._socket, None
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass


_clients = {}
_clients_lock = threading.Lock()


def get_client(websocket_url, timeout=12):
    with _clients_lock:
        client = _clients.get(websocket_url)
        if client is None:
            client = CDPClient(websocket_url, timeout=timeout)
            _clients[websocket_url] = client
        return client


def discard(websocket_url=None):
    with _clients_lock:
        if websocket_url is None:
            clients = list(_clients.values())
            _clients.clear()
        else:
            client = _clients.pop(websocket_url, None)
            clients = [client] if client else []
    for client in clients:
        client.close()
