#!/bin/bash

set -e

pg_restore -U $POSTGRES_USER -d $POSTGRES_DB /dumps/ifg_produz010721.backup