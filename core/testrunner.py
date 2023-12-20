from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.runner import DiscoverRunner


class CustomTestRunner(DiscoverRunner):
    def __init__(self, **kwargs):
        kwargs["pattern"] = "test_*.py"
        super(CustomTestRunner, self).__init__(**kwargs)

    def setup_test_environment(self, **kwargs):
        if not settings.TEST:
            raise ImproperlyConfigured("Environment variable TEST is not set to value '1'")
        super().setup_test_environment(**kwargs)
