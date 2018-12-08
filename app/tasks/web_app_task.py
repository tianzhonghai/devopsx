from .. import celery, utils, db
from multiprocessing import current_process
from app.ansible_api.playbook_runner import PlaybookRunner
from ..models import DeployItem
from ..service import wf_service


@celery.task
def deploy_app_task_async(deploy_id, bizapp):
    current_process()._config = {'semprefix': '/mp'}
    # 这里调用ansible
    try:
        utils.get_logger().info("开始执行同步任务,deploy_id=" + str(deploy_id))
        # runner = PlaybookRunner('192.168.3.22,192.168.2.243,192.178.2.13', deploy_id)
        runner = PlaybookRunner(bizapp.internal_ips, deploy_id)
        yml_files = ['/home/foliday/fosun-devopsx/test.yml']
        extra_vars = {'appid': 'demo.fosun.com'}
        runner.run(yml_files, extra_vars)
        utils.get_logger().info("完成执行playbook,deploy_id=" + str(deploy_id))
        wf_service.publish_complete_task(deploy_id, bizapp.app_id)
        utils.get_logger().info("完成执行同步任务,deploy_id=" + str(deploy_id))
    except Exception as e:
        utils.get_logger().error(e)
    return 4
