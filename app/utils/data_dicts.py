

class DeployResultEnum:
    """发布结果"""
    PENDING = 0
    SUCCESS = 1
    FAIL = 2
    ROOLBACK = 3

    @staticmethod
    def convert_to_desc(val):
        if val == 0:
            return ""
        elif val == 1:
            return "发布成功"
        elif val == 2:
            return "发布失败"
        elif val == 3:
            return "回滚"


class WfActivityConst:
    """发布流程节点"""
    new = "New"
    version = "Version"
    audit = "Audit"
    deploy = "Deploy"
    test = "Test"
    complete = "Complete"

    @staticmethod
    def convert_to_desc(val):
        if val == "New":
            return "流程发起"
        if val == "Version":
            return "版本确认"
        if val == "Audit":
            return "发布审核"
        if val == "Deploy":
            return "系统部署"
        if val == "Test":
            return "系统测试"
        if val == "Complete":
            return "发布完成"

