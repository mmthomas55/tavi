# Tavi

Tavi (as in [Rikki Tikki Tavi](http://en.wikipedia.org/wiki/Rikki-Tikki-Tavi)) is an extremely thin Mongo object mapper for Python. It is a thin abstraction over [pymongo](http://api.mongodb.org/python/current/) that allows you to easily model your applications and persist your data in MongoDB.

## Getting Started

Install using pip:

    pip install Tavi

or clone the project and run:

    python setup.py install

Define your models:

```python
from tavi import document, fields

class Product(document.Document):
    name        = fields.StringField("name", required=True)
    sku         = fields.StringField("sku", required=True)
    description = fields.StringField("description", required=True)
    price       = fields.FloatField("price", min_value=0)
```

Use your models to create and find documents:

    >>> product = Product(name="Spam", sku="123", price=2.99)

    >>> product.valid
    False

    >>> product.errors.full_messages
    ['Description is required']

    >>> product.description = "A tasty canned precooked meat product."

    >>> product.valid
    True

    >>> product.save()
    True

    >>> for p in Product.find():
    ...     print p.name
    ...
    Spam

For more details see [Using Tavi](#using-tavi).


### Dependencies

* pymongo >= 2.5.2
* inflection >= 0.2.0

### Contributing

#### Issues / Roadmap

Use GitHub [issues](https://github.com/bnadlerjr/tavi/issues) for reporting bugs and feature requests. This library is meant to be lightweight so I probably won't be adding much more support outside of some new field types. Feel free to submit pull requests for any critical features you think may be missing.

#### Patches / Pull Requests

* Fork the project.
* Make your feature addition or bug fix.
* Add tests for it. This is important so I don't break it in a future version unintentionally.
* Commit, do not mess with version or history (if you want to have your own version that is fine, but please bump version in a commit by itself I can ignore when I pull).
* Send me a pull request. Bonus points for topic branches.

## <a id="using-tavi"></a>Using Tavi

### Connecting to MongoDB

### Defining Document Objects

Document objects inherit from tavi.documentDocument which provides both field support and persistence. You define a document like this:

```python
class Order(tavi.document.Document):
    name     = tavi.fields.StringField("name", required=True)
    address  = tavi.fields.EmbeddedField("address", Address)
    email    = tavi.fields.StringField("email", required=True)
    pay_type = tavi.fields.StringField("pay_type", required=True)
```

Any ``Order`` classes that are instantiated will have ``name``, ``address``, ``email``, and ``pay_type`` attributes. See [validations](#validations) for how to determine of the objects attributes are valid. Document objects also support persistence methods (see [saving](#saving-documents) and [finding](#finding-documents)).

### Defining Embedded Document Objects

Embedded Document objects inherit from tavi.document.EmbeddedDocument and only have support for fields. Embedded Documents are defined the same way as Documents and support [validations](#validations).

```python
class Address(tavi.document.EmbeddedDocument):
    street      = tavi.fields.StringField("street")
    city        = tavi.fields.StringField("city")
    state       = tavi.fields.StringField("state")
    postal_code = tavi.fields.StringField("postal_code")
```

### Fields

Fields are how Tavi maps the attributes in your objects to attributes in the document for your collections in MongoDB. All fields inherit from ``tavi.base.field.BaseField`` which provides some common [validations](#validations). If you need to add your own field types you may inherit from either ``tavi.base.field.BaseField`` or one of the other field types. Any classes that inherit from ``tavi.base.field.BaseField`` must implement the ``validate`` method and call ``super`` in order for validations to work. For example:

```python
    class MyCustomField(tavi.base.field.BaseField):
        def validate(self, instance, value):
            super(MyCustomField, self).validate(instance, value)
            # Your validation logic goes here...
```

#### Basic Fields

Three basic field types are supported:

* ``tavi.fields.FloatField``
* ``tavi.fields.IntegerField``
* ``tavi.fields.StringField``

#### Embedded Fields

#### Embedded List Fields

### <a id="validations"></a>Validations

### Persistence

#### <a id="saving-documents"></a>Saving Documents

#### <a id="finding-documents"></a>Finding Documents

### Exceptions

### Using pymongo
