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
    """
    Main function for command entry point. Gets projects or get project details depending on the parameters give form
    command line
    :return: print out data taken from Gitlab to pass Zabbix Agent
    """
    gitlab_url = json.load(open(args.config_file))["gitlab_url"]
    gitlab_token = json.load(open(args.config_file))["gitlab_token"]
    project_name_regex = json.load(open(args.config_file))["project_name_regex"]
    owned = json.load(open(args.config_file))["owned"]
    action = args.action
    logging.debug("gitlab-url:[%s]", gitlab_url)
    logging.debug("gitlab_token:[%s]", gitlab_token)
    logging.debug("project_name_regex:[%s]", project_name_regex)
    logging.debug("owned:[%s]", owned)
    logging.debug("action:[%s]", action)
    gl = GitLab(gitlab_url, gitlab_token, project_name_regex, owned)
    if action == actions[0]:
        logging.debug("Get projects")
        print gl.get_projects()
    elif action == actions[1]:
        logging.debug("Get project")
        print gl.get_project(args.project_id)


class GitLab:
    """
    Main class for Gitlab Integration
    """
    gl = None

    def __init__(self, gitlab_url, gitlab_token, project_name_regex, owned=True):
        """
        Init method of the class.
        :param gitlab_url: GitLab url to connect. Ex: https://gitlab.com
        :param gitlab_token: Personal Access token which is created in settings of your profile
        :param project_name_regex: Reqular expression for filtering projects. This way you filter the data
        :param owned: set True to get projects owned by the user, set False to get all projects
        which will be sent to Zabbix Agent.
        """
        logging.debug("Init method")
        self.project_name_regex = project_name_regex
        self.regex = re.compile(project_name_regex)
        self.owned = owned
        self.gl = gitlab.Gitlab(gitlab_url, gitlab_token)

    def get_projects(self):
        """
        This method gets projects information from GitLab depending on the Regular Expression given in Init method.
        Prints out the result json data.
        :return: print out projects id and name data in Zabbix Agent Json format.
        """
        data = []
        if self.owned:
            projects = self.gl.projects.list(owned=True)
        else:
            projects = self.gl.projects.list(all=True)

        for project in projects:
            logging.debug("Looping in projects")
            p_data = {"{#ID}": str(project.id), "{#NAME}": str(project.name)}
            logging.debug("Project Json Data:[%s]", p_data)
            if self.regex.match(str(project.name)):
                logging.debug("Pass regex control, add to data")
                data.append(p_data)
            logging.debug("Return data:[%s]", data)
        return self._construct_zabbix_json(data)

    def get_project(self, project_id):
        """
        This method get project infromation from GitLab. Prints out the result json data.
        :param project_id: Id of the project.
        :return: print out project related data in Standard Json format
        """
        logging.debug("Get project information with Id:[%s]", project_id)
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
        logging.debug("Project data:[%s]", data)
        return json.dumps(data)

    def _construct_zabbix_json(self, data):
        """
        This method converts standard json data to Zabbix Agent Json format.
        :param data: json data to convert
        :return: json data for Zabbix Agent Json format.
        """
        logging.debug("Convert data to Zabbix Agent Json format")
        zabbix_data = {"data": data}
        logging.debug("Zabbix Agent data:[%s]", data)
        return json.dumps(zabbix_data)


if __name__ == "__main__":
    main()
