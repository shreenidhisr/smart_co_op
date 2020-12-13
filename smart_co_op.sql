create database co_op;

use co_op;

create table farmer(
farmer_id int primary key auto_increment,
name varchar(30) not null,
email varchar(40) not null,
password varchar(20) not null,
mobile int(10),
aadhar varchar(20) not null
);

alter table farmer 
modify column mobile numeric(10);

create table farmer_address(
farmer_id int primary key auto_increment,
state varchar(20) not null,
city varchar(30) not null,
taluka varchar(30) not null,
house_no varchar(20) not null,
pincode varchar(30) not null,
foreign key(farmer_id) references farmer(farmer_id) on update cascade on delete cascade
);

create table cart(
cart_id int primary key auto_increment
);


create table farmer_cart(
farmer_id int,
cart_id int,
primary key(farmer_id,cart_id),
foreign key(farmer_id) references farmer(farmer_id) on update cascade on delete cascade,
foreign key(cart_id) references cart(cart_id) on update cascade on delete cascade
);

create table society(
society_id int auto_increment,
chief_name varchar(30) not null,
email varchar(30) not null,
password varchar(30) not null,
primary key(society_id)
);

create table society_address(
society_id int primary key,
state varchar(20),
city varchar(30),
taluka varchar(30),
pincode varchar(30),
foreign key(society_id) references society(society_id) on update cascade on delete cascade
);

create table govt_authority(
auth_id int auto_increment,
name varchar(20) not null,
email varchar(30) not null,
mobile int(10),
password varchar(30) not null,
primary key(auth_id)
);


create table products(
product_id int primary key auto_increment,
quantity_avail int not null,
cost int not null,
product_type varchar(20) not null,
society_id int,
auth_id int,
foreign key(society_id) references society(society_id) on update cascade on delete cascade,
foreign key(auth_id) references govt_authority(auth_id) on update cascade on delete cascade
);

alter table products 
add column img_path varchar(50);

alter table products
add column prod_name varchar(30);



create table cart_items(
cart_items_id int primary key auto_increment,
purchased boolean not null,
quantity int not null,
date_added date not null,
cart_id int,
prod_id int,
foreign key(cart_id) references cart(cart_id) on update cascade on delete cascade,
foreign key(prod_id) references products(product_id) on update cascade on delete cascade
);



create table society_govtauthority(
society_id int,
auth_id int,
primary key(society_id,auth_id),
foreign key(society_id) references society(society_id) on update cascade on delete cascade,
foreign key(auth_id) references govt_authority(auth_id) on update cascade on delete cascade
);

CREATE TABLE IF NOT EXISTS `locations` (
		`id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
        `pincode` VARCHAR(30) NOT NULL,
        `city_id` INT(11) NOT NULL,
        `city_name` VARCHAR(30) NOT NULL,
        `state_id` INT(11) NOT NULL,
        `state_name` VARCHAR(30) NOT NULL,
        `country_id` INT(11) NOT NULL,
        `country_name` VARCHAR(30) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE utf8_general_ci;
        
