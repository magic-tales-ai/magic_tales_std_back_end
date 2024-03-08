CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    image VARCHAR(255),
    is_popular tinyint,
    price float,
    discount_per_year float,
    save_up_message varchar(255),
    stories_per_month int,
    customization_options text,
    voice_synthesis text,
    custommer_support text,
    description text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

insert into plans (name, image, is_popular, price, discount_per_year, save_up_message, stories_per_month, customization_options, voice_synthesis, custommer_support, description)
values
("Free Plan", "http://104.237.150.104:8000/static/FreePlan.png", 0, 0, 0, null, 3, null, null, null, '{ "messages": [ "Access to a limited number of stories per month (let''s say 3)", "Limited customization" ] }'),
("StoryCraft Plan", "http://104.237.150.104:8000/static/StoryCraftPlan.png", 0, 4.99, 0, null, 5, null, "Basic", null, '{ "messages": [ "Access to a limited number of stories per month (let''s say 5)", "Basic voice synthesis options", "Limited customization" ] }'),
("StoryCraft Plus", "http://104.237.150.104:8000/static/StoryCraftPlusPlan.png", 1, 9.99, 20, "Save 20% off", 15, "More options", "Premium", "Priority", '{ "messages": [ "More stories (up to 15 per month)", "More customization options", "Premium voice synthesis" ] }'),
("StoryCraft Pro", "http://104.237.150.104:8000/static/StoryCraftProPlan.png", 0, 19.99, 10, "Save 10% off", 999, "Full customization", "Premium voice synthesis", "Priority", '{ "messages": [ "Unlimited stories", "Full customization", "Access to premium voice synthesis", "Priority customer support" ] }');

alter table users add plan_id int not null default 1 after password;