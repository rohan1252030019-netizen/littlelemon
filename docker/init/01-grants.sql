-- Extra privileges so that the Django test runner can create and drop
-- the test database (test_littlelemon).
GRANT ALL PRIVILEGES ON `littlelemon`.* TO 'lemon'@'%';
GRANT ALL PRIVILEGES ON `test_littlelemon`.* TO 'lemon'@'%';
FLUSH PRIVILEGES;
