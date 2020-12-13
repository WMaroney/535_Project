CREATE DATABASE HIPS;
USE HIPS;

SET foreign_key_checks = 0;
drop table if exists users;

CREATE TABLE user_table(
	user_id integer auto_increment,
	User_Name varchar(50) not null,
	Password varchar(30) not null,
	User_Type varchar(10) not null,
	primary key (user_id)
);

drop table if exists device_table;
CREATE TABLE device_table(
	device_ID integer auto_increment,
	user_id integer,
	Device_Name varchar(50) not null,
	Device_IP varchar(30) not null,
	Device_Type varchar(50) not null,
	PRIMARY KEY (Device_ID),
	FOREIGN KEY fk_user(user_id) REFERENCES user_table(user_id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT
);

SET foreign_key_checks = 1;	

