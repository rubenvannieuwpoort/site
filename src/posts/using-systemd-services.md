{
    "title": "Using systemd services",
    "date": "2025-10-08",
    "show": true
}

Most modern general-purpose Linux distributions use [systemd](https://systemd.io) to manage the various services that are needed by the system. If you for example, run a home server, it can be convenient to use a service to ensure that your server starts automatically after boot.

To understand how systemd works in detail, I recommend reading the "man pages" for `systemd`, `systemctl`, `systemd.unit`, and `systemd.service`. Here, I'll just show by example, by showing how I've set up the service for my home server.


## Managing services

You can list the services that are currently running with `sudo systemctl list-units --type=service`.


## Setting up a systemd service

To create a `server` service, we need to create the service file `/etc/systemd/system/server.service`:
```
[Unit]
Description=Server Daemon

# start this service automatically after network is online
After=network-online.target

# when this service is started, start network service
Wants=network-online.target


[Service]

# automatically restart after 5 seconds on crash
Restart=on-failure
RestartSec=5s

# command to run (can also contain CLI options)
ExecStart=/home/ruben/bin/server

# environment variables
Environment="DOMAIN=rubenvannieuwpoort.nl"
Environment="WWW_ROOT=/home/ruben/www"


[Install]

# needed for services that can start at boot
WantedBy=multi-user.target
```

After adding the service file, you need to run the following to actually enable and start the service:
```
# reload the configuration
sudo systemctl daemon-reload
# enable the service on boot
sudo systemctl enable server
# start the service now
sudo systemctl start server
```

Optionally, the last two commands can be combined as `sudo systemctl start server.service --now`.


## Reading logs

To read logs, we can use `journalctl`:
```
sudo journalctl -u server
```

The keys used to control `journalctl` are similar to `less` and `vim`. You can use `G` to go to the end of logs, `j`/`k` to move down/up a single line, and `CTRL+u`/`CTRL+d` to scroll up one page at a time. Press `q` to exit the log viewer.

Alternatively, you can use the `-f` CLI flag to "follow" the last logs.
