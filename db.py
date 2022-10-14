import datetime

import pandas as pd
from sshtunnel import SSHTunnelForwarder
import configparser, os
import sqlalchemy as sa

import consts

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import db_models
import utils


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class StaticDBConnection(metaclass=Singleton):
    """Make sure to close the connection once you finish."""

    def __init__(self, ssh, ssh_user, ssh_host, ssh_pkey, delicate,
                 db_host, db_port, db_name, stream, db_user, db_pass,
                 use_uri,
                 ):
        # SSH Tunnel Variables
        if ssh:
            self.__ssh_connect__(ssh_host, ssh_user, ssh_pkey, db_host, db_port)
        elif not ssh:
            self.local_port = db_port
        self.engine = self.__create_database_engine__(delicate, stream, db_user, db_pass, db_host,
                                                      self.local_port, db_name, use_uri)
        self.metadata = sa.MetaData()

    def __create_database_engine__(self, delicate, stream, db_user, db_pass, db_host, db_port, db, use_uri):
        print(f"Creating connection to {db_host} on {db}...")
        if use_uri == True:
            conn_url = sa.engine.URL.create(
                drivername=delicate,
                username=db_user,
                password=db_pass,
                host=db_host,
                database=db,
                port=db_port
            )
        else:
            conn_url = f'{delicate}://{db}'
        print('Connection URI is:', conn_url)
        engine = sa.create_engine(conn_url)
        if stream:
            engine.connect().execution_options(stream_results=stream)
        print(f'Database [{engine.url.database}] session created...')
        return engine

    def __ssh_connect__(self, ssh_host, ssh_user, ssh_pkey, db_host, db_port):
        print("Establishing SSH connection ...")
        try:
            self.server = SSHTunnelForwarder(
                ssh_host=(ssh_host, 22),
                ssh_username=ssh_user,
                ssh_private_key=ssh_pkey,
                remote_bind_address=(db_host, db_port),
            )
            server = self.server
            server.start()  # start ssh server
        except Exception:
            raise ConnectionError(
                "Can't open a tunnel to the requested server. "
                "please check if the server is reachable and/or the provided configurations is correct."
            )
        self.local_port = server.local_bind_port
        print(f'Server connected via SSH || Local Port: {self.local_port}...')

    def schemas(self):
        inspector = sa.inspect(self.engine)
        print('Postgres database engine inspector created...')
        schemas = inspector.get_schema_names()
        schemas_df = pd.DataFrame(schemas, columns=['schema name'])
        print(f"Number of schemas: {len(schemas_df)}")
        return schemas_df

    def tables(self, schema):
        inspector = sa.inspect(self.engine)
        print('Postgres database engine inspector created...')
        tables = inspector.get_table_names(schema=schema)
        tables_df = pd.DataFrame(tables, columns=['table name'])
        print(f"Number of tables: {len(tables_df)}")
        return tables_df

    def select(self, query, chunksize=None):
        print(f'Executing \n{query}\n in progress...')
        try:
            query_df = pd.read_sql(query, self.engine, chunksize=chunksize).convert_dtypes(convert_string=False)
        except Exception as e:
            print(e)
            raise e
        print('<> Query Successful <>')
        return query_df

    def write(self, df, table, schema, if_exists='fail', chunksize=None, index=False):
        """Note: This method can't actually replace the values of records in the DB!!"""
        print(f'Writing data to [{table}] in the database schema {schema}...')
        try:
            df.to_sql(table, self.engine, schema=schema, if_exists=if_exists, chunksize=chunksize, index=index)
        except ValueError as e:
            print(e)
        print(f'<> Adding date to [{table}] Successful <>')
        return True

    def generic_query(self, sql):
        print(f'Executing \n{sql}\n in progress...')
        conn = None
        try:
            conn = self.engine.connect()
            res = conn.execute(sql)
        except Exception as e:
            print(e)
            raise e
        finally:
            conn.close()
        print(f'<> Run SQL done Successful <>')
        return res

    def close(self):
        self.engine.dispose()
        print('<> Connection Closed Successfully <>')

    def create_database(self):
        print(self.engine.url)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        return database_exists(self.engine.url)

        pass


