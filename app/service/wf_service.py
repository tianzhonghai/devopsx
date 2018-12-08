from app import db
from app.models import Deploy, BizApp, WfTask, WfTaskHist, DeployItem
from app.utils import data_dicts, common_util


def create_deploy_task(appid, envid, version, userid, username):
    """
    创建发布任务
    :param appid:
    :param envid:
    :param version:
    :param userid:
    :param username:
    :return:
    """
    createdat = common_util.common_utls.get_format_time()
    # 创建发布任务
    bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == appid).first()
    bizdeploy = Deploy.Deploy(appid, version, envid, userid, username, createdat,
                              data_dicts.DeployResultEnum.PENDING, "", data_dicts.WfActivityConst.confirmVersion)
    db.session.add(bizdeploy)
    db.session.commit()

    # 增加待办任务
    wftaskhist = WfTaskHist.WfTaskHist(bizdeploy.deploy_id,
                                       data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.created),
                                       data_dicts.WfActivityConst.created, userid, username,
                                       createdat)
    wftask = WfTask.WfTask(bizdeploy.deploy_id,
                           data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.confirmVersion),
                           data_dicts.WfActivityConst.confirmVersion, bizapp.test_id, bizapp.test_account, createdat)

    db.session.add(wftask)
    db.session.add(wftaskhist)
    db.session.commit()

    db.session.close()


def confirm_version_task(task_id, deploy_id, app_id, version):
    """
    确认版本任务
    :param task_id:
    :param deploy_id:
    :param app_id:
    :param version:
    :return:
    """
    createdat = common_util.common_utls.get_format_time()
    db.session.execute(
        'UPDATE biz_deploy SET app_version=:app_version, deploy_result=:deploy_result, wf_status=:wf_status WHERE deploy_id=:deploy_id',
        {"app_version": version, "deploy_result": data_dicts.DeployResultEnum.PENDING,
         "wf_status": data_dicts.WfActivityConst.confirmPublish, "deploy_id": deploy_id})
    # db.session.commit()
    # get app info
    bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == app_id).first()
    oldwftask = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == task_id).first()
    # 增加待办任务
    wftask = WfTask.WfTask(deploy_id,
                           data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.confirmPublish),
                           data_dicts.WfActivityConst.confirmPublish, bizapp.dev_id, bizapp.dev_account, createdat)
    wftaskhist = WfTaskHist.WfTaskHist(deploy_id, oldwftask.act_name, oldwftask.act_type,
                                       bizapp.dev_id, bizapp.dev_account, createdat)

    db.session.add(wftask)
    db.session.add(wftaskhist)

    db.session.execute('DELETE FROM wf_task WHERE task_id=' + str(task_id))
    db.session.commit()

    db.session.close()


def confirm_publish_task(task_id, deploy_id, app_id):
    """
    确认发布任务
    :param task_id:
    :param deploy_id:
    :param app_id:
    :return:
    """
    createdat = common_util.common_utls.get_format_time()
    db.session.execute(
        'UPDATE biz_deploy SET deploy_result=:deploy_result, wf_status=:wf_status WHERE deploy_id=:deploy_id',
        {"deploy_result": data_dicts.DeployResultEnum.PENDING, "wf_status": data_dicts.WfActivityConst.publishing,
         "deploy_id": deploy_id})
    db.session.commit()
    # get app info
    bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == app_id).first()
    oldwftask = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == task_id).first()
    # 增加待办任务
    # wftask = WfTask.WfTask(deploy_id,
    #                        data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.publishing),
    #                        data_dicts.WfActivityConst.publishing, bizapp.dev_id, bizapp.dev_account, createdat)
    wftaskhist = WfTaskHist.WfTaskHist(deploy_id, oldwftask.act_name, oldwftask.act_type,
                                       bizapp.dev_id, bizapp.dev_account, createdat)

    # db.session.add(wftask)
    db.session.add(wftaskhist)

    db.session.execute('DELETE FROM wf_task WHERE task_id=' + str(task_id))
    db.session.commit()

    db.session.close()


def publish_complete_task(deploy_id, app_id):
    """
    发布完成
    :param deploy_id:
    :param app_id:
    :return:
    """
    createdat = common_util.common_utls.get_format_time()
    # 所有任务都成功
    deploy_tasks = db.session.query(DeployItem.BizTask).filter_by(deploy_id=deploy_id).values('deploy_id', 'result_status')
    flag = True
    for dt in deploy_tasks:
        if dt[1] != "ok":
            flag = False

    if flag:
        # 发布成功后测试验证
        db.session.execute(
            "UPDATE biz_deploy SET deploy_result = 1, wf_status = '"+data_dicts.WfActivityConst.published + "' WHERE deploy_id = " + str(deploy_id))

        bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == app_id).first()
        wftask = WfTask.WfTask(deploy_id,
                               data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.test),
                               data_dicts.WfActivityConst.test, bizapp.test_id, bizapp.test_account, createdat)
        db.session.add(wftask)
        db.session.commit()
    else:
        # 发布失败，流程结束
        db.session.execute(
            "UPDATE biz_deploy SET deploy_result = 2, wf_status = '"+data_dicts.WfActivityConst.published+"' WHERE deploy_id = " + str(deploy_id))
        db.session.commit()

    db.session.close()


def test_deploy_task(task_id, deploy_id, app_id, deploy_result):
    """
    测试发布结果
    :param task_id:
    :param deploy_id:
    :param app_id:
    :param deploy_result:
    :return:
    """
    createdat = common_util.common_utls.get_format_time()
    bizapp = BizApp.BizApp.query.filter(BizApp.BizApp.app_id == app_id).first()
    oldwftask = WfTask.WfTask.query.filter(WfTask.WfTask.task_id == task_id).first()
    if deploy_result == 1:
        db.session.execute(
        'UPDATE biz_deploy SET deploy_result=:deploy_result, wf_status=:wf_status WHERE deploy_id=:deploy_id',
        {"deploy_result": data_dicts.DeployResultEnum.SUCCESS,
         "wf_status": data_dicts.WfActivityConst.close, "deploy_id": deploy_id})
        db.session.commit()
    else:
        db.session.execute(
            'UPDATE biz_deploy SET deploy_result=:deploy_result, wf_status=:wf_status WHERE deploy_id=:deploy_id',
            {"deploy_result": data_dicts.DeployResultEnum.FAIL,
             "wf_status": data_dicts.WfActivityConst.close, "deploy_id": deploy_id})
        db.session.commit()
    # 增加待办任务
    wftask = WfTask.WfTask(deploy_id,
                           data_dicts.WfActivityConst.convert_to_desc(data_dicts.WfActivityConst.close),
                           data_dicts.WfActivityConst.close, bizapp.dev_id, bizapp.dev_account, createdat)
    wftaskhist = WfTaskHist.WfTaskHist(deploy_id, oldwftask.act_name, oldwftask.act_type,
                                       bizapp.dev_id, bizapp.dev_account, createdat)

    db.session.add(wftask)
    db.session.add(wftaskhist)

    db.session.execute('DELETE FROM wf_task WHERE task_id=' + str(task_id))
    db.session.commit()

    db.session.close()
