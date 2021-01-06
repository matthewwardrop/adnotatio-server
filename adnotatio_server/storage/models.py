import json
import time

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from .util import to_snake_case, unique_constructor


Base = declarative_base()


@unique_constructor(
    lambda id=None, email=None: (id, email),
    lambda query, id=None, email=None: query.filter(Author.id == id) if id is not None else query.filter(Author.email == email)
)
class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    email = Column(String(512), index=True)
    name = Column(String(512))
    avatar = Column(String(1024))


@unique_constructor(
    lambda id=None, uuid=None: (id, uuid),
    lambda query, id=None, uuid=None: query.filter(Comment.uuid == uuid) if uuid is not None else query.filter(Comment.id == id)
)
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)

    uuid = Column(String(512), index=True)

    authority = Column(String(512))
    document_id = Column(String(512))
    document_version = Column(String(512))

    reply_to_id = Column(Integer, ForeignKey('comments.id'))

    text = Column(Text)
    annotations = Column(Text)  # JSON

    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship(Author, lazy="joined")

    ts_created = Column(BigInteger)
    ts_updated = Column(BigInteger)

    is_resolved = Column(Boolean)

    replies = relationship(
        'Comment',
        backref=backref('reply_to', remote_side=[id]),
        lazy='select'
    )

    @classmethod
    def fromJSON(cls, d, author_info):
        assert 'uuid' in d

        comment = cls(uuid=d['uuid'])

        comment.authority = d['context']['authority']
        comment.document_id = d['context']['documentId']
        comment.document_version = d['context']['documentVersion']

        assert comment.author is None or comment.author.email == author_info.email, "Author mismatch (upstream: {}, current: {}).".format(comment.author.email, author_info.email)

        comment.reply_to_id = Comment(uuid=d.get('replyTo')).id if d.get('replyTo') else None
        comment.text = d.get('text')
        comment.annotations = json.dumps(d.get('annotations', []))

        if author_info.email:
            comment.author = Author(email=author_info.email)
            comment.author.name = author_info.name
            comment.author.avatar = author_info.avatar
        else:
            comment.author = None

        if not comment.ts_created:
            comment.ts_created = int(time.time() * 1000)
        comment.ts_updated = int(time.time() * 1000)

        comment.is_resolved = d.get('isResolved', False)

        return comment

    def toJSON(self):
        return {
            'uuid': self.uuid,
            'context': {
                'authority': self.authority,
                'documentId': self.document_id,
                'documentVersion': self.document_version
            },
            'replyTo': self.reply_to.uuid if self.reply_to else None,
            'text': self.text,
            'annotations': json.loads(self.annotations) if self.annotations else None,
            'authorEmail': self.author.email if self.author else None,
            'authorName': self.author.name if self.author else None,
            'authorAvatar': self.author.avatar if self.author else None,
            'tsCreated': self.ts_created,
            'tsUpdated': self.ts_updated,
            'isResolved': self.is_resolved
        }

    def is_author(self, author_info):
        return self.author is not None and self.author.email == author_info.email

    def apply_patch(self, patch, author_info):
        illegal_fields = set(patch.keys()).difference(self.patchable_fields_for_user(author_info))
        if illegal_fields:
            raise RuntimeError("User {} attempted to modify illegal fields: {}".format(author_info.email, illegal_fields))

        for attribute, value in patch.items():
            setattr(self, to_snake_case(attribute), value)
        return self

    def patchable_fields_for_user(self, author_info):
        if self.is_author(author_info):
            return ['text', 'authorName', 'authorAvatar', 'isResolved']
        return ['isResolved']
