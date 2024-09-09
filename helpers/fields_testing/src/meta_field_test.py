from django.db import models
from .class_field_test import ClassFieldTest


class MetaFieldTest(ClassFieldTest):
    '''
    Allows testing Meta nested class in django model. 
    Similar to `ClassFieldTest`.

    Example:
    ```
    class ConstraintsFieldTest(MetaFieldTest, SimpleTestCase):
        klass = User
        field_name = 'constraints'
        value = [
            models.UniqueConstraint(
                fields=['telephone_prefix', 'telephone_number'],
                name='telephone_number_with_prefix_unique'
            )
        ]
    ```
    '''
    @property
    def field(self) -> models.Field:
        "Gets nestred Meta class inside model class."
        return getattr(self.klass._meta, self.field_name)
