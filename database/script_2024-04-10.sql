alter table users add column name varchar(255) after id;
alter table users add last_name varchar(255) after name;
alter table users add column new_email varchar(255) after password;
alter table users add column new_password varchar(255) after new_email;
alter table users add validation_code int after new_password;