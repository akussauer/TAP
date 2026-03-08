import io
import base64
from collections import defaultdict

import matplotlib
matplotlib.use('Agg') # non-interactive backend — must come before pyplot
import matplotlib.pyplot as plt
import seaborn as sns

class Plotter:
    # Generates pie and bar charts for lesson breakdown sections.
    def __init__(self, file_func=None):
        self.file_func = file_func

    ## Base64 data-URI API (for HTML / PDF)
    def build_pie_uri(self, subjects: list[dict]) -> str | None:
        """Return a PNG data-URI pie chart of subject time distribution, or None."""
        fig = self._make_pie_fig(subjects)
        if fig is None:
            return None
        uri = self._fig_to_data_uri(fig)
        plt.close(fig)
        return uri

    def build_bar_uri(self, subjects: list[dict]) -> str | None:
        # Return a PNG data-URI bar chart of minutes per session type, or None.
        fig = self._make_bar_fig(subjects)
        if fig is None:
            return None
        uri = self._fig_to_data_uri(fig)
        plt.close(fig)
        return uri

    ## File-save API (for Markdown)

    def save_pie(self, subjects: list[dict], path: str) -> bool:
        # Save pie chart to *path*. Returns True on success.
        fig = self._make_pie_fig(subjects)
        if fig is None:
            return False
        fig.savefig(path, dpi=120, bbox_inches='tight')
        plt.close(fig)
        return True

    def save_bar(self, subjects: list[dict], path: str) -> bool:
        # Save bar chart to *path*. Returns True on success.
        fig = self._make_bar_fig(subjects)
        if fig is None:
            return False
        fig.savefig(path, dpi=120, bbox_inches='tight')
        plt.close(fig)
        return True

    # Shared style constants
    _FIG_SIZE   = (6, 5)        # identical canvas size for both charts
    _FONT_SIZE  = 11            # base font size used everywhere
    _PALETTE    = 'Set2'       # named palette for bar colours

    ## Figure builders
    def _make_pie_fig(self, subjects: list[dict]):
        rows = [
            (s.get('title') or 'Untitled', s.get('elapsed_seconds', 0))
            for s in subjects if s.get('elapsed_seconds', 0) > 0
        ]
        if not rows:
            return None

        labels = [r[0] for r in rows]
        values = [r[1] for r in rows]
        colours = plt.get_cmap(self._PALETTE).colors[:len(rows)]

        fig, ax = plt.subplots(figsize=self._FIG_SIZE)
        ax.pie(
            values, labels=labels, colors=colours,
            autopct='%1.1f%%', startangle=140,
            textprops={'fontsize': self._FONT_SIZE},
        )
        ax.axis('equal')
        ax.set_title('Time Distribution by Subject', fontsize=self._FONT_SIZE + 1, fontweight='bold')
        fig.tight_layout()
        return fig

    def _make_bar_fig(self, subjects: list[dict]):
        type_minutes: dict[str, float] = defaultdict(float)
        for s in subjects:
            stype = s.get('session_type') or 'Unknown'
            type_minutes[stype] += s.get('elapsed_seconds', 0) / 60.0
        type_minutes = {k: v for k, v in type_minutes.items() if v > 0}
        if not type_minutes:
            return None

        types = list(type_minutes.keys())
        minutes = [type_minutes[t] for t in types]
        colours = plt.get_cmap(self._PALETTE).colors[:len(types)]

        fig, ax = plt.subplots(figsize=self._FIG_SIZE)
        sns.barplot(x=types, y=minutes, ax=ax, hue=types, palette=colours)
        ax.set_title('Time by Session Type', fontsize=self._FONT_SIZE + 1, fontweight='bold')
        ax.set_xlabel('Session Type', fontsize=self._FONT_SIZE)
        ax.set_ylabel('Time (minutes)', fontsize=self._FONT_SIZE)
        ax.tick_params(labelsize=self._FONT_SIZE)
        fig.tight_layout()
        return fig

    ## Internal utilities
    @staticmethod
    def _fig_to_data_uri(fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode('ascii')
        return f"data:image/png;base64,{b64}"
