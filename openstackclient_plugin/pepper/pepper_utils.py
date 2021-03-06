from pepper.cli import PepperCli
import sys
import os
import json


class PepperExecutor(object):
    def __init__(self, uri=None, eauth='pam', user='salt', passwd=None):
        """
        https://github.com/saltstack/pepper
        :param uri:
        :param eauth:
        :param user:
        :param passwd:
        """
        self.uri = uri
        self.eauth = eauth
        self.user = user
        self.passwd = passwd

    def execute(self, cmd):
        """
        workaround for invoking pepper functions without
        this function does not provide error handling,
        so user should handle them accordingly
        :param [] cmd: a list of commands
        :return: generator of salt cmd result
        """

        os.environ['SALTAPI_URL'] = self.uri
        os.environ['SALTAPI_EAUTH'] = self.eauth
        os.environ['SALTAPI_USER'] = self.user
        os.environ['SALTAPI_PASS'] = self.passwd

        # manually assemble pass-in values
        if not isinstance(cmd, (list, tuple)):
            cmd = [cmd]
        elif isinstance(cmd, tuple):
            cmd = list(cmd)

        # workaround to override all existing options
        # existing option has two sources: 1. pass-in as command to be executed
        # 2. this method has been previously invoked
        sys.argv = [sys.argv[0]] + cmd

        result_list = []
        cli = PepperCli()
        for exit_code, result in cli.run():
            if exit_code == 0:
                # print(result)
                result_list.append(json.loads(result))
            else:
                raise Exception('error executing command')
        return result_list

    def execute_return_exit_code(self, cmd):
        """
        workaround for invoking pepper functions without
        this function does not provide error handling,
        so user should handle them accordingly
        cmd should return a integer value where 0 stands for success
        :param [] cmd: a list of commands
        :return: generator of salt cmd result
        """

        # os.environ['SALTAPI_URL'] = self.uri
        # os.environ['SALTAPI_EAUTH'] = self.eauth
        # os.environ['SALTAPI_USER'] = self.user
        # os.environ['SALTAPI_PASS'] = self.passwd

        # manually assemble pass-in values
        if not isinstance(cmd, (list, tuple)):
            cmd = [cmd]
        elif isinstance(cmd, tuple):
            cmd = list(cmd)

        # workaround to override all existing options
        # existing option has two sources: 1. pass-in as command to be executed
        # 2. this method has been previously invoked
        sys.argv = [sys.argv[0]] + cmd

        result_list = []
        cli = PepperCli()
        for exit_code, result in cli.run():
            if exit_code == 0:
                for i, j in json.loads(result).get('return', [{}])[0].items():
                    result_list.append(j)
            else:
                raise Exception('error while executing command')
        return result_list


class PepperWrapper(object):
    def __init__(self):
        pass

    def execute(self, dest, *cmd):
        cmd_list = [dest, 'cmd.run'] + list(cmd)
        executor = PepperExecutor()
        res_list = executor.execute_return_exit_code(cmd_list)
        return "\n".join(res_list)
