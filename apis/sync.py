import pandas as pd
import numpy as np
import requests
from datetime import timedelta
from database import db, SQLs
from common import consts, utils
from database.models import User, Task, Project
from scripts.controllers import MainController


class Sync:
    __BASE_AUTHENTICATION_URL = "http://figurozapi-test.eu-central-1.elasticbeanstalk.com/"
    __SEND_FORGET_PASSWORD_URL = __BASE_AUTHENTICATION_URL + "api/UserAccounts/ForgetPassword"
    __GET_USER_SYNC_FLAG_URL = __BASE_AUTHENTICATION_URL + "api/UserAccounts/GetUserSyncFlag"
    __SEND_LOGIN_URL = __BASE_AUTHENTICATION_URL + "api/Authenticate/Login"
    __GET_TASK_URL = __BASE_AUTHENTICATION_URL + "api/Tasks"
    __GET_PROJECT_URL = __BASE_AUTHENTICATION_URL + "api/Projects/ByStatus/1"
    __INSERT_TIMELINES_URL = __BASE_AUTHENTICATION_URL + "api/UserTaskDurationDetail/BulkInsert"
    __TIMEOUT = 300
    __HEADERS = {
        'User-Agent': 'Custom Agent 0.0',
        'Content-Type': "application/json",
        'charset': ':utf-8',
        'accept': 'text/plain',
        'Server': 'nginx/1.20.0',
        # "Authorization": "",
    }
    __ACCEPTED_STATUS_CODE = ['10', '20', '30']

    @classmethod
    def send_forget_password_request(cls, email_address):
        print('Send Forget Password Request')
        response = None
        try:
            params = {
                'emailAddress': email_address,
            }
            response = requests.post(
                url=Sync.__SEND_FORGET_PASSWORD_URL,
                params=params,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS
            )
            print(response.status_code)
            print(response.headers)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                return response.json()
            else:
                return False

        except requests.exceptions.HTTPError as e:
            print(e)
            e.args = e.args + ('APIs might be down',)
            raise e
        finally:
            if response is not None:
                response.close()

    @classmethod
    def send_login_request(cls, email_address, password):
        print('Send Login Request')
        response = None
        try:
            params = {
                'emailAddress': email_address,
                'password': password
            }
            response = requests.post(
                url=Sync.__SEND_LOGIN_URL,
                json=params,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS,
            )
            print(response.status_code)
            print(response.headers)
            print(response.url)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                res = response.json()
                Sync.__HEADERS['Authorization'] = "Bearer " + res['token']
                user = User(
                    token=res['token'],
                    refresh_token=res['refreshToken'],
                    id=res['user']['id'],
                    company_id=res['user']['companyId'],
                    username=res['user']['username'],
                    email_address=res['user']['emailAddress'],
                    password=password,
                    status=res['user']['status'],
                    access_level=res['user']['accessLevel'],
                    code=res['user']['code'],
                    screenshot_interval=res['user']['screenshotInterval'],
                    can_edit_time=res['user']['canEditTime'],
                    blur_screen=res['user']['blurScreen'],
                    receive_daily_report=res['user']['receiveDailyReport'],
                    inactive_time=res['user']['inactiveTime'],
                    can_delete_screencast=res['user']['canDeleteSceencast'],
                    owner_user=res['user']['ownerUser'],
                    sync_data=res['user']['syncData'],
                    profile_image=res['user']['profileImage'],
                )

                from common import utils
                df = utils.create_df_from_object(user).convert_dtypes(infer_objects=True)
                df[['group_members', 'group_managers', 'timezone', 'current_app_version', 'user_location']] = df[
                    ['group_members', 'group_managers', 'timezone', 'current_app_version', 'user_location']].astype(str)
                MainController.DB_CONNECTION.write(df, 'User', if_exists='replace')

                return user

            else:
                return False

        except requests.exceptions.HTTPError as e:
            print(e)
            e.args = e.args + ('APIs might be down',)
            raise e
        finally:
            if response is not None:
                response.close()

        pass

    @classmethod
    def get_projects_request(cls, token):
        print('Get Projects Request')
        Sync.__HEADERS['Authorization'] = "Bearer " + token
        response = None
        try:
            params = {
                # 'emailAddress': email_address,
            }
            response = requests.get(
                url=Sync.__GET_PROJECT_URL,
                params=params,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS
            )
            print(response.status_code)
            print(response.headers)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                projects_lst = response.json()
                projects = [Project(
                    id=project['id'],
                    name=project['projectName'].title(),
                    company_id=project['companyId'],
                    status=project['status'],
                    project_access=project['projectAccess'],
                    project_groups=project['projectGroups'],
                    project_members=project['projectMembers'],
                ) for project in projects_lst]
                df = pd.DataFrame(projects_lst)
                df[['projectGroups', 'projectMembers']] = df[['projectGroups', 'projectMembers']].astype(str)
                MainController.DB_CONNECTION.write(df, 'Project', if_exists='replace')
                return projects
            else:
                return False

        except requests.exceptions.HTTPError as e:
            print(e)
            e.args = e.args + ('APIs might be down',)
            raise e
        finally:
            if response is not None:
                response.close()

    @classmethod
    def get_tasks_request(cls, token):
        print('Get Projects Request')
        Sync.__HEADERS['Authorization'] = "Bearer " + token
        response = None
        try:
            params = {
                # 'emailAddress': email_address,
            }
            response = requests.get(
                url=Sync.__GET_TASK_URL,
                params=params,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS
            )
            print(response.status_code)
            print(response.headers)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                tasks_lst = response.json()
                tasks = [Task(
                    project_id=task['projectId'],
                    id=task['id'],
                    status=task['status'],
                    name=task['taskName'].title(),
                ) for task in tasks_lst]
                df = pd.DataFrame(tasks_lst)
                MainController.DB_CONNECTION.write(df, 'Task', if_exists='replace')
                return tasks
            else:
                return False

        except requests.exceptions.HTTPError as e:
            print(e)
            e.args = e.args + ('APIs might be down',)
            raise e
        finally:
            if response is not None:
                response.close()

    @classmethod  # TODO: needs more consideration # TODO: not sure we need this API.
    def get_user_sync_flag_request(cls, email_address, password, token):
        print('Get Projects Request')
        Sync.__HEADERS['Authorization'] = "Bearer " + token
        response = None
        try:
            params = {
                # 'emailAddress': email_address,
            }
            response = requests.get(
                url=Sync.__GET_USER_SYNC_FLAG_URL,
                params=params,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS
            )
            print(response.status_code)
            print(response.headers)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                res = response.json()
                if res == 1:
                    return res
                else:
                    return False
            else:
                return False

        except requests.exceptions.HTTPError as e:
            print(e)
            e.args = e.args + ('APIs might be down',)
            raise e
        finally:
            if response is not None:
                response.close()

    @classmethod
    def update_project_timelines_request(cls, user, ):
        print('Update Project Timeline Request')
        Sync.__HEADERS['Authorization'] = "Bearer " + user.token
        response = None
        df = db.execute(SQLs.SELECT_ALL_TIMELINES_WHERE_USER_AND_SYNC_IS_ZERO.format(
            user=user.id
        ), conn_s=MainController.DB_CONNECTION).convert_dtypes(infer_objects=True, )
        df['project_id'] = df['project_id'].astype(np.int64)
        df['sub_id'] = df['sub_id'].astype(np.int64)
        df['user'] = df['user'].astype(np.int64)
        df['sync'] = df['sync'].astype(np.int64)
        data = df.drop(
            ['project_id', 'current_project_line_id', 'sync', 'day_format', 'time_start', 'time_end'],
            axis=1
        )

        data.columns = ["taskId", "userId", "id", "duration", "startDate"]
        data['startDate'] = pd.to_datetime(data['startDate']).dt.strftime(consts.GENERAL_DATE_TIME_FORMATS)
        data['duration'] = pd.to_timedelta(data['duration']).fillna(timedelta(seconds=0))
        data['endDate'] = (pd.to_datetime(data['startDate']) + data['duration']).dt.strftime(
            consts.GENERAL_DATE_TIME_FORMATS)
        data['detailStatus'] = 0

        data[['startDate', 'endDate']] = data[['startDate', 'endDate']].astype(str)
        data['duration'] = (data['duration'] / pd.Timedelta(seconds=1)).astype(np.int64)
        data = data[
            ['id', 'startDate', 'endDate', 'duration', 'detailStatus', 'userId', 'taskId', ]  # 'userTaskDurationId',
        ].drop_duplicates().to_dict('records')

        print(data)
        try:
            response = requests.post(
                url=Sync.__INSERT_TIMELINES_URL,
                json=data,
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS
            )
            print(response.url)
            print(response.headers)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                df['sync'] = 1  # TODO: convert to update statement
                MainController.DB_CONNECTION.write(df, 'ProjectTimeLine', if_exists='replace')
                return response
            else:
                return False

        except requests.exceptions.HTTPError as e:
            e.args = e.args + ('APIs might be down',)
            print(e)
            raise e
        finally:
            if response is not None:
                response.close()

    @classmethod
    def update_screenshots_request(cls, user, ):
        print('Update ScreenShots Request')
        Sync.__HEADERS['Authorization'] = "Bearer " + user.token
        response = None
        df = db.execute(SQLs.SELECT_ALL_SCREENSHOTS_WHERE_USER_AND_SYNC_IS_ZERO.format(
            user=user.id
        ), conn_s=MainController.DB_CONNECTION).convert_dtypes(infer_objects=True, )
        df['date'] = pd.to_datetime(df['date']).dt.strftime(consts.GENERAL_DATE_TIME_FORMATS).astype(str)
        df['screenshot'] = df['screenshot'].apply(utils.base64_converter)  # TODO: Still Not Working
        df.drop(['sync'], axis=1, inplace=True)
        df = df[['id', 'user', 'date', 'screenshot', 'mouse_move', 'key_click', 'mouse_clicks', ]]
        df.columns = ['id', 'userId', 'screenshotDate', 'screenshotImage', 'mouseMove', 'keyClicks', 'mouseClicks', ]
        print(df.drop_duplicates().to_dict('records'))
        try:
            response = requests.post(
                url=Sync.__INSERT_TIMELINES_URL,
                json=df.drop_duplicates().to_dict('records'),
                timeout=Sync.__TIMEOUT,
                headers=Sync.__HEADERS,
            )
            print(response.url)
            print(response.headers)
            print(response.status_code)

            # response.raise_for_status()
            if str(response.status_code)[:-1] in Sync.__ACCEPTED_STATUS_CODE:
                df['sync'] = 1  # TODO: convert to update statement
                MainController.DB_CONNECTION.write(df, 'Screenshot', if_exists='replace')
                return response
            else:
                return False

        except requests.exceptions.HTTPError as e:
            e.args = e.args + ('APIs might be down',)
            print(e)
            raise e
        finally:
            if response is not None:
                response.close()

def main():
    MainController.initiate_database_connection()
    user = Sync.send_login_request('emran.allan@gmail.com', 'Emran@111')
    MainController.close_database_connection()


if __name__ == "__main__":
    main()

    pass
