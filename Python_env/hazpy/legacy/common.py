import os
from pathlib import Path
import json
import pandas as pd
import pyodbc as py
from sqlalchemy import create_engine


class HazusDB():
    """Creates a connection to the Hazus SQL Server database with methods to access
    databases, tables, and study regions
    """

    def __init__(self):
        self.conn = self.createConnection()
        self.cursor = self.conn.cursor()
        self.databases = self.getDatabases()

    def getConnectionString(self, stringName):
        """ Looks up a connection string in a json file based on an input argument

            Keyword Arguments:
                stringName: str -- the name of the connection string in the json file
                
            Returns:
                conn: pyodbc connection string that needs driver and computername updated
        """
        with open(os.path.join(Path(__file__).parent, "connectionStrings.json")) as f:
            connectionStrings = json.load(f)
            connectionString = connectionStrings[stringName]
        return connectionString

    def createConnection(self):
        """ Creates a connection object to the local Hazus SQL Server database

            Returns:
                conn: pyodbc connection
        """
        # list all Windows SQL Server drivers
        drivers = [
            '{ODBC Driver 17 for SQL Server}',
            '{ODBC Driver 13.1 for SQL Server}',
            '{ODBC Driver 13 for SQL Server}',
            '{ODBC Driver 11 for SQL Server} ',
            '{SQL Server Native Client 11.0}',
            '{SQL Server Native Client 10.0}',
            '{SQL Native Client}',
            '{SQL Server}'
        ]
        computer_name = os.environ['COMPUTERNAME']
        # create connection with the latest driver
        for driver in drivers:
            try:
                conn = py.connect(self.getConnectionString('pyodbc').format(d=driver,cn=computer_name))
                break
            except:
                continue
        self.conn = conn
        return conn

    def createWriteConnection(self, databaseName):
        """ Creates a connection object to a table in the local Hazus 
        SQL Server database

            Keyword Arguments:
                databaseName: str -- the name of the Hazus SQL Server database

            Returns:
                writeConn: sqlalchemy connection
        """
        engine = create_engine(self.getConnectionString('sqlalchemy').format(db=databaseName))
        writeConn = engine.connect()
        self.writeConn = writeConn
        return writeConn

    def appendData(self, dataframe, tableName, truncate=False):
        """Appends the dataframe to Hazus SQL Server database table

            Keyword Arguments:
                dataFrame: df -- pandas dataframe
                tableName: str -- the name of the table to append to
                truncate: boolean -- if true, drop the table before inserting
        new values

            Note:  For best results ensure that your dataframe schema and 
        datatypes match the destination prior to appending.
        """
        if truncate:
            truncateSetting = 'replace'
        else:
            truncateSetting = 'append'
        dataframe.to_sql(name=tableName, con=self.writeConn,
                         if_exists=truncateSetting, index=False)

    def getDatabases(self):
        """Creates a dataframe of all databases in your Hazus installation

            Returns:
                df: pandas dataframe
        """
        query = 'SELECT name FROM sys.databases'
        df = pd.read_sql(query, self.conn)
        return df

    def getTables(self, databaseName):
        """Creates a dataframe of all tables in a database

            Keyword Arguments:
                databaseName: str -- the name of the Hazus SQL Server database

            Returns:
                df: pandas dataframe
        """
        query = 'SELECT * FROM [%s].INFORMATION_SCHEMA.TABLES;' % databaseName
        df = pd.read_sql(query, self.conn)
        self.tables = df
        return df

    def getStudyRegions(self):
        """Creates a dataframe of all study regions in the local Hazus SQL Server database

            Returns:
                studyRegions: pandas dataframe
        """
        exclusionRows = ['master', 'tempdb', 'model',
                         'msdb', 'syHazus', 'CDMS', 'flTmpDB']
        self.cursor.execute('SELECT [StateID] FROM [syHazus].[dbo].[syState]')
        for state in self.cursor:
            exclusionRows.append(state[0])
        query = 'SELECT * FROM sys.databases'
        df = pd.read_sql(query, self.conn)
        studyRegions = df[~df['name'].isin(exclusionRows)]['name']
        studyRegions = studyRegions.reset_index()
        studyRegions = studyRegions.drop('index', axis=1)
        self.studyRegions = studyRegions
        return studyRegions

    def query(self, sql):
        """Performs a SQL query on the Hazus SQL Server database

            Keyword Arguments:
                sql: str -- a T-SQL query

            Returns:
                df: pandas dataframe
        """
        df = pd.read_sql(sql, self.conn)
        return df

    def getHazardBoundary(self, databaseName):
        """Fetches the hazard boundary from a Hazus SQL Server database

            Keyword Arguments:
                databaseName: str -- the name of the database

            Returns:
                df: pandas dataframe -- geometry in WKT
        """
        query = 'SELECT Shape.STAsText() as geom from [%s].[dbo].[hzboundary]' % databaseName
        df = pd.read_sql(query, self.conn)
        return df
