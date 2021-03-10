# pip install azure plotnine passgen pymysql adal wget tempfile
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_active_directory import AADTokenCredentials
from azure.mgmt.resource.resources.models import DeploymentMode
import adal, json, requests, pymysql, passgen, warnings, wget, os, tempfile
from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap
from plotnine.data import mtcars
from io import StringIO
import pandas.io.sql as sqlio

def authenticate_device_code():
    
    # Replace values with your client and tenant id
    tenant = '7cf48d45-3ddb-4389-a9c1-c115526eb52e'
    client_id = '00000000-0000-0000-0000-000000000000'
    authority_host_uri = 'https://login.microsoftonline.com'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    code = context.acquire_user_code(resource_uri, client_id)
    print(code['message'])
    mgmt_token = context.acquire_token_with_device_code(resource_uri, code, client_id)
    credentials = AADTokenCredentials(mgmt_token, client_id)
    return credentials

if __name__ == '__main__':
    
    # Initialize parameters
    # Replace with your subscription id
    subscription_id = "5c2914f4-5ca5-4123-864f-3ea296a402c0"
    resource_group = "cloud-shell-storage-eastus"
    location = "East US"
    mysql_username = "capstone"
    mysql_password = "PennState2021!"
    mysql_servername = "capstone-2021"

    # Other ways to obtain credentials : https://github.com/Azure-Samples/data-lake-analytics-python-auth-options/blob/master/sample.py
    credentials = authenticate_device_code()
    client = ResourceManagementClient(credentials, subscription_id)

    # # Create Resource group
    # print("\nCreating Resource Group","\n")
    # client.resource_groups.create_or_update(resource_group, {"location": location})

    # # Create MySQL Server using ARM template
    # print("Creating Azure Database for MySQL Server","\n")
    # template = json.loads(requests.get("https://raw.githubusercontent.com/Azure/azure-mysql/master/arm-templates/ExampleWithFirewallRule/tem...)
    # parameters = {
    #     'administratorLogin': mysql_username,
    #     'administratorLoginPassword': mysql_password,
    #     'location': location,
    #     'serverName': mysql_servername,
    #     'skuCapacity': 2,
    #     'skuFamily': 'Gen5',
    #     'skuName': 'GP_Gen5_2',
    #     'skuSizeMB': 51200,
    #     'skuTier': 'GeneralPurpose',
    #     'version': '5.7',
    #     'backupRetentionDays': 7,
    #     'geoRedundantBackup': 'Disabled'
    # }
    # parameters = {k: {'value': v} for k, v in parameters.items()}
    # deployment_properties = {
    #     'mode': DeploymentMode.incremental,
    #     'template': template,
    #     'parameters': parameters
    # }
    # deployment_async_operation = client.deployments.create_or_update(
    #     resource_group,
    #     'azure-mysql-sample',
    #     deployment_properties
    # )
    # deployment_async_operation.wait()
    
    # Download SSL cert
    print("Downloading SSL cert","\n")
    certpath = os.path.join(tempfile.gettempdir(), "BaltimoreCyberTrustRoot.crt")
    os.remove(certpath)
    wget.download("https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem", certpath, bar=None)
    
    # Connect to mysql database using pymysql
    print("Connecting to Azure Database for MySQL Server","\n")
    try:
        connection = pymysql.connect(user = mysql_username + '@' + mysql_servername,
                                    password = mysql_password,
                                    host = mysql_servername + ".mysql.database.azure.com",
                                    port = 3306,
                                    db = "mysql",
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True,
                                    ssl={'ca': certpath})
        cursor = connection.cursor()
        
        # Print MySQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        # create database mtcars and connect to it
        print("Creating database mtcars","\n")
        cursor.execute("CREATE DATABASE mtcars")
        connection = pymysql.connect(user = mysql_username + '@' + mysql_servername,
                                    password = mysql_password,
                                    host = mysql_servername + ".mysql.database.azure.com",
                                    port = 3306,
                                    db = "mtcars",
                                    local_infile=1,
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True,
                                    ssl={'ca': certpath})
        cursor = connection.cursor()

        # Create mtcars table
        print("Creating table mtcars","\n")
        create_table_query = '''CREATE TABLE mtcars (
            name VARCHAR(50) NOT NULL, 
            mpg FLOAT NOT NULL, 
            cyl INTEGER NOT NULL, 
            disp FLOAT NOT NULL, 
            hp INTEGER NOT NULL, 
            drat FLOAT NOT NULL, 
            wt FLOAT NOT NULL, 
            qsec FLOAT NOT NULL, 
            vs INTEGER NOT NULL, 
            am INTEGER NOT NULL, 
            gear INTEGER NOT NULL, 
            carb INTEGER NOT NULL
            );'''
        cursor.execute(create_table_query)

        # Load mtcars data from csv file
        print("Loading data into table mtcars","\n")
        mtcars.to_csv("mtcars.csv", index=False, header=False)
        cursor.execute("LOAD DATA LOCAL INFILE 'mtcars.csv' INTO TABLE mtcars FIELDS TERMINATED BY ',';")
        os.remove("mtcars.csv")

        # read mtcars data from MySQL into a pandas dataframe
        print("Reading data from mtcars table into a pandas dataframe","\n")
        mtcars_data = sqlio.read_sql_query("select * from mtcars", connection)

        # visualize the data using ggplot
        print("Visualizing data from mtcars table","\n")
        plot = (ggplot(mtcars_data, aes('wt', 'mpg', color='factor(gear)'))
        + geom_point()
        + stat_smooth(method='lm')
        + facet_wrap('~gear'))

        # We run this to suppress various deprecation warnings from plotnine - keeps our output cleaner
        warnings.filterwarnings('ignore')

        # Save the plot as pdf file
        print("Saving plot as PDF file","\n")
        plot.save("mtcars.pdf")

    except (Exception, pymysql.Error) as error :
        print ("Error while connecting to MySQL", error)
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("MySQL connection is closed","\n")

    # Delete Resource group and everything in it
    print("Deleting Resource Group", "\n")
    delete_async_operation = client.resource_groups.delete(resource_group)
    delete_async_operation.wait()
    print("Deleted: {}\n".format(resource_group))