def create_db_connection(config_path=None, host_config=None, ):
    config = configparser.ConfigParser()

    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "env")

    try:
        config.read(os.path.join(config_path, '{0}.ini'.format(host_config)))
        print(os.path.join(config_path, '{0}.ini'.format(host_config)))
    except IOError:
        raise IOError(
            "Can't read and/or find the config file. "
            "please make sure you are using the correct name and the config file exists."
        )

    print('Config available sections:', config.sections())
    dct = {}
    for section in config.sections():
        print(f'{section} availabe configs are {config.options(section)}')
        for option in config.options(section):
            opt = option.upper()
            try:
                if opt.startswith('USE'):
                    dct[opt] = config.getboolean(section, option)
                elif opt.endswith('NUM'):
                    dct[opt] = config.getint(section, option)
                else:
                    dct[opt] = config.get(section, option)
            except ValueError:
                try:
                    dct[opt] = config.get(section, option)
                except OSError:
                    raise IOError(
                        "Error while reading the config file. "
                        "one of the parameters and/or sections is missing or null."
                    )
            pass
    print('Loaded configs are:', dct)
    return StaticDBConnection(
        # SSH SECTION
        ssh=dct['USE_SSH'],
        ssh_user=dct['SSH_USER'],
        ssh_host=dct['SSH_HOST'],
        ssh_pkey=dct['SSH_PRIVATE_KEY'],
        # DB SECTION
        delicate=dct['DELICATE'],
        db_host=dct['DB_HOST'],
        db_port=dct['DB_PORT_NUM'],
        db_name=dct['DB_NAME'],
        db_user=dct['DB_SQL_USER'],
        db_pass=dct['DB_SQL_PASSWORD'],
        stream=dct['USE_STREAM'],
        # NV SECTION
        use_uri=dct['USE_URI'],
    )


def execute(sql: str, conn_s: StaticDBConnection = None, path: str = None, host: str = None, ):
    if path is None:
        path = consts.DB_CONFIG_DIR

    if host is None:
        host = consts.DB_HOST_FILE_NAME

    if conn_s is None:
        conn = create_db_connection(host_config=host, config_path=path)
    else:
        conn = conn_s

    print('-' * 99)
    if sql.strip().lower().startswith('select'):
        data = conn.select(sql)
    else:
        data = conn.generic_query(sql)
    print('-' * 99)

    if conn_s is None:
        conn.close()

    return data


def initiate_database(conn):
    df = utils.create_df_from_object(db_models.Project(
        project_id=0, name='', status=1, entry_id='', m_user=0, company_id=0,
    ))
    conn.write(df, table='Project', schema=None)

    df = utils.create_df_from_object(db_models.Task(
        project_id=0, sub_id=0, company_id=0, status=0, is_select=False, entry_id='', m_user=0, description='',
    ))
    conn.write(df, table='Task', schema=None)

    df = utils.create_df_from_object(db_models.ProjectTimeLine(
        project_id=0, sub_id=0, user=0,

    ))
    conn.write(df, table='ProjectTimeLine', schema=None)

    df = utils.create_df_from_object(db_models.User(
        user_id=0, sync_id=0, token='', company_id=0, email_address='', password='',
        status=0, logout=0, access_level=0, start_work_at=datetime.datetime.now(), name='',
    ))
    conn.write(df, table='User', schema=None)
    pass


try:
    CONN = create_db_connection(
        config_path=consts.DB_CONFIG_DIR,
        host_config=consts.DB_HOST_FILE_NAME
    )
except Exception as e:

    print(e)
    raise Exception("Couldn't establish a database connection.")
# conn = create_db_connection(host_config='local', config_path='env')
# df = conn.select('select * from "Aplications" p')
# print(df.info())
# conn.close()
