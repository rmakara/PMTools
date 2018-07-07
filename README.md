# PMTools

## General information

Company uses a few tools to track the progress of each project. We use Jira as the issue tracker but also we use external tool to track time reports. That causes a problem when we have data in two systems instead of one. We want to integrate both - issue tracker and time tracker - to keep all required data in both systems so we can use software features in a better way, reduce company's costs, avoid loosing money on not correctly tracked man-hours, make specialists' live easier by simplifying reporting process.

These simple scripts allow you to integrate data between Jira and Toggl. 

## Rewrite tasks from Jira to Toggl

It is the first step in our process. The script lets you to rewrite Jira issues to Toggl. By doing that you are able to use some kind of autocomplete in Toggl to add your time entries to specified Jira task.

## Rewrite time entries from Toggl to Jira

It is the second step in our process. When you have your Toggl reports in the time reporting system then you can rewrite it to Jira. Unfortunately, the script adds all the time entries as "your user" instead the original one in Toggl.

### Risks

* The script does not look for duplicates.
* If you run the script 2 times then you will duplicate worklogs in Jira.
