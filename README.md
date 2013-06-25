# TFBS database

## Install

<code>
create database tfbs;
grant all privileges on tfbs to dj_ango;
</code>

## Populate

python manage.py syncdb
python manage.py loaddata main/fixtures/genes.json
python manage.py loaddata main/fixtures/motifs.json
cd data
./connect_genes.py
./make_tfbs.py

## Start server

<code>
python manage.py runserver
</code>

