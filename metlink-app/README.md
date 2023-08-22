# Instructions

When the repository is first cloned, the database is not present in `static/gtfs.db`. This database contains three tables:

- routes - the names, destinations and colours of routes
- shapes - 
- trips

To refresh the database, run the app using

```
python main.py
```

Now visit: https://localhost:8080/tasks/refresh_gtfs_db - this triggers a job which builds the database

The table names and values are unchanged from the gtfs spec that can be found here https://gtfs.org