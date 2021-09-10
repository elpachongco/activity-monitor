Changelog
=========

## 2021-09-10

This version brings important changes.  making the program less
resource intensive, preparation for porting the program into other operating 
systems, code cleanup, and project organization. 

- Now uses sqlite instead of google sheets

    - Works even without internet connection
    - Presumably less taxing on the system since it doesn't have to send every
    data to an outside storage. 
    - Data is now available only on one system. 

        Previous version allowed
        access of data on different systems by using the  spreadsheets 
        website or app.

    - Now doesn't come with a dashboard 

        The program now has no dashboard/frontend for the data it has 
        gathered. I decided to turn the projects into just an
        activity tracker that allows other projects to access its data. This
        means one can create a dashboard by just accessing the sqlite db.

- Better file structure 

    - New directories and file names 
    - see `./docs/structure.md` for more info

- More modularity 

## 2021-04-??

- Project create 
