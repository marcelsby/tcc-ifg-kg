#!/bin/bash

set -e

pg_restore -U postgres -d ifg_produz /dumps/ifg_produz010721.backup