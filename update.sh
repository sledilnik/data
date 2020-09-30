#!/bin/bash

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
curl -s http://api.mizs.si/stats/ | jq > json/mizs-stats.json
