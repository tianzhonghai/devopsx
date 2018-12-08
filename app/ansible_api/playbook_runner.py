from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import os, json
from .. import utils, db
from ..models import DeployItem


TEMPLATE_DIR = ""


class PlaybookRunner(object):
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, resource, deploy_id):
        self.resource = resource
        self.inventory = None
        self.variable_manager = None
        # self.loader = None
        # self.options = None
        # self.passwords = None
        self.callback = None

        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'timeout', 'remote_user',
                                         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args',
                                         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass',
                                         'verbosity', 'diff', 'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        self.loader = DataLoader()

        self.options = Options(connection='smart', module_path='/usr/share/ansible', forks=100, timeout=10,
                               remote_user='root', ask_pass=False, private_key_file=None, ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
                               become_user='root', ask_value_pass=False, verbosity=None, check=False, diff=False,
                               listhosts=False,
                               listtasks=False, listtags=False, syntax=False)

        self.passwords = dict(vault_pass='')
        self.inventory = InventoryManager(loader=self.loader, sources=self.resource)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.deploy_id = deploy_id

    def run(self, file_paths, extra_vars):
        """
        run ansible palybook
        """
        try:
            self.callback = ResultsCollector(self.deploy_id)
            # logger.info('ymal file path:%s' % filenames)
            # template_file = TEMPLATE_DIR  # 模板文件的路径
            # if not os.path.exists(template_file):
            #   logger.error('%s 路径不存在 ' % template_file)
            #    sys.exit()

            # extra_vars = {}  # 额外的参数 sudoers.yml以及模板中的参数，它对应ansible-playbook test.yml --extra-vars "host='aa' name='cc' "
            # host_list_str = ','.join([item for item in host_list])
            # extra_vars['host_list'] = host_list_str
            # extra_vars['username'] = role_name
            # extra_vars['template_dir'] = template_file
            # extra_vars['command_list'] = temp_param.get('cmdList')
            # extra_vars['role_uuid'] = 'role-%s' % role_uuid
            self.variable_manager.extra_vars = extra_vars

            # actually run it
            executor = PlaybookExecutor(
                playbooks=file_paths, inventory=self.inventory, variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options, passwords=self.passwords,
            )
            executor._tqm._stdout_callback = self.callback
            executor.run()
        except Exception as e:
            # logger.error("run_playbook:%s"%e)
            pass


class ResultsCollector(CallbackBase):

    def __init__(self, deploy_id, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.deploy_id = deploy_id

    def v2_runner_on_unreachable(self, result):
        ResultsCollector.add_task(self.deploy_id, "unreachable", result)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        ResultsCollector.add_task(self.deploy_id, "ok", result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        ResultsCollector.add_task(self.deploy_id, "failed", result)

    def v2_runner_on_skipped(self, result):
        ResultsCollector.add_task(self.deploy_id, "skipped", result)

    def v2_runner_on_no_hosts(self, task):
        ResultsCollector.add_task_without_result(self.deploy_id, "no_host", 'test')

    @staticmethod
    def add_task(deploy_id, result_status, result):
        deployItem = DeployItem.DeployItem(deploy_id, result_status, result.task_name, result._host.get_name(), json.dumps(result._result))
        db.session.add(deployItem)
        db.session.commit()
        db.session.close()

    @staticmethod
    def add_task_without_result(deploy_id, result_status, task_name):
        deployItem = DeployItem.DeployItem(deploy_id, result_status, task_name, '', '')
        db.session.add(deployItem)
        db.session.commit()
        db.session.close()
