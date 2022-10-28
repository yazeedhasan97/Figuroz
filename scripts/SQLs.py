SELECT_ALL_USERS_WHERE_EMAIL_AND_PASSWORD = """
    select * from User where email_address = '{email}' and password = '{password}'
"""

SELECT_ALL_PROJECTS_WHERE_COMPANY = """
    select * from Project where companyId = {company_id}
"""

SELECT_ALL_TASKS_IN_PROJECTS = """
    select * from Task where projectId in {project_id_tuple}
"""

SELECT_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select duration from ProjectTimeLine where user = {user} and project_id like {project_id} and day_format like '{today}' 
"""

SELECT_TASKID_AND_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select sub_id, duration from ProjectTimeLine where user = {user} and project_id like {project_id} and day_format like '{today}' 
"""

INSERT_NEW_ROW_PROJECT_TME_LINE = """
    insert into ProjectTimeLine
        (project_id, current_project_line_id, sub_id, time_start, time_end, user, entry_id, duration, date_ended, sync, day_format)
    VALUES
        ({project_id}, '{current_project_line_id}', {sub_id}, '{time_start}', '{time_end}', {user}, '{entry_id}', '{duration}', '{date_ended}', {sync}, '{day_format}')
"""

# SELECT_ALL_SETTINGS = """
#     select * from Settings
# """

SELECT_DURATIONS_WHERE_USER_AND_DATE = """
    select duration from ProjectTimeLine where user = {user} and day_format like '{today}' 
"""

SELECT_ALL_TIMELINES_WHERE_USER_AND_SYNC_IS_ZERO = """
    select * from ProjectTimeLine where user = {user} and sync = 0 
"""
