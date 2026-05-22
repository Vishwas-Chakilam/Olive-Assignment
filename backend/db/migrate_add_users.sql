-- Run in MySQL Workbench if automatic migration fails (select ollive DB first)
USE ollive;

CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(64) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  display_name VARCHAR(128) NOT NULL DEFAULT '',
  bio TEXT NULL,
  avatar_url VARCHAR(512) NULL,
  theme VARCHAR(32) NOT NULL DEFAULT 'dark',
  default_provider VARCHAR(64) NOT NULL DEFAULT 'mock',
  default_model VARCHAR(128) NOT NULL DEFAULT 'mock-gpt',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Only run if user_id column is missing (ignore error if already exists)
ALTER TABLE conversations ADD COLUMN user_id CHAR(36) NULL;
CREATE INDEX idx_conversations_user_id ON conversations (user_id);
