# -*- encoding: utf-8 -*-
##############################################################################
#
#mario chogllo
#
##############################################################################

{
    "name" : "Database Auto-Backup",
    "version" : "1.0",
    "author" : "Mario Chogllo",
    "website" : "www.goberp.com",
    "category" : "Modulo Base",
    "description": """The Database Auto-Backup system enables the user to make configurations for the automatic backup of the database.
User simply requires to specify host & port under IP Configuration & database(on specified host running at specified port) and backup directory(in which all the backups of the specified database will be stored) under Database Configuration.

Automatic backup for all such configured databases under this can then be scheduled as follows:  
                      
1) Go to Administration / Configuration / Scheduler / Scheduled Actions
2) Schedule new action(create a new record)
3) Set 'Object' to 'db.backup' and 'Function' to 'schedule_backup' under page 'Technical Data'
4) Set other values as per your preference""",
    "depends" : [],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["bkp_conf_view.xml","backup_data.xml"],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
