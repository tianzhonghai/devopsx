

class DeployResultEnum:
    """发布结果"""
    PENDING = 0
    SUCCESS = 1
    FAIL = 2

    @staticmethod
    def convert_to_desc(val):
        if val == 0:
            return ""
        elif val == 1:
            return "发布成功"
        elif val == 2:
            return "发布失败"


class WfActivityConst:
    created = "Created"
    confirmVersion = "ConfirmVersion"
    confirmPublish = "ConfirmPublish"
    publishing = "Publishing"
    published = "Published"
    test = "Test"
    close = "Close"

    @staticmethod
    def convert_to_desc(val):
        if val == "Created":
            return "新建"
        if val == "ConfirmVersion":
            return "版本确认"
        if val == "ConfirmPublish":
            return "确认发布"
        if val == "Publishing":
            return "发布中"
        if val == "Published":
            return "发布完成"
        if val == "Test":
            return "测试验证"
        if val == "Complete":
            return "结束"
