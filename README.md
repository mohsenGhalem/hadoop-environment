# Hadoop 3.4.3 Cluster in Docker + a Python MapReduce Toolkit

> **This repository is a fork of [spraharaj-projects/hadoop-environment](https://github.com/spraharaj-projects/hadoop-environment).**
> The original provides a multinode Hadoop cluster in Docker Compose. This fork keeps its structure and
> fixes it so it builds again today, makes it run on Apple Silicon Macs as well as Linux/WSL2, and adds a
> small toolkit for writing, testing and running **Hadoop Streaming MapReduce jobs in Python**, with
> worked examples on a real e-commerce dataset.

---

## Contents
1. [What's in the box](#whats-in-the-box)
2. [Quick start](#quick-start)
3. [What changed compared to the original](#what-changed-compared-to-the-original)
4. [How the MapReduce template works](#how-the-mapreduce-template-works)
5. [Example jobs](#example-jobs)
6. [Using the Online Retail II dataset](#using-the-online-retail-ii-dataset)
7. [Troubleshooting](#troubleshooting)

---

## What's in the box

Seven containers on one Docker network (`hadoop_network`):

| Container | System | Role | Web UI |
|---|---|---|---|
| `namenode` | HDFS | File-system metadata: which blocks make up each file and where they are | http://localhost:9870 |
| `datanode1-3` | HDFS | Store the data blocks (replicated) | – |
| `resourcemanager` | YARN | Schedules CPU/memory for jobs | http://localhost:8089 |
| `nodemanager1` | YARN | Runs map and reduce tasks | http://localhost:8042 |
| `historyserver` | YARN | Timeline / history of finished jobs | http://localhost:8188 |

Versions: **Hadoop 3.4.3 · Java 11 (Eclipse Temurin) · Python 3.11** (on every node, for Hadoop Streaming).

Two project folders are mounted into the `namenode` container:

| On your machine | Inside `namenode` | Used for |
|---|---|---|
| `data/` | `/hadoop-data/input` | input files for jobs (not committed to git) |
| `map_reduce/` | `/hadoop-data/map_reduce` | your mappers, reducers and the runner scripts |

```
hadoop-environment/
├── Dockerfile              # base image: Java + Python + Hadoop + conf/
├── docker-compose.yml      # the 7 services
├── start-cluster.sh        # download Hadoop, build images, start everything
├── conf/                   # core-, hdfs-, mapred-, yarn-site.xml (baked into the image)
├── namenode/ datanode/ resourcemanager/ nodemanager/ historyserver/   # per-role Dockerfile + run.sh
├── map_reduce/             # MapReduce toolkit + example jobs  (see below)
└── data/                   # your input data (git-ignored)
```

---

## Quick start

**Prerequisites:** Docker Desktop (macOS/Windows) or Docker Engine + Compose v2 (Linux/WSL2), about 4 GB free disk.

```bash
git clone <this-fork-url> hadoop-environment
cd hadoop-environment
bash start-cluster.sh
```

`start-cluster.sh` does everything and is safe to run again:

1. Downloads the Hadoop 3.4.3 tarball **once, on your machine**, with resume support (fast Apache CDN first, archive as fallback), and skips this step if a valid tarball is already there.
2. Creates `hadoop_network` if it doesn't exist.
3. Builds the base image `hadoop-base:3.4.3`, plus an `amd64` copy used only by the history server (see [Apple Silicon](#apple-silicon-and-the-history-server)).
4. Builds the role images and starts the cluster (`docker compose up -d --build`).

The first run takes a few minutes; later runs are cached and take seconds. Check it's up:

```bash
docker ps                                  # 7 containers
docker exec namenode hdfs dfsadmin -report # 3 live datanodes
```

Stop / remove:

```bash
docker compose stop        # stop, keep data
docker compose down        # remove containers, keep HDFS volumes
docker compose down -v     # remove everything including HDFS data
```

---

## What changed compared to the original

### Fixes so the cluster builds and runs
| Problem in the original | Fix |
|---|---|
| `openjdk:11-jdk` was removed from Docker Hub | Java copied from `eclipse-temurin:11-jdk`, from its real path `/opt/java/openjdk` |
| `software-properties-common` no longer exists in Debian *trixie* (base of `python:3.11`) | Install only what Hadoop needs: `curl procps perl hostname` |
| Hadoop 3.3.6 removed from the main mirror; the archive is throttled (~35 KB/s) and drops connections | Upgraded to **Hadoop 3.4.3**; tarball downloaded on the host with resume + mirror fallback, then `COPY`'d into the image |
| `mapred-site.xml` hard-coded `/opt/hadoop-3.3.6/` → MapReduce jobs could not start | Paths updated to `/opt/hadoop-3.4.3/` |
| History server crashed on Apple Silicon (`leveldbjni` has no ARM64 library) | `historyserver` runs as `linux/amd64` under emulation (Rosetta), all other services stay native |
| History stored in `/tmp` and lost on rebuild (the `YARN_CONF_…` env var in its Dockerfile is never read) | LevelDB timeline store path set explicitly in `yarn-site.xml` to the `hadoop_historyserver` volume |
| `start-cluster.sh` failed if the network existed and continued after a failed build | Idempotent network creation, stops on the first error, uses `docker compose` (v2) |

### Improvements
- **Slim base image** (`python:3.11-slim`): ~50 MB instead of ~1 GB, much faster builds, especially the emulated `amd64` one.
- History server started with the current `yarn timelineserver` command (the old one is deprecated).
- Obsolete `version:` key removed from `docker-compose.yml`; `.dockerignore` / `.gitignore` added.
- **MapReduce toolkit** in `map_reduce/`: job template, local tester, generic cluster runner, job chaining. Explained next.
- Example jobs: word count, a CSV aggregation, and five analyses of the Online Retail II dataset, all checked against pandas.

---

## How the MapReduce template works

Jobs are written in plain Python and run through **Hadoop Streaming**: Hadoop sends each input line to your
script on **stdin** and reads `key<TAB>value` lines from its **stdout**. No Java and no Hadoop libraries needed.

### One folder = one job

```
map_reduce/
├── _template/          # copied by new_job.sh
│   ├── mapper.py
│   └── reducer.py
├── my_job/
│   ├── mapper.py       # required
│   ├── reducer.py      # optional: without it the job is map-only
│   ├── combiner.py     # optional: picked up automatically
│   └── lookup.csv      # optional: any other file is shipped to the nodes too
├── new_job.sh          # create a job from the template
├── test_job.sh         # run a job locally, without Hadoop
├── run_job.sh          # run a job on the cluster
└── run_basket_pairs.sh # example of two chained jobs
```

### The workflow

```bash
# 1. create a job from the template
bash map_reduce/new_job.sh my_job

# 2. edit map_reduce/my_job/mapper.py and reducer.py

# 3. test locally in seconds: same steps as Hadoop on one machine
bash map_reduce/test_job.sh my_job myfile.csv

# 4. run on the cluster (myfile.csv must be in data/)
docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh my_job myfile.csv

# full output
docker exec namenode hdfs dfs -cat /user/root/output/my_job/part-*
```

### What happens to your data

```
data/myfile.csv ──► HDFS ──► input splits ──► mapper.py (one copy per split, in parallel)
                                                 │  key<TAB>value lines
                                                 ▼
                               partition by key → sort → [combiner.py]
                                                 │  shuffle: all lines of a key → one reducer
                                                 ▼
                                   reducer.py (receives lines SORTED by key)
                                                 │
                                                 ▼
                              /user/root/output/<job>/part-00000 … in HDFS
```

### The two templates

**`_template/mapper.py`** reads one record per line and prints zero, one or many `key<TAB>value` pairs:

```python
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key = line          # TODO: what do you group by?
    value = 1           # TODO: what do you need per group?
    print(f"{key}\t{value}")
```

**`_template/reducer.py`** receives the mapper output **sorted by key**. All lines of one key are
consecutive, so `itertools.groupby` hands you one key at a time:

```python
for key, group in groupby(parse(sys.stdin), key=lambda kv: kv[0]):
    values = [v for _, v in group]
    result = sum(int(v) for v in values)   # TODO: combine the values of this key
    print(f"{key}\t{result}")
```

> Streaming does **not** call your reducer once per key with a list of values, as the Java API does.
> It sends one sorted stream that contains many keys, which is why the reducer must detect key changes.

### Designing a job: three questions
1. **What do I group by?** → the mapper's **key**
2. **What do I need per group?** → the mapper's **value**
3. **How do I combine one group's values?** → the **reducer**

| Task | Mapper emits | Reducer does |
|---|---|---|
| Count / sum per group | `group  number` | sum |
| Average per group | `group  value,1` | sum both, divide at the end |
| Distinct values | `value  ""` | print each key once |
| Filter rows | the row, only if it matches | *no reducer* (map-only) |
| Top-N per group | `group  item,score` | rank, keep N |
| Join two files | `join_key  TAG,fields` | pair rows with different tags |
| Pairs / co-occurrence | needs **two jobs** (group by basket, then by pair) | |

### What `run_job.sh` does for you
```
run_job.sh <job> <input> [num_reducers]
```
- Uploads `data/<input>` to HDFS at `/user/root/input/<input>`, or reuses it if it's already there (`REUPLOAD=1` forces a fresh upload).
- `<input>` can be a folder in `data/`, or `hdfs:/some/path` to read a **previous job's output** (job chaining).
- Adds `-combiner` if `combiner.py` exists; makes the job map-only if there is no `reducer.py`.
- Ships every other file in the job folder to the nodes (`-files`).
- Deletes the old output folder first (Hadoop refuses to overwrite).
- Splits input into **32 MB** pieces by default, so even small files run as several parallel map tasks. Change it with `SPLIT_MB=16 …`.
- Prints the first 30 result lines.

### What `test_job.sh` does
It runs exactly what Hadoop does, on one machine:
```
cat data/<file> | mapper.py | sort | [combiner.py | sort] | reducer.py
```
with `LC_ALL=C` so `sort` orders keys byte by byte, like Hadoop. Use `-` as the file name to read stdin
(handy for testing chained jobs) and `LINES_SHOWN=all` to see the full output.

### Rules that keep results correct
- Separate key and value with a **TAB**; the key is everything before the first tab.
- A mapper sees only **its split**, never the whole file, and the header line only reaches the first split.
- **Skip malformed lines, don't crash.** A failing task is retried 4 times, then the whole job fails.
- A **combiner** may run 0, 1 or many times. Only use one for associative operations (sum, count, min, max),
  never for distinct counts or averages, and never filter in it, because it only sees partial results.
- Debug with `print(..., file=sys.stderr)`; it goes to the task logs, not into the result.
- Only the Python standard library is installed on the nodes. Add `RUN pip install …` to the `Dockerfile` if you need more.

---

## Example jobs

| Job | Input | What it shows |
|---|---|---|
| `wordcount` | `data/file.txt` | the classic: `word 1` → sum |
| `sales_by_category` | `data/sales.csv` | CSV parsing; count/total/avg/min/max per group |
| `retail_data_quality` | Online Retail II | profiling dirty data; reducer reused as combiner |
| `retail_revenue_by_country` | Online Retail II | revenue, distinct orders and average order value per country (no combiner, and why) |
| `retail_monthly_revenue` | Online Retail II | time key `YYYY-MM`; combiner |
| `retail_top_products` | Online Retail II | top-N within each group |

```bash
docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh wordcount file.txt
docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh retail_revenue_by_country online_retail.csv
```

More detail on each job: [`map_reduce/README.md`](map_reduce/README.md).

---


## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Build stuck on the Hadoop download | Run `start-cluster.sh` again: it resumes. The tarball is kept in the project folder. |
| `historyserver` exits with `UnsatisfiedLinkError … leveldbjni` | It must run as `amd64`: rebuild with `start-cluster.sh`. On a Mac, enable *Docker Desktop → Settings → General → Use Rosetta for x86_64/amd64 emulation*. |
| First `amd64` build is slow | One-time download of the `amd64` base layers; cached afterwards. |
| `Output directory … already exists` | Use `run_job.sh` (it deletes old output) or `hdfs dfs -rm -r <dir>`. |
| Job fails, nothing obvious in the console | Open the job in http://localhost:8089 → *Logs* to see the Python traceback from `stderr`. |
| Edited `conf/*.xml` but nothing changed | The config is baked into the image: run `start-cluster.sh` again. |

---

## Credits & license
Original cluster setup by [spraharaj-projects/hadoop-environment](https://github.com/spraharaj-projects/hadoop-environment).
This fork keeps the original's license (Apache License 2.0). Issues and pull requests are welcome.
