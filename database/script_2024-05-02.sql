ALTER TABLE stories
rename COLUMN session_id  to ws_session_uid;

ALTER TABLE conversations
rename COLUMN session_id  to ws_session_uid;