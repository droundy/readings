#!/bin/sh

set -ev

curl https://droundy.pythonanywhere.com/readings > readings
curl https://droundy.pythonanywhere.com/schedule > schedule
