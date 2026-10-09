#!/bin/sh
set -eu
cat > Snakefile <<'SOURCE'
rule all:
    input: 'baseline.tsv'

rule score:
    input: 'input.tsv'
    output: 'baseline.tsv'
    shell: 'python3 transform.py {input} {output}'
SOURCE
cat > transform.py <<'SOURCE'
import csv
import sys
with open(sys.argv[1], newline='') as source, open(sys.argv[2], 'w', newline='') as target:
    reader = csv.DictReader(source, delimiter='\t')
    writer = csv.writer(target, delimiter='\t', lineterminator='\n')
    writer.writerow(['id', 'score'])
    for row in reader:
        writer.writerow([row['id'], int(row['value']) ** 2 - 1])
SOURCE
printf 'id\tvalue\na\t3\nb\t5\n' > input.tsv
printf 'id\tscore\na\t8\nb\t24\n' > baseline.tsv
