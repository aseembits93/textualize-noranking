from typing import Callable

from textual.expand_tabs import get_tab_widths

__all__ = ["cell_len", "cell_width_to_column_index"]


cell_len: Callable[[str], int]
try:
    from rich.cells import cached_cell_len as cell_len
except ImportError:
    from rich.cells import cell_len


def cell_width_to_column_index(line: str, cell_width: int, tab_width: int) -> int:
    """Retrieve the column index corresponding to the given cell width.

    Args:
        line: The line of text to search within.
        cell_width: The cell width to convert to column index.
        tab_width: The tab stop width to expand tabs contained within the line.

    Returns:
        The column corresponding to the cell width.
    """
    column_index = 0
    total_cell_offset = 0
    # Avoid per-character iteration by working with part substrings at once
    for part, expanded_tab_width in get_tab_widths(line, tab_width):
        part_len = len(part)
        if part_len == 0:
            # No characters before tab, only add expanded tab width
            total_cell_offset += expanded_tab_width
            if total_cell_offset > cell_width:
                return column_index
            column_index += 1
            continue
        # Fast path: try to process runs of single cell width chars at once
        # However, 'cell_len' can be >1, so we must check.
        # Pre-calculate cell widths for part as a whole (if possible)
        # Pypy could optimize this with __getitem__ views, but for CPython this is fastest:
        part_cell_width = cell_len(part)
        # If the whole part fits before cell_width, skip over all chars in one go
        if total_cell_offset + part_cell_width <= cell_width:
            total_cell_offset += part_cell_width
            column_index += part_len
        else:
            # Otherwise, must walk char by char to find the boundary
            for character in part:
                c_width = cell_len(character)
                total_cell_offset += c_width
                if total_cell_offset > cell_width:
                    return column_index
                column_index += 1

        # Account for the appearance of the tab character for this part
        total_cell_offset += expanded_tab_width
        if total_cell_offset > cell_width:
            return column_index

        column_index += 1

    return len(line)
