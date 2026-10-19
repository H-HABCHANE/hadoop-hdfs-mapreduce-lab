# Hadoop HDFS & MapReduce Lab

A hands-on lab that runs a complete Hadoop 3.4.3 cluster (HDFS + YARN) on a single machine with Docker Compose, and uses it to explore HDFS block storage, replication and fault tolerance, and MapReduce jobs written in Python with Hadoop Streaming.

Lab exercises from the Master 2 Big Data course at Université de Perpignan Via Domitia.

## Cluster architecture

`docker-compose.yml` starts 8 containers from the `apache/hadoop:3.4.3` image (Java 11, Hadoop 3.4.3, Python 3):

| Service | Role | Port on host |
|---|---|---|
| `namenode` | HDFS metadata (NameNode web UI) | 9870 |
| `datanode` ×4 | HDFS block storage (scaled with `--scale datanode=4`) | – |
| `resourcemanager` | YARN resource manager (web UI) | 8088 |
| `nodemanager` | YARN node manager, runs map/reduce tasks (4 GB) | – |
| `historyserver` | MapReduce job history (web UI) | 19888 |

Main settings (passed as environment variables and turned into Hadoop XML configuration by the image):

- replication factor `3`;
- fast dead-DataNode detection (`heartbeat.recheck-interval` = 30 s, a node is declared dead after ~90 s instead of ~10 min);
- 512 MB containers for the ApplicationMaster, map and reduce tasks;
- a single YARN `default` queue.

The `tp/` folder is mounted into the `namenode` container at `/tp`.

## Repository structure

```
.
├── docker-compose.yml        # 8-container Hadoop cluster
└── tp/
    ├── texte.txt             # small text for WordCount
    ├── temperatures.txt      # station;date;temperature measurements
    ├── generer_ventes.py     # generates a synthetic sales file (date;city;product;price)
    ├── mapper.py             # WordCount mapper: emits (word, 1)
    ├── reducer.py            # WordCount reducer: sums counts per word
    ├── mapper_ventes.py      # sales mapper: emits (city, price)
    ├── reducer_somme.py      # sums prices per city (also usable as a combiner)
    ├── mapper_temp.py        # temperature mapper: emits (station, temperature)
    ├── reducer_moyenne.py    # average per station (NOT safe as a combiner)
    ├── reducer_max.py        # maximum per station (safe as a combiner)
    ├── mapper_moy.py         # emits (station, sum, count)
    ├── combiner_moy.py       # adds sums and counts, same format in and out
    └── reducer_moy.py        # adds sums and counts, divides only at the end
```

## Requirements

- Docker with Docker Compose v2
- ~8 GB of RAM and ~10 GB of free disk space

## Getting started

```bash
docker compose pull
docker compose up -d --scale datanode=4
docker compose ps
```

Web interfaces:

- NameNode: http://localhost:9870
- ResourceManager: http://localhost:8088
- Job history: http://localhost:19888

Open a shell inside the cluster:

```bash
docker compose exec namenode bash
hdfs dfsadmin -report | grep -E "Live datanodes|Dead datanodes"
```

## HDFS experiments

Run inside the `namenode` container.

```bash
# Basic commands
hdfs dfs -mkdir -p /data/texte /data/ventes /data/temp
hdfs dfs -put /tp/texte.txt /data/texte/

# Generate a 150,000-line sales file (4,876,381 bytes, fixed random seed)
python3 /tp/generer_ventes.py 150000 > /tmp/ventes.csv

# Default 128 MB blocks: 1 block
hdfs dfs -put /tmp/ventes.csv /data/ventes/ventes_128.csv
hdfs fsck /data/ventes/ventes_128.csv -files -blocks -locations

# 1 MB blocks: 5 blocks (4 x 1,048,576 + 682,077 bytes)
hdfs dfs -D dfs.blocksize=1048576 -put /tmp/ventes.csv /data/ventes/ventes_1mo.csv
hdfs fsck /data/ventes/ventes_1mo.csv -files -blocks -locations

# Cost of replication (file size vs. space used with 3 copies)
hdfs dfs -du -h /data/ventes
hdfs dfs -setrep -w 2 /data/ventes/ventes_1mo.csv
hdfs dfs -setrep -w 3 /data/ventes/ventes_1mo.csv
```

### Fault tolerance

Stop a DataNode from the host, then watch HDFS from the `namenode` container:

