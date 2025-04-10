# AMFI NAV Loader

A Python-based system for automating the download, parsing, and storage of mutual fund NAV (Net Asset Value) data from AMFI (Association of Mutual Funds in India). The system is containerized using Docker for easy deployment and management.

## Features

- Automated download of NAV data from AMFI
- Support for daily, monthly, and yearly data downloads
- Automatic handling of weekends and holidays
- Data validation and error handling
- Efficient database storage with partitioning
- Comprehensive logging and monitoring
- Docker-based deployment for easy setup
- Adminer interface for database management

## Requirements

### System Requirements
- Docker
- Docker Compose
- Internet connection for data downloads

### Docker Images
- Python 3.x
- MySQL 8.0
- Adminer (Database management interface)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/ukkit/amfi_nav_loader
   cd amfi_nav_loader
   ```

2. Create .env from .env.sample and enter database details:
   ```bash
   cp .env.sample .env
   MYSQL_ROOT_PASSWORD=example_root_password
   MYSQL_DATABASE=name_of_mysql_database   
   MYSQL_USER=username_for_mysql_database
   MYSQL_PASSWORD=password_for_mysql_database
   IN_MYSQL_PORT=3306  # Specify the incoming MySQL port
   OUT_MYSQL_PORT=3306  # Specify the outgoing MySQL port
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```
   This will:
   - Build the Python application container
   - Start the MySQL database container
   - Start the Adminer interface container
   - Set up the required volumes for data persistence

4. Access the Adminer interface:
   - Open your browser and go to `http://localhost:8080`
   - Login with the following credentials:
     - System: MySQL
     - Server: mysqldb
     - Username: as_defined_in_.env_file
     - Password: as_defined_in_.env_file
     - Database: as_defined_in_.env_file

5. Initialize the database:
   ```bash
   docker-compose exec app python -c "from db.insert_nav import init_database; init_database()"
   ```

## Usage

### Command Line Arguments

The script supports three modes of operation:

1. **Daily Update** (default, no arguments):
   ```bash
   docker-compose exec app python main.py
   ```
   This will:
   - Get the latest business day
   - Download NAV data for that day
   - Parse and validate the data
   - Store it in the database

2. **Monthly Update** (with --months argument):
   ```bash
   docker-compose exec app python main.py --months 3
   ```
   This will:
   - Check the earliest date in the database
   - Download data from that point backwards
   - Process and store the data
   - Provide a summary of the operation

### Examples

1. Run daily update:
   ```bash
   docker-compose exec app python main.py
   ```

2. Run monthly update for past 6 months:
   ```bash
   docker-compose exec app python main.py --months 6
   ```

## Directory Structure

```
amfi_nav_loader/
├── app/
│   ├── downloader/
│   │   └── download_nav.py
│   ├── parser/
│   │   └── parse_nav.py
│   ├── db/
│   │   └── insert_nav.py
│   └── main.py
├── data/
│   └── (downloaded files)
├── logs/
│   ├── monthly_job.log
│   └── error_log.txt
├── .env.sample
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Docker Commands

### Common Docker Operations
1. Start the containers:
   ```bash
   docker-compose up -d
   ```

2. Stop the containers:
   ```bash
   docker-compose down
   ```

3. View logs:
   ```bash
   docker-compose logs -f
   ```

4. Access the application container:
   ```bash
   docker-compose exec app bash
   ```

5. Access the database:
   ```bash
   docker-compose exec db mysql -u root -p
   ```

### Volume Management
- Data files are stored in the `./data` volume
- Logs are stored in the `./logs` volume
- Database data is persisted in the `mysql_data` volume

## Troubleshooting

### Common Issues

1. **Container Startup Issues**
   - Check Docker daemon status
   - Verify port availability
   - Check disk space for volumes
   - Review Docker logs

2. **Database Connection Errors**
   - Verify MySQL container is running
   - Check database credentials
   - Ensure proper permissions are set
   - Verify network connectivity between containers

3. **Download Failures**
   - Check internet connection
   - Verify AMFI website accessibility
   - Ensure proper file permissions in volumes
   - Check for rate limiting

4. **Data Validation Errors**
   - Check log files for specific errors
   - Verify data format compliance
   - Ensure proper date formats
   - Check for missing required fields

### Log Files

- **monthly_job.log**: Contains detailed information about monthly job execution
- **error_log.txt**: Records any errors encountered during execution
- **Docker logs**: Available via `docker-compose logs`

## Best Practices

1. **Regular Maintenance**
   - Run monthly updates regularly
   - Monitor log files
   - Clean up old data files
   - Backup database regularly
   - Update Docker images periodically

2. **Error Handling**
   - Check log files after each run
   - Address errors promptly
   - Maintain error history
   - Implement retry mechanisms

3. **Performance Optimization**
   - Use appropriate batch sizes
   - Monitor database performance
   - Optimize queries
   - Regular maintenance
   - Monitor container resource usage

4. **Security**
   - Keep Docker images updated
   - Use strong database passwords
   - Limit container resource usage
   - Regular security audits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Support

For support, please:
1. Check the documentation
2. Review the log files
3. Search for similar issues
4. Create a new issue if needed 