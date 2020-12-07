# Chat Apps

I have built a chat app in a few different ways. 

Initially I set out to build a simple command line chat app with python, to get a better understanding of sockets, but it ended up being a good opportunity to learn about a lot more, and test my skills. 

It led to me getting to grips with basic encryption (asymmetric and symmetric keys) and ORMs (had only used raw SQL queries with pg-promise/psycopg2 before now), among other things. 

## Python Version
Uses the built in socket library, as well as the RSA and cryptography packages for encryption. 

### To Use:
Server - simply run python3 server.py. This will allow local connections to port 8004 currently
Client - run python3 client.py, enter a username, and start chatting. 
