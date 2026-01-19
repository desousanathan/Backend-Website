DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email_address NOT NULL
);



DROP TABLE IF EXISTS stock;
CREATE TABLE stock
(
    prod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    desc TEXT,
    num_available INTEGER,
    price DECIMAL,
    image_filename TEXT
);


DROP TABLE IF EXISTS wishlist;
CREATE TABLE wishlist
(
    user_id TEXT NOT NULL,
    prod_id INTEGER NOT NULL
);

DROP TABLE IF EXISTS prev_purchases;
CREATE TABLE prev_purchases
(
    user_id TEXT NOT NULL,
    time DATE NOT NULL,
    name TEXT NOT NULL,
    num_of_items INTEGER NOT NULL

);

DROP TABLE IF EXISTS suggestions;
CREATE TABLE suggestions
(
    user_id TEXT NOT NULL,
    suggestion TEXT NOT NULL
);

INSERT INTO stock (name, desc, num_available, price, image_filename) 
VALUES 
    ('Running Shoes', 'High-performance running perfect for all occations', 50, 69.99, 'running_shoes.jpg'),
    ('Basketball Shoes', 'Durable basketball shoes desigined for the top most performance', 30, 89.99, 'basketball_shoes.jpg'),
    ('Soccer Shoes', 'High-performance soccer for great grip and power, perfect for all positions', 60, 89.99, 'football_shoes.jpg'),
    ('Tennis Shoes', 'Lightweight and cushioned tennis shoes designed for quick movement on the court and ', 40, 79.99, 'tennis_shoes.jpg'),
    ('Baseball Shoes', 'Baseball cleats designed for traction and comfort on the diamond.', 35, 99.99, 'baseball_shoes.jpg'),
    ('Cycling Shoes', 'Aerodynamic cycling shoes for high-speed performance and comfort on the road.', 25, 129.99, 'cycling_shoes.jpg'),
    ('Hiking Shoes', 'Rugged hiking shoes for exploring trails and outdoor adventures.', 20, 149.99, 'hiking_shoes.jpg'),
    ('CrossFit Shoes', 'CrossFit shoes bast for power and stability, when you are powering through a set', 45, 109.99, 'crossfit_shoes.jpg'),
    ('Golf Shoes', 'Comfortable and durable golf shoes with excellent grip perfect for long days on the course', 50, 119.99, 'golf_shoes.jpg'),
    ('Track Shoes', 'Professional track shoes made for speed and comfort', 30, 79.99, 'track_shoes.jpg');