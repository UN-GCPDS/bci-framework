#!/usr/bin/bash

echo "Removing old files"
mv material-components-web.min.css material-components-web.min.css.old
mv material-components-web.min.js material-components-web.min.js.old
echo "Downloading new files"
wget https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css
wget https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js
echo "Done"
