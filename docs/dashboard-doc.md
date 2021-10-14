# Dashboard documentation

The dashboard works out of the box and is intentionally shipped with the built
files to prevent the user from installing additional tools to use or configure.

The project uses reactjs, and chartjs. These are also shipped with the program
instead of fetched from a cdn to make the program work offline and for faster
development. 

## Running the dashboard

To run, simply cd to `./dashboard/` and execute the run script: `run.py` or
`python3 run.py`. 

```bash
$ cd ./dashboard
$ ./run.py
```

This will start a simple flask server that will serve the index.html files on
`http://yourIpAddress:5000`. Open with a browser.

The page will be accessible to all devices in the network. To disable this,
remove the items `"--host"`, and `"0.0.0.0"` from the list `runFlaskCmd` on
`../dashboard/run.py`.
