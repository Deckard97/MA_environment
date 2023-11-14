import csv
from faker import Faker

fake = Faker()

while True:
    # Generate fake sentences
    comment = fake.sentence()
    article = fake.sentence()

    # Write comment to comments.csv
    with open('comments.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([comment])

    # Write article to articles.csv
    with open('articles.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([article])