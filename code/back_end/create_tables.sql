-- PostgreSQL Database--

create schema deepvision;
commit;

-- users table
create table deepvision.users (
    id          SERIAL PRIMARY KEY,
	username        VARCHAR(50) NOT NULL,
	password        VARCHAR(20) NOT NULL, 
	companyName     VARCHAR(50), 
	account_created TIMESTAMP);
commit;

-- project table
create table deepvision.projects (
    id          SERIAL PRIMARY KEY, -- this would then be used as the name of the S3 bucket
	projectOwnerId  SERIAL REFERENCES deepvision.users(id),
	projectName     VARCHAR(50), 
	project_created TIMESTAMP);
commit;

-- user project table
create table deepvision.user_project(
    projectId   SERIAL REFERENCES deepvision.projects(id),
    userId      SERIAL REFERENCES deepvision.users(id)
    );
commit;

-- project status table
create table deepvision.project_status(
    id              SERIAL PRIMARY KEY,
    projectId       SERIAL REFERENCES deepvision.projects(id),
    last_accessed   TIMESTAMP,
    timestamp       TIMESTAMP,
    cost            FLOAT,
    numPhoto        INT,
	performance     FLOAT);
commit;

-- check schema
select * from information_schema.schemata;

-- check tables created
SELECT * from information_schema.tables 
where table_schema = 'deepvision';




