"""Provides support for dealing with Mongo Documents."""
from bson.objectid import ObjectId
from tavi import Connection
from tavi.base.documents import BaseDocument, BaseDocumentMetaClass
from tavi.errors import TaviConnectionError
from tavi.utils.timer import Timer
import datetime
import inflection
import logging

logger = logging.getLogger(__name__)

class DocumentMetaClass(BaseDocumentMetaClass):
    """MetaClass for Documents. Sets up the database connection, infers the
    collection name by pluralizing and underscoring the class name, and sets
    the collection fo rthe Document.

    """

    def __init__(cls, name, bases, attrs):
        super(DocumentMetaClass, cls).__init__(name, bases, attrs)
        cls._collection_name = inflection.underscore(inflection.pluralize(name))

    @property
    def collection(cls):
        """Returns a handle to the Document collection."""
        if not Connection.database:
            raise TaviConnectionError(
                "Cannot connect to MongoDB. Did you call "
                "'tavi.connection.Connection.setup'?")
        return Connection.database[cls._collection_name]

    @property
    def collection_name(cls):
        """Returns the name of the Document collection."""
        return cls._collection_name

class Document(BaseDocument):
    """Represents a Mongo Document. Provides methods for saving and retrieving
    and deleting Documents.

    """
    __metaclass__ = DocumentMetaClass

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self._id = None

    @property
    def bson_id(self):
        """Returns the BSON Id of the Document."""
        return self._id

    def delete(self):
        """Removes the Document from the collection."""
        timer = Timer()
        with timer:
            result = self.__class__.collection.remove({ "_id": self._id })

        logger.info("(%ss) %s DELETE %s", timer.duration_in_seconds(),
                self.__class__.__name__, self._id)

        if result.get("err"):
            logger.error(result.get("err"))

    @classmethod
    def find(cls, *args, **kwargs):
        """Returns all Documents in collection that meet criteria. Wraps
        pymongo's *find* method and supports all of the same arguments.

        """
        timer = Timer()
        with timer:
            results = cls.collection.find(*args, **kwargs)

        logger.info("(%ss) %s FIND %s, %s (%s record(s) found)",
            timer.duration_in_seconds(), cls.__name__, args, kwargs,
            results.count())

        return [cls(**result) for result in results]

    @classmethod
    def find_all(cls):
        """Returns all Documents in collection."""
        return cls.find()

    @classmethod
    def find_by_id(cls, id_):
        """Returns the Document that matches *id_* or None if it cannot be
        found.

        """
        return cls.find_one(ObjectId(id_))

    @classmethod
    def find_one(cls, spec_or_id=None, *args, **kwargs):
        """Returns one Document that meets criteria. Wraps pymongo's find_one
        method and supports all of the same arguments.

        """
        timer = Timer()
        with timer:
            result = cls.collection.find_one(spec_or_id, *args, **kwargs)

        found_record, num_found = None, 0

        if result:
            found_record, num_found = cls(**result), 1

        logger.info("(%ss) %s FIND ONE %s, %s, %s (%s record(s) found)",
            timer.duration_in_seconds(),
            cls.__name__, spec_or_id, args, kwargs, num_found)

        return found_record

    def save(self):
        """Saves the Document by inserting it into the collection if it does
        not exist or updating it if it does. Returns True if save was
        successful. Ensures that the Document is valid before saving and
        returns False if it was not.

        If the document model has a field named 'created_at', this field's
        value will be set to the current time when the document is inserted.

        """
        if not self.valid:
            return False

        collection = self.__class__.collection
        timer = Timer()
        operation = None

        if "last_modified_at" in self.fields:
            self.last_modified_at = datetime.datetime.utcnow()

        if self.bson_id:
            operation = "UPDATE"
            with timer:
                result = collection.update({ "_id": self._id },
                    { "$set": self.data })

            if result.get("err"):
                logger.error(result.get("err"))
        else:
            operation = "INSERT"
            if "created_at" in self.fields:
                self.created_at = datetime.datetime.utcnow()

            with timer:
                self._id = collection.insert(self.data)

        logger.info("(%ss) %s %s %s, %s",
            timer.duration_in_seconds(), self.__class__.__name__, operation,
            self.data, self._id)
        return True

class EmbeddedDocument(BaseDocument):
    """Represents a single EmbeddedDocument. Supports an *owner* attribute that
    indicates the owning Document.

    """
    def __init__(self, **kwargs):
        super(EmbeddedDocument, self).__init__(**kwargs)
        self.owner = None