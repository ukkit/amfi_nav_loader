import os

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysqldb'),
    'user': os.getenv('MYSQL_USER', 'bob'),
    'password': os.getenv('MYSQL_PASSWORD', 'marley'),
    'database': os.getenv('MYSQL_DATABASE', 'dont_worry'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}
# NAVALL_BASE_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt="
NAVALL_BASE_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}&todt={}"
