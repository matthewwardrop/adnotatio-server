import os

from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.migration import MigrationContext
from flask import Blueprint, request

from .auth import default_author_resolver
from .jsonapi import jsonapify_wrap
from .storage.database import init_db
from .storage.models import Comment


class AdnotatioApiBlueprint(Blueprint):

    def __init__(self, db_uri='sqlite:////tmp/adnotatio.db', db_auto_upgrade=True, author_resolver=None, enable_cors=False):
        Blueprint.__init__(self, 'adnotatio', __name__)
        self.author_resolver = author_resolver or default_author_resolver
        self.enable_cors = enable_cors
        self.db_uri = db_uri
        self.db_auto_upgrade = db_auto_upgrade

        @self.before_app_first_request
        def init():
            """Docstring for public function."""
            self.db_init()

        @self.before_request
        def clear_cache():
            if hasattr(self.db, '_unique_cache'):
                del self.db._unique_cache

        if enable_cors:
            @self.after_request
            def after_request(response):
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
                return response

        @self.route('/whoami')
        @jsonapify_wrap
        def whoami():
            """Returns information about the user, in particular their name, email and avatar uri."""
            author_info = self.author_resolver()
            return {
                'type': 'authors',
                'id': author_info.email,
                'attributes': {
                    'name': author_info.name,
                    'email': author_info.email,
                    'avatar': author_info.avatar
                }
            }

        @self.route('/comments')
        @jsonapify_wrap
        def comments():
            """Return all comments associated with a particular document."""

            return list(
                {'type': 'comments', 'id': c.uuid, 'attributes': c.toJSON()}
                for c in self.db.query(Comment).filter(
                    Comment.authority == request.args.get('authority'),
                    Comment.document_id == request.args.get('documentId')
                ).all()
            )

        @self.route('/comments/<uuid>')
        @jsonapify_wrap
        def get_comment(uuid):
            """Return a comment identified by its uuid in a given document context."""

            comment = self.db.query(Comment).filter(
                Comment.authority == request.args.get('authority'),
                Comment.document_id == request.args.get('documentId'),
                Comment.uuid == uuid
            ).first()

            if not comment:
                raise ValueError("Unknown comment for uuid '{}'.".format(uuid))

            return {
                'type': 'comments',
                'id': comment.uuid,
                'attributes': comment.toJSON()
            }

        @self.route('/comments/<uuid>', methods=['put', 'patch'])
        @jsonapify_wrap
        def put_comment(uuid):
            """Update the attributes for a given comment."""

            comment = Comment.fromJSON(request.json.get('data', {}).get('attributes'), author_info=self.author_resolver())
            self.db.add(comment)
            self.db.commit()

            return {
                'type': 'comments',
                'id': comment.uuid,
                'attributes': comment.toJSON()
            }

    def db_init(self):
        self.db = init_db(self.db_uri)
        if self.db_revision is None or self.db_auto_upgrade:
            self.db_upgrade()
        return self

    @property
    def db_revision(self):
        conn = self.db.connection()

        context = MigrationContext.configure(conn)
        return context.get_current_revision()

    def db_create_revision(self, message, autogenerate=True):
        command.revision(self._alembic_config, message=message, autogenerate=autogenerate)
        return self

    def db_upgrade(self):
        command.upgrade(self._alembic_config, "head")
        return self

    def db_downgrade(self, revision):
        command.downgrade(self._alembic_config, revision)
        return self

    @property
    def _alembic_config(self):
        dir = os.path.join(os.path.dirname(__file__), 'migrations')
        config = AlembicConfig(os.path.join(dir, 'alembic.ini'))
        config.set_main_option('script_location', dir)
        config.set_main_option('sqlalchemy.url', self.db_uri)
        config.set_main_option('adnotatio_server_path', os.path.dirname(__file__))
        return config
