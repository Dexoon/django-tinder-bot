#!/bin/sh
echo "UUID=`uuidgen`"> /uuid/.env.uuid
exec "$@"