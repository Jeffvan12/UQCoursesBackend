### Details 
This project is primarily used to scrap a UQ program list. Then add the details of the program and courses to a postgres database. 

A very simple server was also implemented, made with sanic,  to connect to the front end website.




### Setting up 


Create a python3.7x virtual environment 

Install the requirements with ``pip(version) install -r requirements.txt``

First change the *creates_tables.py* to connect to your postgres server, and then run it to create the tables. 

Build the tables with *create_tables.py*



### Running 

Either just use *uq_scraper.py* to scarp courses and add them to your database, or run *index.py* to create a server. 










### To run server using Gunicorn 
``` 
index:app --bind 0.0.0.0:1338 --worker-class sanic.worker.GunicornWorkerr
```


### TODOs for the project 
 - [ ] Improve the error handling 
 - [ ] Add comments to the code 

