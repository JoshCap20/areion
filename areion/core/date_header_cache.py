"""
Why can't we just do headers["Date"] = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT") and be done with it?

Performance.
"""

import threading
import datetime
import time


class DateHeaderCache:
    """
    Singleton class to cache the Date header value, updating it once per second.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DateHeaderCache, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.date_str = self._get_current_date()
        self.update_lock = threading.Lock()
        self.updater_thread = threading.Thread(target=self._update_date, daemon=True)
        self.updater_thread.start()

    def _get_current_date(self) -> str:
        """
        Get the current UTC date formatted per HTTP standards.
        Example: 'Wed, 21 Oct 2015 07:28:00 GMT'
        """
        return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _update_date(self):
        """
        Continuously update the date string every second.
        """
        while True:
            new_date = self._get_current_date()
            with self.update_lock:
                self.date_str = new_date
            time.sleep(1)

    def get_date(self) -> str:
        """
        Retrieve the current cached date string.
        """
        with self.update_lock:
            return self.date_str
