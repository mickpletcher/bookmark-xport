from __future__ import annotations

from datetime import UTC, datetime

import pytest

from bookmark_exporter.exporters.html_exporter import render
from bookmark_exporter.models import Bookmark, BookmarkFolder


def _tree() -> BookmarkFolder:
    nested = BookmarkFolder(
        name="Tools",
        children=[Bookmark(title="Nested & <b>", url="https://example.org/x?a=1&b=2")],
    )
    return BookmarkFolder(
        name="Development",
        children=[
            nested,
            BookmarkFolder(name="Empty"),
            Bookmark(title="Docs", url="https://example.com/docs"),
        ],
    )


def test_starts_with_the_netscape_doctype() -> None:
    assert render(_tree()).startswith("<!DOCTYPE NETSCAPE-Bookmark-file-1>")


def test_selected_folder_becomes_the_top_level_heading() -> None:
    html = render(_tree())
    assert "<DT><H3>Development</H3>" in html


def test_nesting_is_preserved() -> None:
    html = render(_tree())
    development = html.index("<H3>Development</H3>")
    tools = html.index("<H3>Tools</H3>")
    nested = html.index("Nested &amp; &lt;b&gt;")
    assert development < tools < nested


def test_escapes_titles_and_urls() -> None:
    folder = BookmarkFolder(
        name='Quotes " and <tags>',
        children=[
            Bookmark(title="<script>alert(1)</script>", url='https://example.com/"onload="x')
        ],
    )
    html = render(folder)

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Quotes &quot; and &lt;tags&gt;" in html
    assert '"https://example.com/&quot;onload=&quot;x"' in html


def test_unicode_survives() -> None:
    folder = BookmarkFolder(
        name="Café", children=[Bookmark(title="ünïcode ✓", url="https://example.org/✓")]
    )
    html = render(folder)
    assert "Café" in html
    assert "ünïcode ✓" in html


def test_empty_folder_produces_an_empty_list() -> None:
    html = render(BookmarkFolder(name="Empty"))
    assert "<H3>Empty</H3>" in html
    assert html.count("<DT><A") == 0


def test_output_is_deterministic() -> None:
    assert render(_tree()) == render(_tree())


def test_add_date_is_emitted_when_known() -> None:
    folder = BookmarkFolder(
        name="Dated",
        children=[
            Bookmark(
                title="Docs",
                url="https://example.com",
                added=datetime(2022, 1, 1, tzinfo=UTC),
            )
        ],
    )
    assert 'ADD_DATE="1640995200"' in render(folder)


def test_siblings_and_parents_are_excluded() -> None:
    child = BookmarkFolder(name="Child", children=[Bookmark(title="Keep", url="https://a.test")])
    sibling = BookmarkFolder(
        name="Sibling", children=[Bookmark(title="Drop", url="https://b.test")]
    )
    BookmarkFolder(name="Parent", children=[child, sibling])

    html = render(child)
    assert "Keep" in html
    assert "Drop" not in html
    assert "Parent" not in html


@pytest.mark.parametrize("url", ["", "javascript:alert(1)", "not a url", "https://a.test/#<>"])
def test_unusual_urls_do_not_break_rendering(url: str) -> None:
    html = render(BookmarkFolder(name="Odd", children=[Bookmark(title="t", url=url)]))
    assert "<DT><A HREF=" in html
    assert "<>" not in html


def test_preserves_mixed_bookmark_and_folder_order() -> None:
    folder = BookmarkFolder(
        name="Ordered",
        children=[
            Bookmark("First", "https://first.test"),
            BookmarkFolder(name="Middle"),
            Bookmark("Last", "https://last.test"),
        ],
    )

    html = render(folder)
    assert html.index(">First</A>") < html.index(">Middle</H3>") < html.index(">Last</A>")
