#!/bin/sh
flask --app moj init-db
exec flask run --host=0.0.0.0 -p 5500