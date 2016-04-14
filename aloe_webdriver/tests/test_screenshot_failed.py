"""
Test saving screenshots after failed steps.
"""

import re
import os
from glob import iglob

from aloe.registry import CALLBACK_REGISTRY, PriorityClass
from aloe.testing import FeatureTest, in_directory


@in_directory('tests')
class TestScreenshots(FeatureTest):
    """Test saving screenshots after failed steps."""

    def cleanup_screenshots(self):
        """Clean up any screenshots taken."""

        for ext in ('png', 'html'):
            for filename in iglob('failed_*.{}'.format(ext)):
                os.unlink(filename)

    def setUp(self):
        """Register the failed screenshot steps."""

        self.cleanup_screenshots()

        import aloe_webdriver.screenshot_failed

    def tearDown(self):
        """Remove all the registered hooks."""

        CALLBACK_REGISTRY.clear(priority_class=PriorityClass.USER)

        self.cleanup_screenshots()

    def file_name(self,
                  extension,
                  feature,
                  scenario_index=None,
                  scenario=None):
        """
        The name of the file that ought to be created when a scenario fails.

        :param extension: File extension, such as 'html' or 'png'
        :param feature: Feature file name that the scenario belongs to
        :param scenario_index: 1-based index of the scenario
        :param scenario: Scenario name; if not given, assume background
        """

        return \
            'failed_{feature}_{scenario_index}_{scenario}.{extension}'.format(
                feature=re.sub(r'\W', '_', feature),
                scenario_index=scenario_index if scenario else 0,
                scenario=scenario or "Background",
                extension=extension,
            )

    def test_failed_screenshots(self):
        """Test that failed tests screenshots and page source are recorded."""

        feature_string = """
Feature: Test screenshots on failed steps

Scenario: This scenario succeeds
    When I visit test page "basic_page"
    Then I should see "Hello there"

Scenario: This scenario fails
    When I visit test page "basic_page"
    Then I should see "A unicorn"
"""

        result = self.run_feature_string(feature_string)

        # Feature will be put in a temporary file, find out its name as it will
        # be used as the base of the screenshot names
        feature = os.path.relpath(result.tests_run[0])

        assert not os.path.exists(
            self.file_name('.png', feature, 1, "This scenario succeeds")), \
            "Successful scenario should not be screenshotted."
        assert not os.path.exists(
            self.file_name('.html', feature, 1, "This scenario succeeds")), \
            "Successful scenario page source should not be saved."

        assert os.path.exists(
            self.file_name('.png', feature, 2, "This scenario fails")), \
            "Failed scenario should be screenshotted."
        assert os.path.exists(
            self.file_name('.html', feature, 2, "This scenario fails")), \
            "Failed scenario page source should be saved."
