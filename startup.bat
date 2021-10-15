:: run commands in new cmd window with "start cmd /k"
:: use /c to auto exit when finish
start cmd /c py .\main.py
cd .\dashboard
start cmd /c py .\run.py
:: pyw - run python program in headless mode (no window spawned)
