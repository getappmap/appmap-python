"""Common utilities for web framework integration"""

import re
import time

from appmap._implementation.event import (
    describe_value,
    Event,
    ReturnEvent,
)
from appmap._implementation.recording import Recorder
from appmap._implementation.utils import root_relative_path


class TemplateEvent(Event):  # pylint: disable=too-few-public-methods
    """A special call event that records template rendering."""
    __slots__ = ['receiver', 'path']

    def __init__(self, path, instance=None):
        super().__init__('call')
        self.receiver = describe_value(instance)
        self.path = root_relative_path(path)

    def to_dict(self, attrs=None):
        result = super().to_dict(attrs)
        classlike_name = re.sub(r'\W', '', self.path.title())
        result.update({
            'defined_class': f'<templates>.{classlike_name}',
            'method_id': 'render',
            'static': False,
        })
        return result


class TemplateHandler:  # pylint: disable=too-few-public-methods
    """Patch for a template class to capture and record template
    rendering (if recording is enabled).

    This patch can be used with .utils.patch_class to patch any template class
    which has a .render() method. Note it requires a .filename property; if
    there is no such property, this handler can be subclassed first to provide it.
    """
    def render(self, orig, *args, **kwargs):
        """Calls the original implementation.

        If recording is enabled, adds appropriate TemplateEvent
        and ReturnEvent.
        """
        rec = Recorder()
        if rec.enabled:
            start = time.monotonic()
            call_event = TemplateEvent(self.filename, self)  # pylint: disable=no-member
            rec.add_event(call_event)
        try:
            return orig(self, *args, **kwargs)
        finally:
            if rec.enabled:
                rec.add_event(
                    ReturnEvent(call_event.id, time.monotonic() - start)
                )
