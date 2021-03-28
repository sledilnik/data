#!/bin/sh

REPO="github.com/sledilnik/data"

# copy new data into repo
git checkout master
git add csv/*
git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
git remote add upstream https://${GITHUB_TOKEN}@${REPO}.git > /dev/null 2>&1
git push --quiet upstream master
git remote remove upstream
