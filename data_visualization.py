import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_bar_chart(data, x_column, y_column, agg_func='sum'):
    """
    Create a bar chart using Plotly Express.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to visualize
    x_column : str
        Column name for x-axis
    y_column : str
        Column name for y-axis
    agg_func : str, optional
        Aggregation function for y values ('sum', 'mean', 'count', etc.)
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    try:
        # Group by if necessary
        if data[x_column].dtype == 'object' or len(data[x_column].unique()) < len(data):
            if agg_func == 'sum':
                grouped_data = data.groupby(x_column)[y_column].sum().reset_index()
            elif agg_func == 'mean':
                grouped_data = data.groupby(x_column)[y_column].mean().reset_index()
            elif agg_func == 'count':
                grouped_data = data.groupby(x_column)[y_column].count().reset_index()
            else:
                # Default to sum
                grouped_data = data.groupby(x_column)[y_column].sum().reset_index()
        else:
            grouped_data = data
        
        # Create bar chart
        fig = px.bar(
            grouped_data, 
            x=x_column, 
            y=y_column,
            title=f"{y_column} by {x_column} ({agg_func})",
            labels={x_column: x_column.replace('_', ' ').title(), y_column: y_column.replace('_', ' ').title()},
            text_auto='.2s',
            height=500
        )
        
        # Update layout for better visualization
        fig.update_layout(
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis={'categoryorder':'total descending'} if agg_func == 'sum' else None
        )
        
        # Ensure x-axis is not too crowded
        if len(grouped_data[x_column].unique()) > 10:
            fig.update_layout(
                xaxis=dict(
                    tickmode='auto',
                    nticks=10,
                    tickangle=45
                )
            )
        
        return fig
    except Exception as e:
        print(f"Error creating bar chart: {str(e)}")
        return None

def create_line_chart(data, x_column, y_column):
    """
    Create a line chart using Plotly Express.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to visualize
    x_column : str
        Column name for x-axis
    y_column : str
        Column name for y-axis
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    try:
        # Sort data by x column if it's a date or number
        if pd.api.types.is_numeric_dtype(data[x_column]) or pd.api.types.is_datetime64_any_dtype(data[x_column]):
            data = data.sort_values(by=x_column)
        
        # Create line chart
        fig = px.line(
            data,
            x=x_column,
            y=y_column,
            title=f"{y_column} over {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(), y_column: y_column.replace('_', ' ').title()},
            height=500
        )
        
        # Add markers to the line
        fig.update_traces(mode='lines+markers')
        
        # Update layout for better visualization
        fig.update_layout(
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Format x-axis if it's a date
        if pd.api.types.is_datetime64_any_dtype(data[x_column]):
            fig.update_xaxes(
                tickformat="%Y-%m-%d",
                tickangle=45
            )
        
        return fig
    except Exception as e:
        print(f"Error creating line chart: {str(e)}")
        return None

def create_scatter_plot(data, x_column, y_column, color_column=None):
    """
    Create a scatter plot using Plotly Express.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to visualize
    x_column : str
        Column name for x-axis
    y_column : str
        Column name for y-axis
    color_column : str, optional
        Column name for color coding points
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    try:
        # Create scatter plot
        fig = px.scatter(
            data,
            x=x_column,
            y=y_column,
            color=color_column,
            title=f"{y_column} vs {x_column}" + (f" by {color_column}" if color_column else ""),
            labels={
                x_column: x_column.replace('_', ' ').title(), 
                y_column: y_column.replace('_', ' ').title(),
                color_column: color_column.replace('_', ' ').title() if color_column else None
            },
            height=500
        )
        
        # Update layout for better visualization
        fig.update_layout(
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Add trendline
        if not color_column and data[x_column].nunique() > 5 and data[y_column].nunique() > 5:
            fig.update_layout(
                shapes=[dict(
                    type='line',
                    xref='x',
                    yref='y',
                    x0=data[x_column].min(),
                    y0=np.polyval(np.polyfit(data[x_column], data[y_column], 1), data[x_column].min()),
                    x1=data[x_column].max(),
                    y1=np.polyval(np.polyfit(data[x_column], data[y_column], 1), data[x_column].max()),
                    line=dict(
                        color='red',
                        width=2,
                        dash='dash',
                    )
                )]
            )
        
        return fig
    except Exception as e:
        print(f"Error creating scatter plot: {str(e)}")
        return None

def create_histogram(data, column):
    """
    Create a histogram using Plotly Express.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to visualize
    column : str
        Column name for histogram
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    try:
        # Create histogram
        fig = px.histogram(
            data,
            x=column,
            title=f"Distribution of {column}",
            labels={column: column.replace('_', ' ').title()},
            height=500
        )
        
        # Update layout for better visualization
        fig.update_layout(
            xaxis_title=column.replace('_', ' ').title(),
            yaxis_title="Count",
            margin=dict(l=40, r=40, t=50, b=40),
            bargap=0.1
        )
        
        return fig
    except Exception as e:
        print(f"Error creating histogram: {str(e)}")
        return None

def create_pie_chart(data, column):
    """
    Create a pie chart using Plotly Express.
    
    Parameters:
    ----------
    data : pandas.DataFrame
        Data to visualize
    column : str
        Column name for pie chart
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    try:
        # Count values in the column
        value_counts = data[column].value_counts().reset_index()
        value_counts.columns = ['value', 'count']
        
        # Create pie chart
        fig = px.pie(
            value_counts,
            values='count',
            names='value',
            title=f"Distribution of {column}",
            labels={'value': column.replace('_', ' ').title(), 'count': 'Count'},
            height=500
        )
        
        # Update layout for better visualization
        fig.update_layout(
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # If there are too many categories, limit to top N
        if len(value_counts) > 10:
            top_n = value_counts.nlargest(10, 'count')
            other_count = value_counts[~value_counts['value'].isin(top_n['value'])]['count'].sum()
            
            top_n = pd.concat([
                top_n,
                pd.DataFrame([{'value': 'Other', 'count': other_count}])
            ])
            
            fig = px.pie(
                top_n,
                values='count',
                names='value',
                title=f"Distribution of {column} (Top 10 + Other)",
                labels={'value': column.replace('_', ' ').title(), 'count': 'Count'},
                height=500
            )
        
        return fig
    except Exception as e:
        print(f"Error creating pie chart: {str(e)}")
        return None
