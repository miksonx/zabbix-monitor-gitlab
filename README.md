# Monitor GitLab Projects with Zabbix
This repo includes necessary scripts/templates for monitoring GitLab Project details over Zabbix.
By using this solution you can gather and monitor below information over Zabbix.

Per Project:
- Number of environments
- Number of Merge Requests
- Number of Opened Opened Requests
- Number of Opened Closed Requests
- Number of Opened Merged Merge Requests
- Number of Pipelines
- Number of Success Pipelines
- Number of Pending Pipelines

With Discovery Rules feature of Zabbix, you do not need to add projects manually to Zabbix.
Discovery rules automatically discover projects on GitLab and gather above information per project.
You can filter projects which will be discovered by using regex in config or in Zabbix Template.

## Solution Details
This solution;
 - gather GitLab project details by running custom python scripts
 - Use Zabbix Agent UserParameter feature to send data to Zabbix Server
 - Use Discovery Rules to discover projects in GitLab by running python script
 - Use Discovery Rule Items to gather information from Gitlab by running python script
 
## Requirements
This solution tested on below environments. You may experience problem in different versions.
- Zabbix Server 4.0.5
- Zabbix Agent 3.4.15
- Python 2.7.5
- Ansible 2.7.9

## Installation
You need Ansible to install scripts and configure Zabbix Agent. Follow the steps below:

* Clone this repository to Ansible installed host
* Edit ```hosts``` file in the directory ```ansible```
    *  **Suggested:** make installation to 1 host which Zabbix Agent installed
* Edit ```vars.yml``` file in the directory ```ansible/vars```
    * zabbix_agent_directory_path: Root path of Zabbix Agent
    * gitlab_url: Url address of the Gitlab Server
    * gitlab_token: Personal Access Token
    * project_name_regex: Regular expression for filtering projects (by project names)
    * owned: Set true to get your projects, set false to get all projects
        * If you are goint to use this on GitLab itself, set ```owned``` true
* Run below command to start installation
```ansible-playbook -i hosts playbook/install.yml```
* Import Zabbix Template ```GitLab``` by using template file in ```zabbix/templates/zbx_gitlab_template.xml```

After all you will start to see Zabbix gathering data from GitLab.

Now, you are ready to use graphics in GitLab template.

## Important
You may need to configure Zabbix Agent and Zabbix Server depending on the number of projects you want to monitor.
For this, set ```Timeout``` variable to ```30``` in the configs of both Zabbix Agent and Zabbix Server.
