PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS puzzle_table;
DROP TABLE IF EXISTS android_metadata;
DROP TABLE IF EXISTS room_master_table;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  resetGuid TEXT UNIQUE NOT NULL
);

CREATE TABLE `puzzle_table` (
    `id` TEXT UNIQUE NOT NULL,
    `puzzle` TEXT NOT NULL,
    `timeCreated` TEXT NOT NULL,
    `lastModified` TEXT NOT NULL,
    `puzzleIcon` TEXT NOT NULL,
    PRIMARY KEY(`id`)
    );
COMMIT;