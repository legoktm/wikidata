#!/bin/bash
#$ -l h_rt=168:00:00
#$ -l virtual_free=50M
#$ -j y
#$ -b y
#$ -wd /home/legoktm/rewrite
#$ -o /home/legoktm/public_html/en_removal.log

/home/legoktm/rewrite/pwb.py /home/legoktm/wikidata/enwiki_removal.py -pt:0
