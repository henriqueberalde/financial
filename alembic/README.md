Generic single-database configuration.
### Create a Revision
* ```alembic -n development revision -m "some description"```

### Upgrade / Downgrade migrations on development env
* ```alembic -n development upgrade head```
* ```alembic -n development downgrade -1```
