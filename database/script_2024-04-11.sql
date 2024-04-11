ALTER TABLE users ADD active TINYINT DEFAULT 0 AFTER validation_code;
UPDATE users SET active = 1; /* ACTIVATE ALL USERS */