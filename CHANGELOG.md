Changelog
=========

## 2021-09-10

This version brings significat changes. The two main goals for this update are
to make the program less resource intensive, and to prepare for porting the
program into other operating systems.

- Now uses sqlite instead of google sheets

    - Works even without internet connection.
    - Presumably less taxing on the system since it doesn't have to send every
    data to an outside storage. 
    - Data is now available only on one system. 

        Previous versions allowed access of data on different systems by using
        the  spreadsheets website or app.

    - Doesn't come with a dashboard 

        The program now has no dashboard/frontend for the data it has 
        gathered. I decided to turn the project into just an
        activity tracker that is designed to allow other projects to access its
        data. One can create a dashboard by just accessing the sqlite db.
        
- Better file structure 

    - New directories and file names 
    - see `./docs/structure.md` for more info

- More modularity. 

    - Each *.py file is dedicated for one purpose with the main.py as the 
    controller.
    - Makes the progam easier to maintain and port to other OS. If a part of 
    the program becomes incompatible to other systems, it will be easy to 
    replace just one component.

## 2021-04-??

Project create. This version used google sheets as a database which made it easy
to create a dashboard, and to make it available to other platforms because 
accessing the data required only a browser. 


