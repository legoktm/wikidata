#!/bin/bash
#$ -l h_rt=00:10:00
#$ -l virtual_free=10M
#$ -j y
#$ -wd /home/legoktm/rewrite
#$ -o /home/legoktm/public_html/wd_autopatrol.log

/home/legoktm/rewrite/pwb.py /home/legoktm/wikidata/autopatrol.py -pt:0
