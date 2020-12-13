create table payment(
payment_id int primary key auto_increment,
pay_date date ,
amount numeric(10),
farm_id int references farmer(farmer_id) on delete cascade on update cascade,
cart_id int references cart(cart_id) on delete cascade on update cascade
);