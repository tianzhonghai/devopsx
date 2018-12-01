from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import os


TEMPLATE_DIR = ""
class PlaybookRunner(object):
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, resource, appid):
        self.resource = resource
        self.inventory = None
        self.variable_manager = None
        # self.loader = None
        # self.options = None
        # self.passwords = None
        self.callback = None
        self.results_raw = {}

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
        self.appid = appid

    def run(self, file_paths, extra_vars):
        """
        run ansible palybook
        """
        try:
            self.callback = ResultsCollector(self.appid)
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

    def get_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            self.results_raw['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            self.results_raw['failed'][host] = result._result

        for host, result in self.callback.host_unreachable.items():
            self.results_raw['unreachable'][host] = result._result['msg']

            # print "Ansible执行结果集:%s"%self.results_raw
        return self.results_raw


class ResultsCollector(CallbackBase):

    def __init__(self,appid, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.appid = appid

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result
