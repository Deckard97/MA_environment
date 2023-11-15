import csv
import json
import random
from faker import Faker

fake = Faker()

while True:
    # Generate fake sentences
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

    # Generate the complete Article creation JSON string
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
    with open('sentence.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([comment])

    # Write article request body to articles.csv
    with open('articles.csv', 'w', newline='') as file:
        file.write(article_json + '\n')