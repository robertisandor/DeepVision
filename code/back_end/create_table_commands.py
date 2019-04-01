# schema: deepvision

# create projects table
cmds = [ """create table deepvision.projects 
(projectID INT PRIMARY KEY SERIAL
companyID INT NOT NULL
projectName VARCHAR(50), 
numPhoto INT, 
created TIMESTAMP);"""]

# create users table

cmds = [ """create table deepvision.projects 
(projectID INT PRIMARY KEY SERIAL
companyID INT NOT NULL
projectName VARCHAR(50), 
numPhoto INT, 
created TIMESTAMP);"""]