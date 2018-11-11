import json

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from .util import unique_constructor


Base = declarative_base()


@unique_constructor(
    lambda email: email,
    lambda query, email: query.filter(Author.email == email)
)
class Author(Base):
    __tablename__ = 'authors'

    email = Column(String, primary_key=True)
    name = Column(String)
    avatar = Column(String)


@unique_constructor(
    lambda uuid: uuid,
    lambda query, uuid: query.filter(Comment.uuid == uuid)
)
class Comment(Base):
    __tablename__ = 'comments'

    uuid = Column(String, primary_key=True)

    authority = Column(String)
    document_id = Column(String)
    document_version = Column(String)

    reply_to = Column(String, ForeignKey('comments.uuid'))

    text = Column(Text)
    annotations = Column(Text)  # JSON

    author_email = Column(String, ForeignKey('authors.email'))
    author = relationship(Author, lazy="joined")

    ts_created = Column(Integer)
    ts_updated = Column(Integer)

    is_resolved = Column(Boolean)

    replies = relationship(
        "Comment", backref=backref('host', remote_side=[uuid])
    )

    @classmethod
    def fromJSON(cls, d, author_info):
        assert 'uuid' in d

        comment = cls(uuid=d['uuid'])

        comment.authority = d['context']['authority']
        comment.document_id = d['context']['documentId']
        comment.document_version = d['context']['documentVersion']

        assert comment.author is None or comment.author.email == author_info.email

        comment.reply_to = d.get('replyTo')
        comment.text = d.get('text')
        comment.annotations = json.dumps(d.get('annotations'))

        comment.author_email = author_info.email
        if comment.author_email:
            comment.author = Author(email=comment.author_email)
            comment.author.name = author_info.name
            comment.author.avatar = author_info.avatar

        comment.ts_created = d.get('tsCreated')
        comment.ts_updated = d.get('tsUpdated')

        comment.is_resolved = d.get('isResolved')

        return comment

    def toJSON(self):
        return {
            'uuid': self.uuid,
            'context': {
                'authority': self.authority,
                'documentId': self.document_id,
                'documentVersion': self.document_version
            },
            'replyTo': self.reply_to,
            'text': self.text,
            'annotations': json.loads(self.annotations),
            'authorEmail': self.author_email,
            'authorName': self.author.name if self.author else None,
            'authorAvatar': self.author.avatar if self.author else None,
            'tsCreated': self.ts_created,
            'tsUpdated': self.ts_updated,
            'isResolved': self.is_resolved
        }
