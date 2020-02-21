# MongoDB Gmail

Inspired by [elasticsearch-gmail](https://github.com/oliver006/elasticsearch-gmail). 
Parse your "gmail takeout file" and indexing mail messages into MongoDB. 
After that you can use some aggregation functions for insights or analytics your inbox

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

**First**, go [here](https://www.google.com/settings/takeout/custom/gmail) and download your Gmail mailbox, depending on the amount of emails you have accumulated this might take a while.

The downloaded archive is in the [mbox format](http://en.wikipedia.org/wiki/Mbox) and Python provides libraries to work with the mbox format so that's easy.

**Second**, install python dependecies

```bash
vend/bin/pip install -r requirements.txt
```

**Thirdly** Run MongoDB, you can use docker-compose for starting mongodb and web-view panel

```bash
docker-compose up 
```

**Fourthly** Run parser.

```bash
venv/bin/python ./cli.py --init=true ~/path/to/your/mail.mbox
```

### Usage

Connection to the MongoDB instance:

```
mongo -u root -p example --authenticationDatabase admin

> use google-mail
switched to db google-mail
```

And exec aggregation functions.
* See [examples](https://github.com/Rpsl/mongodb-gmail/tree/master/examples)  
* See [documentation of MongoDB Aggregation framework](https://docs.mongodb.com/manual/aggregation/)
```
> db.mails.aggregate([
	{ $match: { labels: { $in: ['inbox'] } } },
	{ $group: {_id: "$from", total: {$sum : 1} } },
	{ $sort : {"total": -1 } }
])
```

### Options

```bash
/mongodb-gmail: ./venv/bin/python ./cli.py --help
Usage: cli.py [OPTIONS] FILENAME

  Print FILENAME.

  FILENAME path to mbox file

Options:
  --mongodb TEXT          Connection string for mongodb instance  [default:
                          mongodb://root:example@127.0.0.1]
  --db-name TEXT          MongoDB database name  [default: google-mail]
  --collection-name TEXT  MongoDB collection name  [default: mails]
  --init BOOLEAN          Force deleting and re-initializing the MongoDB
                          collection  [default: False]
  --body BOOLEAN          Will index all body content, stripped of HTML/CSS/JS
                          etc. Adds fields: "body" and "body_size"  [default:
                          False]
  --help                  Show this message and exit.
```

### Todo

[] Repair parse body
[] Extract examples (aggregate functions) to the personal classes and execute from cli
[] Add `--report` option for executing the aggregates and generate report files