from sahara.plugins.cdh.v5 import validation
from sahara.tests.unit.plugins.cdh import base_validation_tests as bvt


class ValidationTestCase(bvt.BaseValidationTestCase):
    def setUp(self):
        super(ValidationTestCase, self).setUp()
        self.module = validation
