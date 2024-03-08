CREATE TABLE conversations (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    session_id VARCHAR (255),
    origin SET('user', 'ai'),
    type SET('chat', 'command'),
    command VARCHAR (255),
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);