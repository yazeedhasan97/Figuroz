import functools
import requests
from datetime import datetime

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


class WrapperSync:
    ACCEPTED_STATUS_CODE = ['10', '20', '30']

    @staticmethod
    def request(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print('Send request in progress...')
            print(args)
            print(kwargs)
            response = None
            try:
                response = func(*args, **kwargs)
                print(response.status_code)
                print(response.headers)
                if str(response.status_code)[:-1] in WrapperSync.ACCEPTED_STATUS_CODE:
                    return response.json()
                else:
                    return False
            except requests.exceptions.HTTPError as e:
                print(e)
                e.args = e.args + ('APIs might be down',)
                raise e
            except Exception as e:
                print(e)
                e.args = e.args + ('APIs might be down',)
                raise e
            finally:
                if response is not None:
                    response.close()

        return wrapper


class MasterSync:
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
    }

    def __init__(self, environment='test', timeout=300, headers: dict = None, accept: list = None):
        envs = list(MasterSync.APIS_ACTIVE_ENVIRONMENTS.keys())
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
            WrapperSync.ACCEPTED_STATUS_CODE = accept.copy()

        self.timeout = timeout
        self.base_url = MasterSync.APIS_ACTIVE_ENVIRONMENTS[environment]
        self._merge()

    def _merge(self):
        for key, url in MasterSync.POST_URLS.items():
            MasterSync.POST_URLS[key] = self.base_url + url
        for key, url in MasterSync.GET_URLS.items():
            MasterSync.GET_URLS[key] = self.base_url + url

    @WrapperSync.request
    def post_forget_password_request(self, email: str, ):
        print('Post Forget Password Request')
        params = {
            'emailAddress': email,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('FORGET_PASSWORD', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_login_request(self, email: str, password: str):
        print('Post Login Request')
        params = {
            'emailAddress': email,
            'password': password
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('LOGIN', None),
            json=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_timelines_request(self, token: str, data: dict):
        print('Post ProjectTimelines Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('TIMELINES', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_screenshots_request(self, token: str, data: dict):
        print('Post ScreenShots Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }

        return requests.post(
            url=MasterSync.POST_URLS.get('SCREENSHOTS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_account_settings_request(self, token: str, data: dict):
        print('Post ACCOUNT_SETTINGS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('ACCOUNT_SETTINGS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_idles_request(self, token: str, data: dict):
        print('Post IDLE Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('IDLE', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_logs_request(self, token: str, data: dict):
        print('Post LOGS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('LOGS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_windows_request(self, token: str, data: dict):
        print('Post WINDOWS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('WINDOWS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def post_applications_request(self, token: str, data: dict):
        print('Post APPLICATIONS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.post(
            url=MasterSync.POST_URLS.get('APPLICATIONS', None),
            params=params,
            json=data,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_projects_request(self, token: str, ):
        print('Get Projects Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('PROJECT', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_tasks_request(self, token: str, ):
        print('Get Tasks Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('TASK', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_reset_user_sync_data_request(self, token: str, user_id: int):
        print('Get RESET_USER_SYNC_DATA Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'userId': user_id,
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('RESET_USER_SYNC_DATA', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_timelines_request(self, token: str, man_date: datetime):
        print('Get TIMELINES Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'date': str(man_date),
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('TIMELINES', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_durations_request(self, token: str, man_date: datetime):
        print('Get DURATIONS Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            'date': str(man_date),
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('DURATIONS', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_user_sync_flag_request(self, token: str, ):
        print('Get USER_SYNC_FLAG Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('USER_SYNC_FLAG', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )

    @WrapperSync.request
    def get_domain_table_request(self, token: str, ):
        print('Get DOMAIN_TABLE Request')
        self.headers['Authorization'] = "Bearer " + token
        params = {
            # 'emailAddress': email_address,
        }
        return requests.get(
            url=MasterSync.GET_URLS.get('DOMAIN_TABLE', None),
            params=params,
            timeout=self.timeout,
            headers=self.headers.copy()
        )


def main():
    sync = MasterSync(environment='test')
    user = sync.send_login_request('emran.allan@gmail.com', 'Emran@111')
    print(user)


if __name__ == "__main__":
    main()

    pass
