import threading

from utils.worker_thread import Subscriber

_LOG_PAYLOAD_KEY = 'v1.log'


class Logger(Subscriber):
    def __init__(self):
        self._connection = None
        self._log_buffer = []
        self._log_buffer_lock = threading.Lock()
        self._order = 0

    def set_connection(self, connection):
        self._connection = connection

    def send_log(self, payload):
        with self._log_buffer_lock:
            self._log_buffer.append(payload)

    def did_start(self):
        pass

    def will_stop(self):
        # TODO: IMPLEMENT ME! May need to flush buffers.
        # Only do this if there is an active connection.
        pass

    def minimum_loop_time_secs(self):
        return 60

    def loop(self):
        global _LOG_PAYLOAD_KEY

        self._batch_logs()

        if self._connection is None:
            return

        with self._log_buffer_lock:
            for payload in self._log_buffer:
                payload['order'] = self._order
                self._order += 1
                self._connection.send_directive(_LOG_PAYLOAD_KEY, payload)

            self._log_buffer.clear()

    def _batch_logs(self):
        with self._log_buffer_lock:
            self._batch_logs_progressbar_set()
            self._batch_logs_message_send()

    def _batch_logs_progressbar_set(self):
        remove_indices = set()

        key_to_idx = {}

        for i in range(len(self._log_buffer)):
            payload = self._log_buffer[i]
            if payload['logType'] != 'progressBarSet':
                continue

            key = payload['key']
            if key in key_to_idx:
                remove_indices.add(i)
                target_payload = self._log_buffer[key_to_idx[key]]
                target_payload['progress'] = payload['progress']
            else:
                key_to_idx[key] = i

        self._log_buffer = [p for i, p in enumerate(self._log_buffer)
                            if i not in remove_indices]

    def _batch_logs_message_send(self):
        remove_indices = set()

        for i in reversed(range(1, len(self._log_buffer))):
            payload = self._log_buffer[i]
            prev_payload = self._log_buffer[i - 1]

            if payload['logType'] != 'messageSend' or prev_payload['logType'] != 'messageSend':
                continue

            # Collapse the message into the previous payload.
            prev_payload['content'] += f'\n{payload["content"]}'
            remove_indices.add(i)

        self._log_buffer = [p for i, p in enumerate(self._log_buffer)
                            if i not in remove_indices]
