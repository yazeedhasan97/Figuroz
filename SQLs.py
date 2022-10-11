SELECT_ALL_USERS_WHERE_NAME_AND_PASSWORD = """
    select * from User where name = '{name}' and password = '{password}'
"""

SELECT_ALL_TASKS_WHERE_PROJECTS_AND_USER = """
    select * from Task where project_id in {project_id_tuple} and m_user = '{user}'
"""

SELECT_ALL_PROJECTS_WHERE_USER_AND_COMPANY = """
    select * from Project where m_user = '{user}' and company_id = '{company_id}' 
"""

SELECT_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select duration from ProjectTimeLine where user like '{user}' and project_id like '{project_id}' and day_format like '{today}' 
"""

SELECT_TASKID_AND_DURATION_AND_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE = """
    select sub_id, duration from ProjectTimeLine where user like '{user}' and project_id like '{project_id}' and day_format like '{today}' 
"""

INSERT_NEW_ROW_PROJECT_TME_LINE = """
    insert into ProjectTimeLine
        (project_id, current_project_line_id, sub_id, time_start, time_end, user, entry_id, duration, date_ended, sync, day_format)
    VALUES
        ({project_id}, '{current_project_line_id}', {sub_id}, '{time_start}', '{time_end}', {user}, '{entry_id}', '{duration}', '{date_ended}', {sync}, '{day_format}')
"""
