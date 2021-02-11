from typing import List

WHITE_SPACE = ' '
HARD_LINE = '='
SOFT_LINE = '-'
SEPARATOR = ' | '


class TableBuilder:
    title: str
    rows: List[tuple]

    def __init__(self, headers: tuple):
        self.headers = headers
        self.rows = []

        # columns is used to validate new item inputs
        self.column_count = len(headers)

        # this value is updated each time a row is added
        # it allows us to avoid a full iteration when building table
        self.column_widths = [0] * self.column_count

    def add_row(self, row: tuple) -> None:
        """
        adds the given row to the current table

        :param row: dict object containing the data
        :raises ValueError: this error is thrown when the columns of received rows
                            does not match the number of columns in header
        """
        if len(row) != self.column_count:
            raise ValueError(f"Expected {self.column_count} columns, but 'row' has {len(row)} columns")

        self.rows.append(row)

        # update max length
        for i, column in enumerate(row):
            if len(column) > self.column_widths[i]:
                self.column_widths[i] = len(column)
    
    def _build_row(self, row, should_prefix=True):
        cells = []
        for i, v in enumerate(row):
            cells.append(self._build_column_cells(v, i))

        cells[0] = WHITE_SPACE + cells[0]

        return SEPARATOR.join(cells)

    def _build_column_cells(self, value, column_index):
        return value + WHITE_SPACE * (self.column_widths[column_index] - len(value))

    def __str__(self):
        # format:     [-] column 1   | column 2 | column 3
        table_width = len(WHITE_SPACE) + sum(self.column_widths) + len(SEPARATOR) * self.column_count

        lines = [
            HARD_LINE * table_width,
            self._build_row(self.headers),
            SOFT_LINE * table_width,
        ] + [self._build_row(row) for row in self.rows] + [
            HARD_LINE * table_width,
        ]

        return '\n'.join(lines)

    def __repr__(self):
        return f'{self.__class__.__name__}(title={self.title}, headers={self.headers}, row_count={len(self.rows)})'
