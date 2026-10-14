#!/bin/bash
# Two chained MapReduce jobs: baskets -> product pairs -> pair counts.
#   docker exec -it namenode bash /hadoop-data/map_reduce/run_basket_pairs.sh
set -e
MR=/hadoop-data/map_reduce
bash $MR/run_job.sh retail_basket_pairs_1 "${1:-online_retail.csv}" 4
bash $MR/run_job.sh retail_basket_pairs_2 hdfs:/user/root/output/retail_basket_pairs_1 2
echo ">> Top 15 product pairs bought together:"
hdfs dfs -cat /user/root/output/retail_basket_pairs_2/part-* | sort -t$'\t' -k2,2nr | head -15
