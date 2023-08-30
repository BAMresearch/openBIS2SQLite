# postgres-to-sql

Scripts to convert openbis postgres dumps to a sqlite readable transaction

## how to get dump file

1. connect to postgres database
1.1 docker
- start a shell in a running docker container (`sudo docker exec -it <container> sh`)
- generate dump with `pg_dump --create --no-owner --inserts --attribute-inserts -Fc -U <user> -f <filename> openbis_prod`, default user being `postgres`
- copy the created file from docker to local with `sudo docker cp <container>:/home/openbis/openbis/servers/<filename> <destination>`
