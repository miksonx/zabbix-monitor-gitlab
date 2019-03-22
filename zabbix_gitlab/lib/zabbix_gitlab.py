#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This includes neccessary functions/methods getting information from gitlab for zabbix agent
"""
__author__ = "Aytunc Beken"
__copyright__ = "Copyright (C) 2019 Aytunc Beken"
__version__ = "0.1"
__license__ = "MIT"
__maintainer__ = "Aytunc Beken"
__email__ = "aytuncbeken.ab@gmail.com"
__status__ = "Production"

# Generic / Built-In
import logging
import argparse
import gitlab
import json
import re

# Set argument parser
actions = ['get-projects', 'get-project']
parser = argparse.ArgumentParser(
    description="Gitlab commands library for getting information from GitLab and convert to zabbix agent json format")
parser.add_argument('--config-file', dest="config_file", action="store", required=True,
                    help="Json Config file path")
parser.add_argument('--project-id', dest="project_id", action="store", required=False,
                    help="Project Id of Gitlab Project")
parser.add_argument('--action', dest="action", action="store", choices=actions, required=True,
                    help="Action to perform")
parser.add_argument('--debug', dest="debug", action="store_const", required=False, help="debug", const="debug")

args = parser.parse_args()

# Logging Configuration
logger = logging.getLogger()
if args.debug is None:
    logger.setLevel(logging.ERROR)
else:
    logger.setLevel(logging.DEBUG)


def main():
    gitlab_url = json.load(open(args.config_file))["gitlab_url"]
    gitlab_token = json.load(open(args.config_file))["gitlab_token"]
    project_name_regex = json.load(open(args.config_file))["project_name_regex"]
    action = args.action
    logging.debug("token:[%s]", gitlab_token)
    logging.debug("gitlab-url:[%s]", gitlab_url)
    gl = GitLab(gitlab_url, gitlab_token, project_name_regex)
    if action == actions[0]:
        print gl.get_projects()
    elif action == actions[1]:
        print gl.get_project(args.project_id)


class GitLab:
    gl = None

    def __init__(self, gitlab_url, gitlab_token, project_name_regex):
        self.project_name_regex = project_name_regex
        self.regex = re.compile(project_name_regex)
        self.gl = gitlab.Gitlab(gitlab_url, gitlab_token)

    def get_projects(self):
        data = []
        for project in self.gl.projects.list(all=True):
            p_data = {"{#ID}": str(project.id), "{#NAME}": str(project.name)}
            if self.regex.match(str(project.name)):
                data.append(p_data)
        return self._construct_zabbix_json(data)

    def get_project(self, project_id):
        data = {}
        project = self.gl.projects.get(project_id)
        data["projectName"] = project.name
        pipelines = project.pipelines.list(all=True)
        data["pipelineTotal"] = len(pipelines)
        data["pipelineSuccessTotal"] = len([p for p in pipelines if p.status == "success"])
        data["pipelinePendingTotal"] = len([p for p in pipelines if p.status == "pending"])
        merge_requests = project.mergerequests.list(all=True)
        data["mergeRequests"] = len(merge_requests)
        data["openedMergeRequests"] = len([m for m in merge_requests if m.state == "opened"])
        data["closedMergeRequests"] = len([m for m in merge_requests if m.state == "closed"])
        data["mergedMergeRequests"] = len([m for m in merge_requests if m.state == "merged"])
        environments = project.environments.list(all=True)
        data["environmentTotal"] = len(environments)
        return json.dumps(data)

    def _construct_zabbix_json(self, data):
        zabbix_data = {"data": data}
        return json.dumps(zabbix_data)


if __name__ == "__main__":
    main()
