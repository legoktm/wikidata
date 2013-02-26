#!/bin/bash
#$ -l h_rt=20:00:00
#$ -l virtual_free=300M
#$ -l arch='sol'
#$ -l sql-s1-rr=1
#$ -l sql-s2-rr=1
#$ -l sql-s3-rr=1
#$ -l sql-s4-rr=1
#$ -l sql-s5-rr=1
#$ -l sql-s6-rr=1
#$ -l sql-s7-rr=1
#$ -j y
#$ -wd /home/legoktm/rewrite
#$ -o /home/legoktm/public_html/wd_redir.log

/home/legoktm/rewrite/pwb.py /home/legoktm/wikidata/wikidata_redir.py -pt:0
