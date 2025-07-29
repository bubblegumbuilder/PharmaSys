USE pharmacy;

TRUNCATE TABLE pharmacy.drugs;
TRUNCATE TABLE pharmacy.users;

--error part(ammu py)
LOAD DATA INFILE 'C:/Users/Kurt Jio Sumilao/Documents/GitHub/PharmaSys/[SQL]Sheets/DrugDatabase.csv'
INTO TABLE pharmacy.drugs
FIELDS TERMINATED BY ','
ENCLOSED BY ''
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/Users/Kurt Jio Sumilao/Documents/GitHub/PharmaSys/[SQL]Sheets/LoginData.csv'
INTO TABLE pharmacy.users
FIELDS TERMINATED BY ','
ENCLOSED BY ''
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;