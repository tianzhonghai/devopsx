import time


class CommonUtils:
    @staticmethod
    def get_format_time():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
