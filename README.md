# Project 1

This project is a book review application, wherein users
can create accounts, search for books through a preloaded
database of 5000 books, and write reviews for books, consisting
of a text component and rating on a scale of 1 to 5. Users
can also go to a url where if they enter an ISBN, a page
will be returned containing relevant info in JSON format.

In the application.py file is all the logic of the application
including routes, database queries, form submission, etc. In the 
templates folder there are 5 templates which the routes direct the user
to, including a base template which serves as the base for the other
four templates to build off of. 

The import.py file is a script that imports the 5000 pre-selected
books into the database.
