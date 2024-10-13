import unittest
from areion.core.date_header_cache import DateHeaderCache
import datetime
import time


class TestDateHeaderCache(unittest.TestCase):

    def test_singleton_instance(self):
        instance1 = DateHeaderCache()
        instance2 = DateHeaderCache()
        self.assertIs(instance1, instance2, "DateHeaderCache is not a singleton")

    def test_date_format(self):
        instance = DateHeaderCache()
        date_str = instance.get_date()
        try:
            datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        except ValueError:
            self.fail("DateHeaderCache date format is incorrect")

    def test_date_update(self):
        instance = DateHeaderCache()
        date_str1 = instance.get_date()
        time.sleep(2)
        date_str2 = instance.get_date()
        self.assertNotEqual(date_str1, date_str2, "DateHeaderCache date did not update")


if __name__ == "__main__":
    unittest.main()
