-- Run once in MySQL Workbench or: mysql -u root -p < backend/db/init_mysql.sql
CREATE DATABASE IF NOT EXISTS ollive
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ollive;

-- Tables are created automatically by SQLAlchemy on backend startup.
