Check list for child_tracker:

- DataBase:
    - SQLWRAPPER 
    - configuration object
- Whatsapp:
    - message Handler
    - Managment API
- API GateWay Endpoints:
    - save_new_message - child phone
    - check_for_deleted_messages - child phone
    - command execution - mother phone
- *CronTab tasks:*
    - restart mother & child waha sessions
    - check for deleted messages
- *Installation process:*
    - Journey - Web Interface (Installation Steps):
        1. Mother & child Phone
        2. Group Name
        3. How many days should messages be saved? (Default is 2 days, Whatsapp allows 2 weeks before a user is unable  
           to delete it's msg)
        4. Prepre Mother phone  -> QR
        5. Prepre Child phone   -> QR
        - Create DB file + Table
        6. Installation Complete + How To's
    - Web Interface
    - Updated Configuration File

