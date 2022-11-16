import functools
import time
import json
import requests
from datetime import datetime

from common import consts
from database.models import ProjectTimeLine, Idle, Screenshot, UserLog, UserAccountSetting, Window, Application

ACTIVE_ENVIRONMENT = 'test'
TIMEOUT = 300
HEADERS = {
    'User-Agent': 'Custom Agent 0.0',
    'Content-Type': "application/json",
    'charset': ':utf-8',
    'accept': 'text/plain',
    # 'Server': 'nginx/1.20.0',
    # "Authorization": "",
}
ACCEPTED_STATUS_CODE = ['10', '20', '30']


class DataWrapper:
    ACCEPTED_STATUS_CODE = ['10', '20', '30']

    @staticmethod
    def requester(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print('Send request in progress...')
            response = None
            try:
                response = func(*args, **kwargs)
                print(response.status_code)
                print(response.headers)

                if str(response.status_code)[:-1] in DataWrapper.ACCEPTED_STATUS_CODE:
                    try:
                        return response.json()
                    except:
                        print(response.content)
                        return response.content
                else:
                    return False
            except requests.exceptions.HTTPError as e:
                e.args = e.args + ('APIs might be down',)
                raise e
            except Exception as e:
                e.args = e.args + ('APIs might be down',)
                raise e
            finally:
                if response is not None:
                    response.close()

        return wrapper

    @staticmethod
    def loader(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print('Load data from the database in progress...')
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('Failed load data from the database. The database might be unreachable...')
                e.args = e.args + ('APIs might be down',)
                raise e
            finally:
                pass

        return wrapper


class DataRequester:
    APIS_ACTIVE_ENVIRONMENTS = {
        'test': "http://figurozapi-test.eu-central-1.elasticbeanstalk.com/api/",
        'prod': "https://figurozapi.com/api/",
    }
    POST_URLS = {
        'FORGET_PASSWORD': "UserAccounts/ForgetPassword",
        'LOGIN': "Authenticate/Login",
        'TIMELINES': "UserTaskDurationDetail/BulkInsert",
        'APPLICATIONS': "UserApplications/BulkInsert",
        'WINDOWS': "UserApplicationsDetail/BulkInsert",
        'LOGS': "UserApplcationsDetailLogs/BulkInsert",
        'IDLE': "UserTaskIdleDetail/BulkInsert",
        'ACCOUNT_SETTINGS': "UserAccountsSettings/BulkInsert",
        'SCREENSHOTS': "UserScreenshots/BulkInsert",
    }
    GET_URLS = {
        'USER_SYNC_FLAG': "UserAccounts/GetUserSyncFlag",
        'TASK': "Tasks",
        'PROJECT': "Projects/ByStatus/1",
        'DURATIONS': "UserTaskDurationDetail/GetUserTaskDurationByDate",  # + m_Date;
        'TIMELINES': "UserTaskDurationDetail/GetUserTaskDurationDetailByDate",  # +m_Date;
        'DOMAIN_TABLE': "DomainTable",
        'RESET_USER_SYNC_DATA': "UserAccounts/ResetUserSyncData",  # + App.user_ID;
        'UPLOAD_FILE': "File",  # + App.user_ID;
    }

    def __init__(self, environment='test', timeout=300, headers: dict = None, accept: list = None):
        envs = list(DataRequester.APIS_ACTIVE_ENVIRONMENTS.keys())
        assert environment in envs, \
            f"Must select a valid-active environment.\n" \
            f"Current active environments are {envs}, you passed '{environment}'"

        if headers is None:
            self.headers = {
                'User-Agent': 'Custom Agent 0.0',
                'Content-Type': "application/json",
                'charset': ':utf-8',
                'accept': 'text/plain',
                # 'Server': 'nginx/1.20.0',
                # "Authorization": "",
            }
        else:
            self.headers = headers.copy()

        if accept is not None:
            DataWrapper.ACCEPTED_STATUS_CODE = accept.copy()

        self.timeout = timeout
        self.base_url = DataRequester.APIS_ACTIVE_ENVIRONMENTS[environment]
        self._merge()

    def _merge(self):
        for key, url in DataRequester.POST_URLS.items():
            DataRequester.POST_URLS[key] = self.base_url + url
        for key, url in DataRequester.GET_URLS.items():
            DataRequester.GET_URLS[key] = self.base_url + url

    @DataWrapper.requester
    def post_forget_password_request(self, email: str, ):
        print('Post Forget Password Request')
        params = {
            'emailAddress': email,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('FORGET_PASSWORD', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_login_request(self, email: str, password: str):
        print('Post Login Request')
        params = {
            'emailAddress': email,
            'password': password
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('LOGIN', None),
            json=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_timelines_request(self, token: str, data: dict):
        print('Post ProjectTimelines Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('TIMELINES', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_screenshots_request(self, token: str, data: dict):
        # TODO: must include the upload file function
        print('Post ScreenShots Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }

        return requests.post(
            url=DataRequester.POST_URLS.get('SCREENSHOTS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_account_settings_request(self, token: str, data: dict):
        print('Post ACCOUNT_SETTINGS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('ACCOUNT_SETTINGS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_idles_request(self, token: str, data: dict):
        print('Post IDLE Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('IDLE', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_logs_request(self, token: str, data: dict):
        print('Post LOGS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('LOGS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_windows_request(self, token: str, data: dict):
        print('Post WINDOWS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('WINDOWS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def post_applications_request(self, token: str, data: dict):
        print('Post APPLICATIONS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=DataRequester.POST_URLS.get('APPLICATIONS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_projects_request(self, token: str, ):
        print('Get Projects Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('PROJECT', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_tasks_request(self, token: str, ):
        print('Get Tasks Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('TASK', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_reset_user_sync_data_request(self, token: str, user_id: int):
        print('Get RESET_USER_SYNC_DATA Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'userId': user_id,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('RESET_USER_SYNC_DATA', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_upload_file_request(self, user_id: int):
        print('Get UPLOAD_FILE Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'userId': user_id,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('UPLOAD_FILE', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )



    @DataWrapper.requester
    def get_timelines_request(self, token: str, man_date: datetime):
        print('Get TIMELINES Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'date': str(man_date),
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('TIMELINES', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_durations_request(self, token: str, man_date: datetime):
        print('Get DURATIONS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'date': str(man_date),
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('DURATIONS', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_user_sync_flag_request(self, token: str, ):
        print('Get USER_SYNC_FLAG Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('USER_SYNC_FLAG', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )

    @DataWrapper.requester
    def get_domain_table_request(self, token: str, ):
        print('Get DOMAIN_TABLE Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=DataRequester.GET_URLS.get('DOMAIN_TABLE', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy(),
        )


class DataLoader:
    def __init__(self, user_id, session):
        self.user_id = user_id
        self.session = session
        pass

    def _commit(self, data):
        for i, item in enumerate(data):
            data[i].sync = 1
        self.session.commit()

    @DataWrapper.loader
    def load_project_timelines(self, commit=False, ):
        timelines = self.session.query(ProjectTimeLine).filter(
            ProjectTimeLine.sync == 0 and
            ProjectTimeLine.user_id == self.user_id
        ).all()
        res = [{
            'id': timeline.id,
            'startDate': timeline.start.strftime(consts.APIS_DATE_TIME_FORMATS),
            'endDate': timeline.end.strftime(consts.APIS_DATE_TIME_FORMATS),
            'duration': int(timeline.duration.total_seconds()),
            'detailStatus': timeline.status,
            'userId': timeline.user_id,
            'taskId': timeline.task_id,
        } for timeline in timelines]
        if commit:
            self._commit(timelines)
        return res

    @DataWrapper.loader
    def load_screenshots(self, commit=False):
        screenshots = self.session.query(Screenshot).filter(
            Screenshot.sync == 0 and
            Screenshot.user_id == self.user_id
        ).all()
        res = [{
            'id': screenshot.id,
            'userId': screenshot.user_id,
            'screenshotDate': screenshot.date.strftime(consts.APIS_DATE_TIME_FORMATS),
            'screenshotImage': screenshot.screenshot,
            'mouseMove': screenshot.mouse_move,
            'keyClicks': screenshot.key_click,
            'mouseClicks': screenshot.mouse_clicks,
        } for screenshot in screenshots]
        if commit:
            self._commit(screenshots)
        return res

    @DataWrapper.loader
    def load_idles(self, commit=False):
        idles = self.session.query(Idle).filter(
            Idle.sync == 0 and
            Idle.user_id == self.user_id
        ).all()
        res = [{
            'id': idle.id,
            'userTaskDurationDetailId': idle.task_id,
            'startDate': idle.start.strftime(consts.APIS_DATE_TIME_FORMATS),
            'endDate': idle.end.strftime(consts.APIS_DATE_TIME_FORMATS),
            'duration': idle.duration,
            'userApplicationDetailId': idle.application_id,
        } for idle in idles]
        if commit:
            self._commit(idles)
        return res

    @DataWrapper.loader
    def load_logs(self, commit=False):
        logs = self.session.query(UserLog).filter(
            UserLog.sync == 0 and
            UserLog.user_id == self.user_id
        ).all()
        res = [{
            'id': log.id,
            'startDate': log.start.strftime(consts.APIS_DATE_TIME_FORMATS),
            'endDate': log.end.strftime(consts.APIS_DATE_TIME_FORMATS),
            'userApplicationsDetailID': log.window_id,
            'userTaskDurationDetailId': log.project_timeline_id,
            'duration': log.duration,
        } for log in logs]
        if commit:
            self._commit(logs)
        return res

    @DataWrapper.loader
    def load_account_settings(self, commit=False):
        account_settings = self.session.query(UserAccountSetting).filter(
            UserAccountSetting.sync == 0 and
            UserAccountSetting.user_id == self.user_id
        ).all()
        res = [{
            'id': setting.id,
            'userId': setting.user_id,
            'type': setting.type,
            'settingValue': setting.value,
            'updatedDate': setting.date.strftime(consts.APIS_DATE_TIME_FORMATS),
        } for setting in account_settings]
        if commit:
            self._commit(account_settings)
        return res

    @DataWrapper.loader
    def load_windows(self, commit=False):
        windows = self.session.query(Window).filter(
            Window.sync == 0 and
            Window.user_id == self.user_id
        ).all()
        res = [{
            'id': window.id,
            'applicationId': window.application_id,
            'windowTitle': window.title,
            'windowURL': window.window_url.replace('\\', '/'),
            'startDate': window.start.strftime(consts.APIS_DATE_TIME_FORMATS),
            'url': window.url,
            'urlDomain': window.domain_url,
        } for window in windows]
        if commit:
            self._commit(windows)
        return res

    @DataWrapper.loader
    def load_applications(self, commit=False):
        applications = self.session.query(Application).filter(
            Application.sync == 0 and
            Application.user_id == self.user_id
        ).all()
        res = [{
            'id': application.id,
            'applicationName': application.name,
            'applicationPath': application.path.replace('\\', '/'),
            'applicationVersion': application.version,
            'description': application.description,
            'userAccountsId': application.user_id,

        } for application in applications]
        if commit:
            self._commit(applications)
        return res


class LoadUploadController:
    def __init__(self, session, requester, user_id, token, commit=False):
        self.loader = DataLoader(
            user_id=user_id,
            session=session,
        )
        self.requester = requester
        self.user_id = user_id
        self.token = token
        self.commit = commit
        pass

    def load_and_upload(self):
        time.sleep(1)
        self.load_and_upload_project_timelines()
        self.load_and_upload_idles()
        self.load_and_upload_windows()
        self.load_and_upload_applications()
        self.load_and_upload_screenshots()
        self.load_and_upload_logs()
        self.load_and_upload_account_settings()
        time.sleep(1)
        pass

    def load_and_upload_project_timelines(self):
        data = self.loader.load_project_timelines(
            commit=self.commit
        )
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_timelines_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_screenshots(self):
        data = self.loader.load_screenshots(
            commit=self.commit
        )
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_screenshots_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_idles(self):
        data = self.loader.load_idles(
            commit=self.commit
        )
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_idles_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_logs(self):
        data = self.loader.load_logs()
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_logs_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_account_settings(self):
        data = self.loader.load_account_settings()
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_account_settings_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_windows(self):
        data = self.loader.load_windows()
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_windows_request(
                token=token,
                data=data,
            )
            print(res)
        pass

    def load_and_upload_applications(self):
        data = self.loader.load_applications()
        print(data)
        if data:
            time.sleep(1)
            res = self.requester.post_applications_request(
                token=token,
                data=data,
            )
            print(res)
        pass


if __name__ == "__main__":
    from database.models import create_database_session

    mode = 'test'
    api_sync = DataRequester(mode)

    db_sync = create_database_session(
        consts.TEST_DB_PATH,
        echo=False,
    )
    data = api_sync.post_login_request(
        email='emran.allan@gmail.com',
        password='Emran@111'
    )
    token, user_id = data['token'], data['user']['id']
    print(user_id, token)

    print(api_sync.get_upload_file_request(
        user_id
    ))

    # load_upload_controller = LoadUploadController(
    #     session=db_sync,
    #     requester=api_sync,
    #     user_id=user_id,
    #     token=token,
    # )
    # load_upload_controller.load_and_upload()
    pass
