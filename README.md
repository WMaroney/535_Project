# CarVerse--
A automobile based database developed for CSC 540 Database Systems

## Requirements

- Python3
- Flask
- Flask Forms
- Flask WTF
- pymySQL
- SQLite

## Description

This database and website is being developed for a graduate level project for database systems CSC 540. The database has automobiles preloaded in and would allow a user to search and add cars to the database.

## Where are we in development?

- [x] Hosted
- [x] Able to login
- [x] Able to sign up
- [x] Display cars on Index
- [x] Add Car
- [x] Search Car
- [ ] Remove Car pushed to version 2 feature
- [ ] Display Car data on Search not ID's
- [ ] More robust search parameters allowing user to search by brand or other criteria

## File & Folder Organization
- File & Folder Organization
	- Folders
		- Templates folder holds html templates
	- Files
		- main.py (main program)
		- CarVerse_tables.sql (SQL script to build database and tables)
		- CarVerse_data.sql (SQL script to preload data into database)
		- README.md
		- rqs.txt (requirements)

## To Run the Application

- Clone or download repo to desktop
- Open terminal and navigate to CarVerse Folder
- Install requirements.txt from the terminal "pip3 install -r requirements.txt"
- Run "python3 main.py" in the terminal
- Open Firefox/Chrome or any other internet Browser and Input "http://localhost:8080" to view the web application
