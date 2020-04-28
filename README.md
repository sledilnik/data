[![Build Status](https://travis-ci.com/sledilnik/data.svg?branch=master)](https://travis-ci.com/sledilnik/data)

# Slovenia COVID-19 Data Collection - Sledilnik.org

Visualized at [COVID-19 Sledilnik Home Page](https://covid-19.sledilnik.org) 

Collecting and organising data as they come in from various sources. 
Master tables are at https://tinyurl.com/sledilnik-gdocs

This repository is for organising our collaboration better: wikis, issues etc.


# Updating data

Trigger rebuild at [Travis CI](https://travis-ci.com/github/sledilnik/data)


## Changelog

### 2020-04-28
- **stats.csv**: rename `cases.active.todate` to `cases.active` [issue #11](https://github.com/sledilnik/data/issues/11)

### 2020-04-26
- **stats.csv**: added `tests.regular.*` and `tests.ns-apr20.*` to separate tests for [National Survey April 2020](https://covid19.biolab.si/)
- **stats.csv**: changed `tests.positive.*` to report positive actual tests (slightly higher than `cases.confirmed.*`)

### 2020-04-25
- **dict-municipality.csv**: fixed region for Gornja Radgona (was `lj` - is `ms` now)

### 2020-04-20
- **dict-age-groups.csv**: age groups with population (total, male, female)

### 2020-04-18
- **dict-retirement_homes.csv**: added tax-id for each retirement home
