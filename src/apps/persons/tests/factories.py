import factory
from factory.django import DjangoModelFactory

from apps.persons.choices import MentionType
from apps.persons.models import Person, PersonMention
from apps.sources.tests.factories import SourceFactory


class PersonFactory(DjangoModelFactory[Person]):
    """Build persons with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = Person

    first_name = "John"
    middle_name = ""
    last_name = factory.Sequence(lambda n: f"Doe{n}")


class PersonMentionFactory(DjangoModelFactory[PersonMention]):
    """Build person mentions with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = PersonMention
        skip_postgeneration_save = True

    person = factory.SubFactory(PersonFactory)
    source = factory.SubFactory(SourceFactory)
    mention_type = MentionType.PROFILE
    context = factory.Sequence(lambda n: f"Mentioned in context {n}")

    @factory.post_generation
    def created_timestamp(obj, create, extracted, **kwargs):
        """Override the managed creation timestamp when one is given."""
        if create and extracted is not None:
            PersonMention.objects.filter(pk=obj.pk).update(
                created_timestamp=extracted,
            )
            obj.created_timestamp = extracted
