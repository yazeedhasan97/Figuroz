from datetime import timedelta


class DurationKeeper:
    def __init__(self, user_id: int, project_id: int, task_id: int, duration: timedelta = timedelta(seconds=0)):
        self.__user_id = user_id
        self.__project_id = project_id
        self.__task_id = task_id
        self.__duration = duration

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_user_id(self):
        return self.__user_id

    def __set_user_id(self, user_id):
        self.__user_id = user_id

    user_id = property(
        fget=__get_user_id,
        fset=__set_user_id,
        doc='None.',
    )

    def __get_task_id(self):
        return self.__task_id

    def __set_task_id(self, task_id):
        self.__task_id = task_id

    task_id = property(
        fget=__get_task_id,
        fset=__set_task_id,
        doc='None.',
    )

    def __get_duration(self):
        return self.__duration

    def __set_duration(self, duration):
        self.__duration = duration

    duration = property(
        fget=__get_duration,
        fset=__set_duration,
        doc='None.',
    )
