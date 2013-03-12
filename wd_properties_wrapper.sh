#!/bin/bash
#$ -l h_rt=72:00:00
#$ -l virtual_free=300M
#$ -l arch='sol'
#$ -j y
#$ -b y
#$ -l sql-s1-rr=1
#$ -wd /home/legoktm/rewrite
#$ -o /home/legoktm/public_html/wd_properties.log

/home/legoktm/rewrite/pwb.py /home/legoktm/wikidata/wikidata_properties.py -pt:0
