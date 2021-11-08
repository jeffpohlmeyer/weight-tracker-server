-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(256) NOT NULL,
    "email" VARCHAR(256) NOT NULL,
    "hashed_password" VARCHAR(256) NOT NULL,
    "is_active" INT NOT NULL  DEFAULT 1,
    "is_verified" INT NOT NULL  DEFAULT 0,
    "token" VARCHAR(512),
    "token_expiration" TIMESTAMP,
    "is_superuser" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
