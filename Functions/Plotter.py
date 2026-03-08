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
        # Return a PNG data-URI pie chart of subject time distribution, or None.
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

    ## BytesIO stream API (for DOCX)
    def build_pie_stream(self, subjects: list[dict]) -> io.BytesIO | None:
        # Return a PNG BytesIO stream for the pie chart, or None.
        fig = self._make_pie_fig(subjects)
        if fig is None:
            return None
        buf = self._fig_to_bytesio(fig)
        plt.close(fig)
        return buf

    def build_bar_stream(self, subjects: list[dict]) -> io.BytesIO | None:
        """Return a PNG BytesIO stream for the bar chart, or None."""
        fig = self._make_bar_fig(subjects)
        if fig is None:
            return None
        buf = self._fig_to_bytesio(fig)
        plt.close(fig)
        return buf

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
    _BASE_SIZE  = 6.0       # base figure dimension in inches
    _FONT_SIZE  = 11        # base font size used everywhere
    _PALETTE    = 'Set2'    # named palette for colours

    def _pie_figsize(self, n: int) -> tuple[float, float]:
        """Grow the pie canvas by 0.6" per slice beyond 4, capped at 12"."""
        side = min(self._BASE_SIZE + max(0, n - 4) * 0.6, 12.0)
        return (side, side)

    def _bar_figsize(self, n: int) -> tuple[float, float]:
        """Grow the bar canvas by 0.9" per type beyond 3, capped at 14"."""
        w = min(self._BASE_SIZE + max(0, n - 3) * 0.9, 14.0)
        return (w, self._BASE_SIZE - 1)

    def _palette_colours(self, n: int) -> list:
        """Wrap around the palette so we never run out of colours."""
        base = list(plt.get_cmap(self._PALETTE).colors)
        return [base[i % len(base)] for i in range(n)]

    ## Figure builders
    def _make_pie_fig(self, subjects: list[dict]):
        rows = [
            (s.get('title') or 'Untitled', s.get('elapsed_seconds', 0))
            for s in subjects if s.get('elapsed_seconds', 0) > 0
        ]
        if not rows:
            return None

        n = len(rows)
        labels  = [r[0] for r in rows]
        values  = [r[1] for r in rows]
        colours = self._palette_colours(n)
        use_legend = n > 5

        fig, ax = plt.subplots(figsize=self._pie_figsize(n))
        ax.pie(
            values,
            labels=None if use_legend else labels,
            colors=colours,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': self._FONT_SIZE},
        )
        ax.axis('equal')
        ax.set_title('Time Distribution by Subject', fontsize=self._FONT_SIZE + 1, fontweight='bold')
        if use_legend:
            ax.legend(
                labels, loc='lower center',
                bbox_to_anchor=(0.5, -0.08),
                ncol=min(3, (n + 1) // 2),
                fontsize=self._FONT_SIZE - 1,
            )
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

        types   = list(type_minutes.keys())
        minutes = [type_minutes[t] for t in types]
        colours = self._palette_colours(len(types))

        fig, ax = plt.subplots(figsize=self._bar_figsize(len(types)))
        sns.barplot(x=types, y=minutes, ax=ax, hue=types, palette=colours, legend=False)
        ax.set_title('Time by Session Type', fontsize=self._FONT_SIZE + 1, fontweight='bold')
        ax.set_xlabel('Session Type', fontsize=self._FONT_SIZE)
        ax.set_ylabel('Time (minutes)', fontsize=self._FONT_SIZE)
        ax.tick_params(labelsize=self._FONT_SIZE)
        fig.tight_layout()
        return fig

    ## Internal utilities
    @staticmethod
    def _fig_to_bytesio(fig) -> io.BytesIO:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        buf.seek(0)
        return buf

    @staticmethod
    def _fig_to_data_uri(fig) -> str:
        buf = Plotter._fig_to_bytesio(fig)
        b64 = base64.b64encode(buf.read()).decode('ascii')
        return f"data:image/png;base64,{b64}"
