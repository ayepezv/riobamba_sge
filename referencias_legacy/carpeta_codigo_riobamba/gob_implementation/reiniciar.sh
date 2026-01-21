#!/bin/bash
#sudo service jetty restart
#sudo service postgresql restart
#sudo sv stop siim
ps -ef|grep open
kill -9 `ps -ef|grep -v grep |grep openerp| awk '{print $2}'`
#cd /home/siim/siim_gob
cd /home/mario/oerp/siim_gob
nohup ./openerp-server --addons-path=addons/,../addonsgob --no-database-list &
