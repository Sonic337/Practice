#!/bin/bash
DATE=$(date +%Y-%m-%d)
mkdir -p ~/backups/$DATE
cp -r ~/practice/ ~/backups/$DATE/
echo "Backup done for $DATE"

