#!/bin/bash
set -e

# Wait for Elasticsearch to start up before doing anything.
until curl -s http://elasticsearch:9200/_cluster/health | grep -E 'yellow|green'; do
  echo "Waiting for Elasticsearch..."
  sleep 1
done

# Create the ingest pipeline
curl -X PUT "http://elasticsearch:9200/_ingest/pipeline/apache_custom" -H 'Content-Type: application/json' -d'
{
  "description": "Parse Apache logs to include request duration",
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": [
          "%{IPORHOST:client.ip} %{USER:ident} %{USER:auth} \\[%{HTTPDATE:apache.access.time}\\] \\"%{WORD:apache.access.method} %{DATA:apache.access.url} HTTP/%{NUMBER:apache.access.http_version}\\" %{NUMBER:apache.response.status_code} (?:%{NUMBER:apache.access.body_sent.bytes}|-) \\"%{DATA:apache.access.referrer}\\" \\"%{DATA:apache.access.agent}\\" %{NUMBER:duration}"
        ]
      }
    }
  ]
}'
