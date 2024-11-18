from textual.containers import Container
from textual.widgets import Static
from textual.css.query import NoMatches
from textual.message import Message
from textual import events
from textual.geometry import Offset

class DragHandle(Static):
    """A draggable handle for resizing."""
    
    DEFAULT_CSS = """
    DragHandle {
        width: 1;
        background: $foreground-darken-2;
        cursor: col-resize;
    }
    DragHandle:hover {
        background: $accent;
    }
    """

class SplitView(Container):
    """A container that splits into two resizable panes."""

    DEFAULT_CSS = """
    SplitView {
        layout: horizontal;
        height: 100%;
        overflow: hidden;
    }
    """

    def __init__(self, left_pane, right_pane, left_size: float = 0.5):
        """Initialize with two panes and initial split ratio."""
        super().__init__()
        self.left_pane = left_pane
        self.right_pane = right_pane
        self.left_size = left_size
        self.dragging = False
        
    def compose(self):
        """Create the split view."""
        yield self.left_pane
        yield DragHandle()
        yield self.right_pane

    def on_mount(self):
        """Handle initial layout."""
        self._update_sizes()

    def _update_sizes(self) -> None:
        """Update pane sizes based on split position."""
        try:
            left = self.query_one(f"#{self.left_pane.id}")
            right = self.query_one(f"#{self.right_pane.id}")
            left.styles.width = f"{self.left_size * 100}%"
            right.styles.width = f"{(1 - self.left_size) * 100}%"
        except NoMatches:
            pass

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle start of drag."""
        if isinstance(event.target, DragHandle):
            self.dragging = True
            self.capture_mouse()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle end of drag."""
        if self.dragging:
            self.dragging = False
            self.release_mouse()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse dragging to resize panes."""
        if self.dragging:
            total_width = float(self.size.width)
            if total_width > 0:
                new_left_size = event.screen_x / total_width
                # Limit the minimum size of each pane
                new_left_size = min(max(0.1, new_left_size), 0.9)
                self.left_size = new_left_size
                self._update_sizes()
