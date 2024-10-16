import os

class BaseConfig(object):
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://E-Report:123456@cnhuasolar1608/E-Report?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCOPE_BASE = ['https://analysis.windows.net/powerbi/api/.default']
    POWER_BI_API_URL = 'https://api.powerbi.com/'
    TOKEN_URL_TEMPLATE = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    AUTHORITY_URL = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize'
    SESSION_PERMANENT = True
    SESSION_TYPE = 'filesystem'
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_POOL_TIMEOUT = 20