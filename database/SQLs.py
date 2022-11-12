SELECT_ALL_USERS_WHERE_EMAIL_AND_PASSWORD = """
    select * from Users where email_address = '{email}' and password = '{password}'
"""

SELECT_ALL_PROJECTS_WHERE_COMPANY = """
    select * from Projects where companyId = {company_id}
"""

SELECT_ALL_TASKS_IN_PROJECTS = """
    select * from Tasks where projectId in {project_id_tuple}
"""

SELECT_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select duration from ProjectTimeLines where user = {user} and project_id like {project_id} and day_format like '{today}' 
"""

SELECT_TASKID_AND_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select sub_id, duration from ProjectTimeLines where user = {user} and project_id like {project_id} and day_format like '{today}' 
"""



SELECT_ID_AND_NAME_FROM_APPLICATIONS = """
    select id, name from Applications
"""

SELECT_DURATIONS_WHERE_USER_AND_DATE = """
    select duration from ProjectTimeLines where user = {user} and day_format like '{today}' 
"""

SELECT_ALL_TIMELINES_WHERE_USER_AND_SYNC_IS_ZERO = """
    select * from ProjectTimeLines where user = {user} and sync = 0 
"""

SELECT_ALL_SCREENSHOTS_WHERE_USER_AND_SYNC_IS_ZERO = """
    select * from Screenshots where user = {user} and sync = 0 
"""

######################################### INSERTION STATMENTS #########################################
INSERT_NEW_ROW_INTO_IDLE = """
    insert into Idles
        (id, project_id, task_id, duration, end, start, sync)
    VALUES
        ({id}, {project_id}, {task_id}, {duration}, {end}, {start}, {sync})
"""

INSERT_NEW_ROW_INTO_APPLICATIONS = """
    insert into Applications
        (id, user, name, path, version, description, sync)
    VALUES
        ('{id}', {user}, '{name}', '{path}', '{version}', '{description}', {sync})
"""

INSERT_NEW_ROW_INTO_WINDOWS = """
    insert into Windows
        (id, application_id, title, window_url, start_date, url, domain_url, sync)
    VALUES
        ('{id}', '{application_id}', '{title}', '{window_url}', '{start_date}', '{url}', '{domain_url}', {sync})
"""

INSERT_NEW_ROW_INTO_PROJECT_TIMELINE = """
    insert into ProjectTimeLines
        (project_id, current_project_line_id, sub_id, time_start, time_end, user, entry_id, duration, date_ended, sync, day_format)
    VALUES
        ({project_id}, {current_project_line_id}, {sub_id}, '{time_start}', '{time_end}', {user}, '{entry_id}', '{duration}', '{date_ended}', {sync}, '{day_format}')
"""