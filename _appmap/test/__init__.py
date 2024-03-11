import pytest

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite("_appmap.test.web_framework")
