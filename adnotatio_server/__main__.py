import argparse
import logging
import sys

from flask import Flask

from adnotatio_server.auth import AdnotatioAuthorInfo
from adnotatio_server.blueprint import AdnotatioApiBlueprint


def parse_args(args):
    """Parse arguments passed in from the CLI."""
    argparser = argparse.ArgumentParser(description="Development server")
    argparser.add_argument('-p', '--port', type=int, default=8000, help='Port for HTTP server (default=%d).' % 8000)
    argparser.add_argument('-d', '--debug', action='store_true', default=False, help='Debug mode.')
    argparser.add_argument('--enable-cors', action='store_true', default=False, help='Enable CORS policy allowing cross-domain access.')
    argparser.add_argument('--db-uri', default='sqlite:////tmp/adnotatio.db', help='The database URI to use to store annotations and comments.')
    argparser.add_argument('--db-create-revision', help='Create a new alembic revision.')
    return argparser.parse_args(args)


def main(**overrides):
    """Launch a development Annotatio compatible server for testing purposes."""
    logger = logging.getLogger(__name__)
    args = parse_args(sys.argv[1:])

    for key, value in overrides.items():
        if not hasattr(args, key):
            logger.warning("Invalid override key: {}.".format(key))
            continue
        setattr(args, key, value)

    app = Flask(__name__)
    app.register_blueprint(
        AdnotatioApiBlueprint(
            enable_cors=args.enable_cors,
            db_uri=args.db_uri,
            author_resolver=lambda: AdnotatioAuthorInfo("Dummy User", "dummy@dummy.com", None)
        ),
        url_prefix='/api'
    )

    if args.db_create_revision is not None:
        app.blueprints['adnotatio'].db_create_revision(args.db_create_revision)
    else:
        logger.info('Starting server on port %s with debug=%s', args.port, args.debug)
        app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=False)


if __name__ == '__main__':
    main()
