#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

import paramiko

from paddle_api.config_spec import CompositeSpecNode, ArraySpecNode, StringSpecNode
from paddle_api.plugin import PaddlePlugin, PaddleTask, plugin, TaskDefaultGroups
from paddle_api.project import PaddleProject, ExtendedPaddleProject


@plugin(name="remoter")
class Remoter(PaddlePlugin):
    async def tasks(self, project: PaddleProject) -> List[PaddleTask]:
        return [RunRemoteExecution(project)]

    async def configure(self, project: ExtendedPaddleProject) -> None:
        # Example of remoter configuration
        #
        # remoter:
        #   - script: resource/simple-network.py
        #     requirements: resources/requirements.txt
        #     others:
        #       - resources/file-1.txt
        #       - resources/file-2.txt
        #     input-file: resources/input.txt
        #     output:
        #       directory: resources
        #       file: output.txt
        #
        #     machines:
        #       - user: admin
        #         password: secret
        #         host: localhost
        #         working-dir: /home/project/venv/bin/python3
        #         py-interpreter-path: /home/project/venv/bin/python3
        #
        #       - user: admin
        #         password: secret
        #         host: otherhost
        #         working-dir: /home/project/venv/bin/python3
        #         py-interpreter-path: /home/project/venv/bin/python3`
        #
        spec_root = project.config_spec.root
        remoter_config_spec = ArraySpecNode(
            description="List of configuration parameters blocks for remoter plugin's scenario",
            items=CompositeSpecNode(
                required=["script", "input-file", "output", "machines"],
                properties={
                    "script": StringSpecNode(description="Path to script to be executed"),
                    "requirements": StringSpecNode(
                        description="Path to file requirements.txt to be installed on remote machines"),
                    "others": ArraySpecNode(
                        title="Paths to files that are needed to execute the script",
                        items=StringSpecNode()
                    ),
                    "input-file": StringSpecNode("Path to a file with input data to be shared between remote machines"),
                    "output": CompositeSpecNode(
                        required=["file"],
                        properties={
                            "directory": StringSpecNode(description="Directory to save results"),
                            "file": StringSpecNode(description="File to save results")
                        }
                    ),
                    "machines": ArraySpecNode(
                        description="List of configuration parameters blocks to execute script on remotes machines",
                        items=CompositeSpecNode(
                            required=["user", "host", "working-dir"],
                            properties={
                                "user": StringSpecNode(description="User name on remote machine"),
                                "password": StringSpecNode(description="User password on remote machine"),
                                "host": StringSpecNode(description="Hostname or IP of remote machine"),
                                "working-dir": StringSpecNode(description="Working directory for script execution"),
                                "py-interpreter-path": StringSpecNode(description="Path to python interpreter")
                            }
                        )
                    )
                }
            ),
        )
        spec_root.properties["remoter"] = remoter_config_spec


@dataclass
class ExecutionData:
    script_path: str
    requirements_file_path: str
    others: List[str]
    input: str
    output: str
    username: str
    password: str
    host: str
    working_dir: str
    interpreter_path: str


class RunRemoteExecution(PaddleTask):
    def __init__(self, project: PaddleProject) -> None:
        PaddleTask.__init__(self, project, identifier="runRemoteExecution", group=TaskDefaultGroups.APP.value, deps=[])

    async def initialize(self) -> None:
        pass

    async def act(self) -> None:
        for scenario in self.project.config.list("remoter"):
            output_dir = scenario["output"].get("directory", ".")
            open(f'{output_dir}/{scenario["output"]["file"]}', "w").close()
            for machine in scenario["machines"]:
                self.__execute_scenario(ExecutionData(
                    script_path=scenario["script"],
                    requirements_file_path=scenario.get("requirements"),
                    others=scenario.get("others"),
                    input=scenario["input-file"],
                    output=scenario["output"]["file"],
                    username=machine["user"],
                    password=machine.get("password"),
                    host=machine["host"],
                    working_dir=machine["working_dir"],
                    interpreter_path=machine.get("py-interpreter-path", "python")
                ), f'{output_dir}/{scenario["output"]["file"]}')

    def __execute_scenario(self, data: ExecutionData, output_file: str) -> None:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(data.host, username=data.username, password=data.password)

        sftp = client.open_sftp()
        sftp.put(f"{self.project.working_dir}/{data.script_path}", f'{data.working_dir}/{data.script_path}')
        sftp.put(f"{self.project.working_dir}/{data.requirements_file_path}",
                 f'{data.working_dir}/{data.requirements_file_path}')
        sftp.put(f"{self.project.working_dir}/{data.input}", f"{data.working_dir}/input.txt")
        for other in data.others:
            sftp.put(f"{self.project.working_dir}/{other}", f'{data.working_dir}/{other}')

        client.exec_command(f'cd "{data.working_dir}"')
        # stdin, stdout, stderr
        client.exec_command(
            f'{data.interpreter_path} -m pip install -r {data.working_dir}/{data.requirements_file_path}')
        client.exec_command(f"{data.interpreter_path} {data.working_dir}/{data.script_path}")
        remote_file = sftp.open(f"{data.working_dir}/{data.output}")
        try:
            for line in remote_file:
                with open(output_file, "a") as file:
                    file.write(line)
        finally:
            remote_file.close()
        sftp.close()
        client.close()
