CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,    
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE stories (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    profile_id INTEGER,
    title TEXT,
    synopsis TEXT,
    last_successful_step INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);