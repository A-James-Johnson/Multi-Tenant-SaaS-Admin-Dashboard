CREATE DATABASE IF NOT EXISTS saas_admin
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'saas_user'@'localhost'
IDENTIFIED BY 'saas_password';

GRANT ALL PRIVILEGES ON saas_admin.* TO 'saas_user'@'localhost';

FLUSH PRIVILEGES;