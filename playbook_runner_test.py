from playbook_runner import PlaybookRunner
# 传入inventory路径
pbrunner = PlaybookRunner('192.168.3.22,', 'test.api.fosun.com')
# 获取服务器磁盘信息
yml_files = ['/home/foliday/fosun-devopsx/test.yml']
extra_vars = {'appid': 'demo.fosun.com'}
pbrunner.run(yml_files, extra_vars)
#结果
result = pbrunner.get_result()
#成功
succ = result['success']
#失败
failed = result['failed']
#不可到达
unreachable = result['unreachable']