```bash
# host
docker stop tp-hadoop-datanode-2

# namenode container
for i in $(seq 1 50); do
  echo "$(date +%T) $(hdfs fsck / 2>/dev/null | grep -E 'Under-replicated blocks')"
  sleep 3
done

# host, once done
docker start tp-hadoop-datanode-2
```

Observed run: the node was declared dead about 80 s after being stopped, all 7 blocks became under-replicated (100 %), and HDFS restored 3 copies of every block within about 10 s. Files remained readable throughout, since each block still had 2 live replicas.

## MapReduce with Python (Hadoop Streaming)

Test locally, with `sort` playing the role of shuffle & sort:

```bash
cat /tp/texte.txt | python3 /tp/mapper.py | sort | python3 /tp/reducer.py
```

Run on the cluster:

```bash
STREAMING=/opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.3.jar

# WordCount
hadoop jar $STREAMING \
  -files /tp/mapper.py,/tp/reducer.py \
  -mapper "python3 mapper.py" -reducer "python3 reducer.py" \
  -input /data/texte -output /data/wc_py

# Revenue per city: one map task per block (5 blocks -> 5 map tasks)
hadoop jar $STREAMING \
  -files /tp/mapper_ventes.py,/tp/reducer_somme.py \
  -mapper "python3 mapper_ventes.py" -reducer "python3 reducer_somme.py" \
  -input /data/ventes/ventes_1mo.csv -output /data/ca_ville

# Same job with a combiner
hadoop jar $STREAMING \
  -files /tp/mapper_ventes.py,/tp/reducer_somme.py \
  -mapper "python3 mapper_ventes.py" \
  -combiner "python3 reducer_somme.py" -reducer "python3 reducer_somme.py" \
  -input /data/ventes/ventes_1mo.csv -output /data/ca_ville_comb

# Two reducers: each key goes to hash(key) mod 2
hadoop jar $STREAMING -D mapreduce.job.reduces=2 \
  -files /tp/mapper_ventes.py,/tp/reducer_somme.py \
  -mapper "python3 mapper_ventes.py" -reducer "python3 reducer_somme.py" \
  -input /data/ventes/ventes_1mo.csv -output /data/ca_2red
```

Effect of the combiner on the revenue-per-city job (observed counters):

| Counter | Without combiner | With combiner |
|---|---|---|
| Map output records | 150,000 | 150,000 |
| Combine output records | 0 | 40 |
| Reduce input records | 150,000 | 40 |
| Reduce shuffle bytes | 2,386,248 | 844 |

The output is identical in both cases, because a sum is associative.

### The average pitfall

Using the averaging reducer as a combiner computes an average of averages and gives a wrong result. The fix is to carry `(sum, count)` pairs and divide only in the reducer:

```bash
head -2 /tp/temperatures.txt > /tmp/t1.txt
tail -n +3 /tp/temperatures.txt > /tmp/t2.txt
hdfs dfs -put -f /tmp/t1.txt /tmp/t2.txt /data/temp/

hadoop jar $STREAMING \
  -files /tp/mapper_moy.py,/tp/combiner_moy.py,/tp/reducer_moy.py \
  -mapper "python3 mapper_moy.py" -combiner "python3 combiner_moy.py" \
  -reducer "python3 reducer_moy.py" \
  -input /data/temp -output /data/temp_moy_ok
```

| Station | `reducer_moyenne.py` as combiner | `mapper_moy` / `combiner_moy` / `reducer_moy` |
|---|---|---|
| LYON | 30.3 | 30.3 |
| PERP | 20.0 (wrong) | 23.5 (correct) |

## Monitoring jobs

```bash
yarn application -list -appStates ALL
yarn logs -applicationId <application_id> | more
```

## Stopping the cluster

| Goal | Command | HDFS data |
|---|---|---|
| Pause | `docker compose stop` | kept |
| Resume | `docker compose start` | kept |
| Reset | `docker compose down` then `docker compose up -d --scale datanode=4` | deleted |
| Free disk space | `docker compose down` then `docker image rm apache/hadoop:3.4.3` | deleted |

## Limitations

All containers share the same CPU, memory and disk, so this setup demonstrates Hadoop's mechanisms (blocks, replication, failures, map/shuffle/reduce), not its performance. The 4 DataNodes report the same physical disk (capacity is counted 4 times), there is a single rack, and since the NodeManager does not run alongside a DataNode, map tasks are rack-local rather than data-local.
