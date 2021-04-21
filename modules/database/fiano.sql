/*
    FIANO DB
    Database file for Fiano system
    filename - fiano.sql
*/
-- ******************************* USERS TABLE ********************************************************
CREATE TABLE IF NOT EXISTS users(
    id_user INTEGER PRIMARY KEY autoincrement,
    username TEXT NOT NULL unique,
    password TEXT NOT NULL,
    name TEXT,
    lastname TEXT,
    email TEXT,
    default_password TEXT default '$2b$12$idYVviWZpNQuRrQSXq5VGOJSA.5FPSUcqDLZy/QZbv/WTPQyhlHG2'
);

-- ******************************* PROJECTS TABLE *****************************************************
CREATE TABLE IF NOT EXISTS projects(
    id_project INTEGER PRIMARY KEY autoincrement,
    creation_date TEXT NOT NULL,
    name_project TEXT NOT NULL,
    id_user INTEGER NOT NULL
);

-- ******************************* ANALYSIS TABLE *****************************************************
CREATE TABLE IF NOT EXISTS analysis(
    id_analysis INTEGER PRIMARY KEY autoincrement,
    root_folder TEXT NOT NULL,
    date_analysis TEXT NOT NULL,
    id_project INTEGER,
    id_user INTEGER
);