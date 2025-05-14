import pandas as pd
import json
import io

def export_to_csv(data, include_index=False):
    """
    Export data to CSV format.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to export
    include_index : bool, optional
        Whether to include the index column in the export
        
    Returns:
    -------
    str
        CSV data as string
    """
    try:
        # Create an in-memory buffer
        buffer = io.StringIO()
        
        # Write DataFrame to CSV
        data.to_csv(buffer, index=include_index)
        
        # Get the CSV content as a string
        csv_data = buffer.getvalue()
        
        return csv_data
    except Exception as e:
        raise Exception(f"Failed to export to CSV: {str(e)}")

def export_to_json(data, pretty_print=True):
    """
    Export data to JSON format.
    
    Parameters:
    ----------
    data : dict, list, or pandas.DataFrame
        Data to export
    pretty_print : bool, optional
        Whether to format the JSON with indentation for readability
        
    Returns:
    -------
    str
        JSON data as string
    """
    try:
        # Convert DataFrame to dictionary if needed
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        
        # Convert to JSON string
        if pretty_print:
            json_data = json.dumps(data, indent=4, default=str)
        else:
            json_data = json.dumps(data, default=str)
        
        return json_data
    except Exception as e:
        raise Exception(f"Failed to export to JSON: {str(e)}")

def convert_dataframe_to_html_table(data, max_rows=None):
    """
    Convert DataFrame to an HTML table.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to convert
    max_rows : int, optional
        Maximum number of rows to include in the table
        
    Returns:
    -------
    str
        HTML table as string
    """
    try:
        # Limit rows if specified
        if max_rows is not None and len(data) > max_rows:
            limited_data = data.head(max_rows)
        else:
            limited_data = data
        
        # Convert to HTML
        html_table = limited_data.to_html(classes=["dataframe", "table", "table-striped", "table-hover"], index=False)
        
        return html_table
    except Exception as e:
        raise Exception(f"Failed to convert DataFrame to HTML table: {str(e)}")
