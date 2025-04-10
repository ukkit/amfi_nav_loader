# AMFI NAV Loader

A Python-based system for automating the download, parsing, and storage of mutual fund NAV (Net Asset Value) data from AMFI (Association of Mutual Funds in India). The system is containerized using Docker for easy deployment and management.

## Features

- Automated download of NAV data from AMFI site
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

2. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```
   This will:
   - Build the Python application container
   - Start the MySQL database container
   - Start the Adminer interface container
   - Set up the required volumes for data persistence

3. Access the Adminer interface:
   - Open your browser and go to `http://localhost:8080`
   - Login with the following credentials:
     - System: MySQL
     - Server: db
     - Username: root
     - Password: (as specified in docker-compose.yml)
     - Database: nav_data

4. Initialize the database:
   ```bash
   docker-compose exec app python -c "from app.db.insert_nav import init_database; init_database()"
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
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Usage

### Daily Update
To download and process the latest NAV data:
```bash
docker-compose exec app python app/main.py
```
This will:
1. Get the latest business day
2. Download NAV data for that day
3. Parse and validate the data
4. Store it in the database

### Monthly Update
To download and process data for the past few months:
```bash
docker-compose exec app python app/main.py
```
The script will:
1. Check the earliest date in the database
2. Download data from that point backwards
3. Process and store the data
4. Provide a summary of the operation

### Historical Data
To download historical data for multiple years:
```bash
docker-compose exec app python -c "from app.downloader.download_nav import bulk_download_past_years; bulk_download_past_years(15)"
```
This will download data for the past 15 years.

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

## Download Options

1. **Daily Download**
   - Downloads data for the latest business day
   - Skips weekends and holidays automatically
   - Updates existing records if needed

2. **Monthly Download**
   - Downloads data for the past specified months
   - Starts from the earliest date in the database
   - Fills gaps in historical data
   - Default is 3 months if not specified

3. **Yearly Download**
   - Downloads data for multiple years
   - Useful for initial setup or filling large gaps
   - Processes data year by year
   - Maintains data integrity

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