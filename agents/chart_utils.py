#!/usr/bin/env python3
"""
Chart Generation Utility
Extracts chart generation logic from agents for reusability
"""


def generate_chart_data(tool_result: str, operation_detail: str = None) -> dict:
    """Generate chart data from SQL query results if suitable"""
    try:
        # Check if result looks like tabular data
        if not isinstance(tool_result, str) or len(tool_result.strip()) < 10:
            return None

        lines = [line for line in tool_result.strip().split('\n') if line.strip() and "|" in line]
        if len(lines) < 3:  # Need header + separator + at least 1 data row
            return None

        # Look for table-like structure (with | separators)
        if '|' not in lines[0] or '|' not in lines[1]:
            return None

        # Parse header
        header_line = lines[0].strip()
        if not header_line.startswith('|') or not header_line.endswith('|'):
            return None

        headers = [h.strip() for h in header_line.split('|')[1:-1]]

        # Skip separator line and parse data
        data_lines = lines[2:]
        rows = []
        for line in data_lines:
            line = line.strip()
            if line.startswith('|') and line.endswith('|'):
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(row) == len(headers):
                    rows.append(row)

        if len(rows) == 0 or len(headers) < 2:
            return None

        # Check if we have numeric data suitable for charts
        numeric_columns = []
        for i, header in enumerate(headers):
            try:
                # Check if all values in this column are numeric
                values = [float(row[i]) for row in rows if row[i].replace('.', '').replace('-', '').isdigit()]
                if len(values) == len(rows):  # All values are numeric
                    numeric_columns.append(i)
            except:
                continue

        if len(numeric_columns) == 0:
            return None

        # Generate chart based on data structure
        label_column = 0  # First column as labels
        value_column = numeric_columns[0]  # First numeric column as values

        # If first column is also numeric, use it as value and generate sequential labels
        if 0 in numeric_columns and len(numeric_columns) > 1:
            value_column = numeric_columns[1]

        labels = [row[label_column] for row in rows]
        values = [float(row[value_column]) for row in rows]

        # Determine chart type based on data characteristics
        chart_type = 'bar'
        if len(rows) <= 6:  # Small datasets work well as pie charts
            chart_type = 'pie'
        elif any(word in headers[value_column].lower() for word in ['time', 'date', 'year', 'month']):
            chart_type = 'line'

        # Generate Chart.js data structure
        chart_data = {
            'type': chart_type,
            'title': f"{headers[value_column]} by {headers[label_column]}",
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': headers[value_column],
                    'data': values,
                    'backgroundColor': [
                                           '#4F7DF3', '#ff6384', '#36a2eb', '#ffce56',
                                           '#4bc0c0', '#9966ff', '#ff9f40', '#ff6384'
                                       ][:len(values)] if chart_type == 'pie' else '#4F7DF3',
                    'borderColor': '#4F7DF3' if chart_type != 'pie' else None,
                    'borderWidth': 1 if chart_type != 'pie' else 0
                }]
            }
        }

        print(f"Generated {chart_type} chart with {len(labels)} data points")
        return chart_data

    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None
