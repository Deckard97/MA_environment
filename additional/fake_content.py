import csv
import json
import random
from faker import Faker

fake = Faker()

# Initialize line counters for both files
sentence_line_count = 0
article_line_count = 0
max_lines = 1000

while True:
    # Generate fake data
    comment = fake.sentence()
    article_title = fake.sentence()
    article_description = fake.text()
    article_body = fake.text()

    words = article_description.split()
    if len(words) < 10:
        max_num_tags = len(words)
    else:
        max_num_tags = random.randint(1, 10)
    tags = random.sample(words, max_num_tags)
    tags = [s.replace('.', '') for s in tags]

    article = {
        "article": {
            "title": article_title,
            "description": article_description,
            "body": article_body,
            "tagList": tags
        }
    }
    article_json = json.dumps(article)

    # Write sentence to sentence.csv
    with open('./JMeter/sentence.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if sentence_line_count < max_lines:
            writer.writerow([comment])
            sentence_line_count += 1
        else:
            file.seek(0)
            file.truncate()
            writer.writerow([comment])
            sentence_line_count = 1

    # Write article request body to articles.csv
    with open('./JMeter/articles.csv', 'a', newline='') as file:
        if article_line_count < max_lines:
            file.write(article_json + '\n')
            article_line_count += 1
        else:
            file.seek(0)
            file.truncate()
            file.write(article_json + '\n')
            article_line_count = 1
