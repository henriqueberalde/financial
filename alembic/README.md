Generic single-database configuration.
### Create a Revision
* ```alembic -n development revision -m "some description"```

### Upgrade / Downgrade migrations on development env
* ```alembic -n development upgrade head```
* ```alembic -n development downgrade -1```

### Upgrade / Downgrade migrations on test env
* ```alembic -n test upgrade head```
* ```alembic -n test downgrade -1```
