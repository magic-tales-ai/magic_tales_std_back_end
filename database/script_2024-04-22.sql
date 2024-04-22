-- Add a new column 'helper_id' that allows NULL values
ALTER TABLE users
ADD COLUMN helper_id VARCHAR(255) NULL;
-- Add a new column 'last_visited' with a default value
ALTER TABLE users
ADD COLUMN last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
-- Update the 'last_visited' column to a specific timestamp for all existing records
UPDATE users
SET last_visited = CURRENT_TIMESTAMP;
-- Add a new column 'try_mode' with a default value
ALTER TABLE users
ADD COLUMN try_mode TINYINT DEFAULT 0;