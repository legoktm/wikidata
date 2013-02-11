#!/bin/bash
#$ -l h_rt=00:30:00
#$ -l virtual_free=300M
#$ -l arch='sol'
#$ -l sql-s1-rr=1
#$ -j y
#$ -b y
#$ -wd /home/legoktm/rewrite
#$ -o /home/legoktm/public_html/wd_redir.log

/home/legoktm/rewrite/pwb.py /home/legoktm/wikidata/wikidata_redir.py
