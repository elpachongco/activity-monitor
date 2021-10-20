# Activity Dashboard  

This is the experimental dashboard for the activity database.

## Design plan 📝	

This part contains the things I'm considering while designing the dashboard.

### My usage/activity - Wants

Without thinking about the implementation, the things I want to know about
my usage/activity are:

- Statistics about me, today
    - My performance today vs my usual (avg?) performance
    - Current day start time vs my usual start time 👎
    - Inactivity vs activity ratio today ✅

- Stats about me, long-term
    - My most active hours in a day ✅	
    - My most active days of the week  ✅	
    - My average day duration
    - Total activity duration per day in a week ✅	
    - 10-day activity vs inactivity ✅	
    - Ratio of activity and inactivity per day in the last x days 
    - calendar view of 1-year daily activity duration.


### Components plan

Based on the items above

1. Calendar view, like github commit activity. Except that it contains activity
duration for each day, from today to 365 days ago.

2. Doughnut chart of today's activity vs inactivity ratio.

3. Line graph. Lines: total activity per day, total Inactivity per day, total
day length, and their averages.

4. Histogram. Contains all 24 hours, shows which hours I am most active in.

5. Word map of most common words encountered for window names.
	- Loop through all window names, loop through words in window names, tally
	total occurence for any word encountered. 
    - Then, scale, position words to fit the container.

## TODO

- Make it so that the dashboard retrieves data for a set interval and updates
the components accordingly.
