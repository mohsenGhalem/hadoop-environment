# MapReduce jobs (Hadoop Streaming + Python)

Each job is a folder here containing `mapper.py`, `reducer.py`
(optional `combiner.py`, plus any helper/lookup files). Input files go in `../data/`.

## Workflow
```bash
# 1. create a job from the template
bash map_reduce/new_job.sh my_job

# 2. edit map_reduce/my_job/mapper.py and reducer.py

# 3. test locally (seconds, no Hadoop) — fix bugs here first
bash map_reduce/test_job.sh my_job myfile.csv

# 4. run on the cluster
docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh my_job myfile.csv [num_reducers]

# full output
docker exec namenode hdfs dfs -cat /user/root/output/my_job/part-*
```
Jobs in the YARN UI: http://localhost:8089 — history: http://localhost:8188

## How to design a job — 3 questions
1. **What do I group by?** → that is the mapper's **key**
2. **What do I need per group?** → that is the mapper's **value**
3. **How do I combine the values of one group?** → that is the **reducer**

| Task | Mapper emits | Reducer does |
|---|---|---|
| Word count | `word  1` | sum |
| Total/avg/min/max per group | `group  number` | sum / mean / min / max |
| Distinct values | `value  ""` | print key once |
| Filter rows (grep) | the row, only if it matches | *no reducer* (map-only) |
| Inverted index | `word  doc_id` | set of doc ids |
| Top-N overall | `"all"  item,score` | sort, keep N |
| Join two files | `join_key  TAG,fields` (tag = which file) | pair rows with different tags |
| Co-occurrence | `wordA,wordB  1` | sum |

## Rules to remember
- Key and value are separated by a **TAB**; the key is everything before the first tab.
- The reducer sees keys **sorted**, and all values of one key **together** — but a reducer
  handles many keys, so always detect key changes (the template uses `itertools.groupby`).
- Never assume order of *values* within a key, or that one mapper sees the whole file.
- **Combiner** = mini-reducer run on each mapper's output to cut network traffic. Only valid
  if the operation is associative (sum, min, max, count). For an *average*, emit `sum,count`
  pairs instead of combining averages.
- Map-only job: delete `reducer.py` — output is just the mapper's lines.
- Output folder is overwritten by `run_job.sh` (Hadoop itself refuses to overwrite).
- Only Python's standard library is available on the nodes; add `pip install` lines to the
  main `Dockerfile` if you need more.
- Debug output → `print(..., file=sys.stderr)`; it appears in the task logs, not the result.

## Examples
- `wordcount/` — `bash map_reduce/test_job.sh wordcount file.txt`
- `sales_by_category/` — CSV aggregation: `bash map_reduce/test_job.sh sales_by_category sales.csv`

## Online Retail II jobs (data/online_retail.csv, 1,067,371 rows)
A "valid sale" = invoice not starting with C, quantity > 0, price > 0.
Real products = StockCode starting with 5 digits (POST, M, DOT, BANK CHARGES… are fees).

| Job | Question | MapReduce idea |
|---|---|---|
| `retail_data_quality` | How dirty is the data? | counting + combiner |
| `retail_revenue_by_country` | Revenue, orders, avg order value per country | aggregation, distinct count in reducer |
| `retail_monthly_revenue` | Revenue trend per month | time key + combiner |
| `retail_top_products` | Top 5 products per country | top-N per group |
| `retail_basket_pairs_1` + `_2` | Which products are bought together? | **two chained jobs** (group by invoice → count pairs) |

```bash
docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh retail_revenue_by_country online_retail.csv
docker exec -it namenode bash /hadoop-data/map_reduce/run_basket_pairs.sh
```
