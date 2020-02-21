import click
import pymongo
import logging

import src

DEFAULT_MONGO_URL = 'mongodb://%s:%s@127.0.0.1' % ('root', 'example')
DEFAULT_DB_NAME = 'google-mail'
DEFAULT_COLLECTION_NAME = 'mails'


# todo: skip, debug, batch_size
@click.command()
@click.option('--mongodb', 'mongo_string', default=DEFAULT_MONGO_URL, help='Connection string for mongodb instance',
              show_default=True)
@click.option('--db-name', 'dbname', default=DEFAULT_DB_NAME, help='MongoDB database name', show_default=True)
@click.option('--collection-name', 'collname', default=DEFAULT_COLLECTION_NAME, help='MongoDB collection name',
              show_default=True)
@click.option('--init', default=False, help='Force deleting and re-initializing the MongoDB collection', type=bool,
              show_default=True)
@click.option('--body', default=False,
              help='Will index all body content, stripped of HTML/CSS/JS etc. Adds fields: "body" and "body_size"',
              type=bool, show_default=True)
@click.argument('filename', type=click.Path(exists=True))
def run(mongo_string, dbname, collname, init, body, filename):
    """Print FILENAME.

    FILENAME path to mbox file
    """
    logging.basicConfig(level=logging.INFO)

    mongodb = pymongo.MongoClient(mongo_string)
    uploader = src.Uploader(mongodb, dbname, collname)

    if init is True:
        uploader.drop_collection()
        logging.info('Collection "%s" in database "%s" dropped and will be recreated' % (collname, dbname))

    # execution
    src.Parser(filename, uploader).parse(body)


if __name__ == '__main__':
    run()
