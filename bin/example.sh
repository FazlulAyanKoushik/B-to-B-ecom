#!/bin/bash
source ~/env/bin/activate
cd ~/project

# Usage:
# */1 * * * * ~/project/bin/sample.sh live > ~/logs/cron.log 2>&1

python projectile/manage.py sample --settings=projectile.settings_$1