create table timeline(
    id integer primary key,
    customer_user_id integer,
    customer_username varchar(255),
    customer_name varchar(30),
    session_date date,
    session_time time,
    available boolean,
    raw_text text,
    created datetime,
    updated datetime
);


create table about(
     id integer primary key,
     price1 integer,
     price2 integer,
     price3 integer,
     raw_address text,
     about_master text

 );


insert into about (price1, price2, price3, raw_address, about_master)
values
    ("10", "20", "30", "here will be the address📍", "here will be info about the master ✍️");