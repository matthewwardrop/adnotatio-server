from flask import Blueprint, request

from .auth import default_author_resolver
from .jsonapi import jsonapify_wrap
from .storage.database import init_db
from .storage.models import Comment


class AdnotatioApiBlueprint(Blueprint):

    def __init__(self, db_uri='sqlite:////tmp/adnotatio.db', author_resolver=None, enable_cors=False):
        Blueprint.__init__(self, 'adnotatio', __name__)
        self.author_resolver = author_resolver or default_author_resolver
        self.enable_cors = enable_cors

        @self.before_app_first_request
        def init():
            """Docstring for public function."""
            self.db = init_db(db_uri)

        if enable_cors:
            @self.after_request
            def after_request(response):
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
                return response

        @self.route('/comments')
        @jsonapify_wrap
        def load():
            return list(
                {'type': 'comments', 'id': c.uuid, 'attributes': c.toJSON()}
                for c in self.db.query(Comment).filter(
                    Comment.authority == request.args.get('authority'),
                    Comment.document_id == request.args.get('documentId'),
                    Comment.document_version == request.args.get('documentVersion')
                ).all()
            )

        @self.route('/comments/<uuid>')
        @jsonapify_wrap
        def get(uuid):

            context = {
                "authority": request.args.get('authority'),
                "documentId": request.args.get('documentId'),
                "documentVersion": request.args.get('documentVersion'),
                "documentAuthorEmails": request.args.get('documentAuthorEmails')
            }
            context.update(request.args)

            return self.db[context['uuid'][0]]

        @self.route('/comments/<uuid>', methods=['put', 'patch'])
        @jsonapify_wrap
        def post(uuid):
            from .storage.models import Comment
            self.db.add(Comment.fromJSON(request.json.get('data', {}).get('attributes'), author_info=self.author_resolver()))
            self.db.commit()
            return True
