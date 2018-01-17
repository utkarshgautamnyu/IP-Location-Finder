#!/usr/bin/env bash

set -e

pip install virtualenv
virtualenv .env
.env/bin/pip install -r requirements.txt