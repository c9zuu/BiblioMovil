import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Import our utility modules
from scraper_utils import scrape_website, extract_data_with_selectors
from social_media_scraper import scrape_twitter, scrape_reddit
from data_visualization import create_bar_chart, create_line_chart, create_scatter_plot
from export_utils import export_to_csv, export_to_json

# Set page config for better mobile experience
st.set_page_config(
    page_title="DataHarvest - Developer Scraping Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = "home"
if 'scraping_history' not in st.session_state:
    st.session_state.scraping_history = []

# App title and description
st.title("DataHarvest 🔍")
st.subheader("A Mobile-Friendly Data Scraping Tool for Developers")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Web Scraper", "Social Media Scraper", "Data Visualization", "Export Data", "Scraping History"]
)

# Home page
if page == "Home":
    st.session_state.current_view = "home"
    
    st.markdown("""
    ### Welcome to DataHarvest!
    
    This tool helps developers scrape and visualize data from websites and social media platforms.
    
    #### Key Features:
    - Web scraping with customizable selectors
    - Social media data extraction
    - Basic data visualization
    - Data export in CSV and JSON formats
    - Mobile-friendly interface
    
    Get started by selecting a scraping option from the sidebar!
    """)
    
    # Quick action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Web Scraping", use_container_width=True):
            st.session_state.current_view = "web"
            st.rerun()
    with col2:
        if st.button("Social Media Scraping", use_container_width=True):
            st.session_state.current_view = "social"
            st.rerun()

# Web Scraper Page
elif page == "Web Scraper" or st.session_state.current_view == "web":
    st.session_state.current_view = "web"
    
    st.header("Web Scraper")
    st.markdown("Extract data from any website using URL and CSS selectors")
    
    url = st.text_input("Enter the website URL", "https://example.com")
    
    scrape_method = st.radio(
        "Scraping Method",
        ["Full Page Content", "Custom CSS Selectors", "Table Extraction"]
    )
    
    if scrape_method == "Full Page Content":
        if st.button("Scrape Full Page", use_container_width=True):
            with st.spinner("Scraping data..."):
                try:
                    data = scrape_website(url)
                    st.session_state.scraped_data = {"type": "text", "data": data, "source": url}
                    st.session_state.scraping_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": url,
                        "type": "Web - Full Page",
                        "status": "Success"
                    })
                    st.success("Data scraped successfully!")
                    st.text_area("Scraped Content", data, height=300)
                except Exception as e:
                    st.error(f"Error occurred: {str(e)}")
                    st.session_state.scraping_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": url,
                        "type": "Web - Full Page",
                        "status": f"Failed: {str(e)}"
                    })
    
    elif scrape_method == "Custom CSS Selectors":
        st.subheader("CSS Selectors")
        
        # Expandable info section for CSS selector help
        with st.expander("How to use CSS Selectors"):
            st.markdown("""
            **CSS Selectors** help you target specific elements on a webpage:
            
            - `h1` - Selects all h1 headings
            - `.classname` - Selects elements with class="classname"
            - `#idname` - Selects the element with id="idname"
            - `div.article p` - Selects all paragraphs inside divs with class "article"
            
            You can use browser developer tools (F12) to inspect elements and find their selectors.
            """)
        
        # Dynamic selector fields
        selector_count = st.slider("Number of selectors", 1, 10, 3)
        selectors = {}
        
        for i in range(selector_count):
            col1, col2 = st.columns(2)
            with col1:
                field_name = st.text_input(f"Field name #{i+1}", f"field_{i+1}")
            with col2:
                selector = st.text_input(f"CSS Selector #{i+1}", f"h{i+1}" if i < 6 else "p")
            selectors[field_name] = selector
        
        extract_attributes = st.checkbox("Extract HTML attributes instead of text")
        attribute_name = ""
        if extract_attributes:
            attribute_name = st.text_input("Attribute name (e.g., href, src)", "href")
        
        pagination_selector = ""
        use_pagination = st.checkbox("Enable pagination")
        if use_pagination:
            pagination_selector = st.text_input("Next page button CSS selector", "a.next")
            max_pages = st.slider("Maximum pages to scrape", 1, 20, 3)
        
        if st.button("Scrape with Selectors", use_container_width=True):
            with st.spinner("Scraping data with selectors..."):
                try:
                    pagination_config = {"enabled": use_pagination, "selector": pagination_selector, "max_pages": max_pages} if use_pagination else None
                    data = extract_data_with_selectors(url, selectors, attribute_name if extract_attributes else None, pagination_config)
                    
                    st.session_state.scraped_data = {"type": "structured", "data": data, "source": url}
                    st.session_state.scraping_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": url,
                        "type": "Web - Custom Selectors",
                        "status": "Success"
                    })
                    st.success("Data scraped successfully!")
                    
                    # Convert to DataFrame for display if it's a list of dictionaries
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.json(data)
                except Exception as e:
                    st.error(f"Error occurred: {str(e)}")
                    st.session_state.scraping_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": url,
                        "type": "Web - Custom Selectors",
                        "status": f"Failed: {str(e)}"
                    })
    
    elif scrape_method == "Table Extraction":
        table_number = st.number_input("Table position (0 for first table)", min_value=0, value=0)
        header = st.checkbox("Table has header row", value=True)
        
        if st.button("Extract Table", use_container_width=True):
            with st.spinner("Extracting table data..."):
                try:
                    import pandas as pd
                    tables = pd.read_html(url, header=0 if header else None)
                    
                    if len(tables) > table_number:
                        data = tables[table_number]
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": url}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": url,
                            "type": "Web - Table Extraction",
                            "status": "Success"
                        })
                        st.success(f"Table extracted successfully! Found {len(tables)} tables.")
                        st.dataframe(data)
                    else:
                        st.error(f"Table not found. Only {len(tables)} tables available on the page.")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": url,
                            "type": "Web - Table Extraction",
                            "status": f"Failed: Table not found"
                        })
                except Exception as e:
                    st.error(f"Error occurred: {str(e)}")
                    st.session_state.scraping_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": url,
                        "type": "Web - Table Extraction",
                        "status": f"Failed: {str(e)}"
                    })

# Social Media Scraper Page
elif page == "Social Media Scraper" or st.session_state.current_view == "social":
    st.session_state.current_view = "social"
    
    st.header("Social Media Scraper")
    st.markdown("Extract data from social media platforms")
    
    platform = st.selectbox(
        "Select Platform",
        ["Twitter", "Reddit"]
    )
    
    if platform == "Twitter":
        query_type = st.radio("Search by", ["Username", "Hashtag", "Keyword"])
        
        if query_type == "Username":
            username = st.text_input("Twitter Username (without @)", "twitter")
            num_tweets = st.slider("Number of tweets to scrape", 10, 100, 30)
            
            if st.button("Scrape Twitter User", use_container_width=True):
                with st.spinner(f"Scraping tweets from @{username}..."):
                    try:
                        data = scrape_twitter(f"from:{username}", num_tweets)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Twitter - @{username}"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - @{username}",
                            "type": "Social Media - Twitter User",
                            "status": "Success"
                        })
                        st.success(f"Successfully scraped {len(data)} tweets!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - @{username}",
                            "type": "Social Media - Twitter User",
                            "status": f"Failed: {str(e)}"
                        })
        
        elif query_type == "Hashtag":
            hashtag = st.text_input("Hashtag (without #)", "python")
            num_tweets = st.slider("Number of tweets to scrape", 10, 100, 30)
            
            if st.button("Scrape Twitter Hashtag", use_container_width=True):
                with st.spinner(f"Scraping tweets with #{hashtag}..."):
                    try:
                        data = scrape_twitter(f"#{hashtag}", num_tweets)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Twitter - #{hashtag}"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - #{hashtag}",
                            "type": "Social Media - Twitter Hashtag",
                            "status": "Success"
                        })
                        st.success(f"Successfully scraped {len(data)} tweets!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - #{hashtag}",
                            "type": "Social Media - Twitter Hashtag",
                            "status": f"Failed: {str(e)}"
                        })
        
        elif query_type == "Keyword":
            keyword = st.text_input("Keyword or search term", "data science")
            num_tweets = st.slider("Number of tweets to scrape", 10, 100, 30)
            
            if st.button("Scrape Twitter Keyword", use_container_width=True):
                with st.spinner(f"Scraping tweets with keyword '{keyword}'..."):
                    try:
                        data = scrape_twitter(keyword, num_tweets)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Twitter - '{keyword}'"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - '{keyword}'",
                            "type": "Social Media - Twitter Keyword",
                            "status": "Success"
                        })
                        st.success(f"Successfully scraped {len(data)} tweets!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Twitter - '{keyword}'",
                            "type": "Social Media - Twitter Keyword",
                            "status": f"Failed: {str(e)}"
                        })
    
    elif platform == "Reddit":
        query_type = st.radio("Search by", ["Subreddit", "User", "Search Term"])
        
        if query_type == "Subreddit":
            subreddit = st.text_input("Subreddit name (without r/)", "datascience")
            time_filter = st.selectbox("Time filter", ["day", "week", "month", "year", "all"])
            post_limit = st.slider("Number of posts to scrape", 5, 50, 10)
            
            if st.button("Scrape Subreddit", use_container_width=True):
                with st.spinner(f"Scraping posts from r/{subreddit}..."):
                    try:
                        data = scrape_reddit("subreddit", subreddit, post_limit, time_filter)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Reddit - r/{subreddit}"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - r/{subreddit}",
                            "type": "Social Media - Reddit Subreddit",
                            "status": "Success"
                        })
                        st.success(f"Successfully scraped {len(data)} posts!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - r/{subreddit}",
                            "type": "Social Media - Reddit Subreddit",
                            "status": f"Failed: {str(e)}"
                        })
        
        elif query_type == "User":
            username = st.text_input("Reddit username (without u/)", "spez")
            post_limit = st.slider("Number of posts to scrape", 5, 50, 10)
            
            if st.button("Scrape Reddit User", use_container_width=True):
                with st.spinner(f"Scraping posts from u/{username}..."):
                    try:
                        data = scrape_reddit("user", username, post_limit)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Reddit - u/{username}"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - u/{username}",
                            "type": "Social Media - Reddit User",
                            "status": "Success"
                        })
                        st.success(f"Successfully scraped {len(data)} posts!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - u/{username}",
                            "type": "Social Media - Reddit User",
                            "status": f"Failed: {str(e)}"
                        })
        
        elif query_type == "Search Term":
            search_term = st.text_input("Search term", "data scraping")
            time_filter = st.selectbox("Time filter", ["day", "week", "month", "year", "all"])
            post_limit = st.slider("Number of posts to scrape", 5, 50, 10)
            
            if st.button("Search Reddit", use_container_width=True):
                with st.spinner(f"Searching Reddit for '{search_term}'..."):
                    try:
                        data = scrape_reddit("search", search_term, post_limit, time_filter)
                        st.session_state.scraped_data = {"type": "dataframe", "data": data, "source": f"Reddit - Search: '{search_term}'"}
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - Search: '{search_term}'",
                            "type": "Social Media - Reddit Search",
                            "status": "Success"
                        })
                        st.success(f"Successfully found {len(data)} posts!")
                        st.dataframe(data)
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")
                        st.session_state.scraping_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": f"Reddit - Search: '{search_term}'",
                            "type": "Social Media - Reddit Search",
                            "status": f"Failed: {str(e)}"
                        })

# Data Visualization Page
elif page == "Data Visualization":
    st.header("Data Visualization")
    
    if st.session_state.scraped_data is None:
        st.warning("No data available for visualization. Please scrape some data first.")
    else:
        st.subheader(f"Visualizing data from: {st.session_state.scraped_data['source']}")
        
        # Different visualization options based on data type
        if st.session_state.scraped_data['type'] == "dataframe":
            df = st.session_state.scraped_data['data']
            
            # Show the dataframe
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Column selection for visualization
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if len(numeric_columns) >= 2:
                st.subheader("Create Visualization")
                
                viz_type = st.selectbox(
                    "Visualization Type",
                    ["Bar Chart", "Line Chart", "Scatter Plot"]
                )
                
                if viz_type == "Bar Chart":
                    x_col = st.selectbox("X-axis", df.columns.tolist())
                    y_col = st.selectbox("Y-axis", numeric_columns)
                    
                    # Group by if x is categorical
                    if df[x_col].dtype == 'object' or len(df[x_col].unique()) < 15:
                        agg_func = st.selectbox("Aggregation Function", ["sum", "mean", "count"])
                        chart = create_bar_chart(df, x_col, y_col, agg_func)
                    else:
                        st.warning("Too many unique values for bar chart. Consider using a different column or visualization type.")
                        chart = None
                
                elif viz_type == "Line Chart":
                    x_col = st.selectbox("X-axis", df.columns.tolist())
                    y_col = st.selectbox("Y-axis", numeric_columns)
                    chart = create_line_chart(df, x_col, y_col)
                
                elif viz_type == "Scatter Plot":
                    x_col = st.selectbox("X-axis", numeric_columns)
                    y_col = st.selectbox("Y-axis", [col for col in numeric_columns if col != x_col] if len(numeric_columns) > 1 else numeric_columns)
                    
                    color_col = None
                    if len(df.columns) > 2:
                        use_color = st.checkbox("Add color dimension")
                        if use_color:
                            color_options = ["None"] + df.columns.tolist()
                            color_col = st.selectbox("Color by", color_options)
                            if color_col == "None":
                                color_col = None
                    
                    chart = create_scatter_plot(df, x_col, y_col, color_col)
                
                # Display chart
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("Not enough numeric columns available for visualization. Need at least 2 numeric columns.")
                
                # For text data, offer word cloud or frequency count
                if 'text' in df.columns or any('content' in col.lower() for col in df.columns):
                    text_col = [col for col in df.columns if col == 'text' or 'content' in col.lower()][0]
                    
                    st.subheader("Text Analysis")
                    analysis_type = st.radio("Analysis Type", ["Word Frequency", "Character Count Distribution"])
                    
                    if analysis_type == "Word Frequency":
                        from collections import Counter
                        import re
                        import plotly.express as px
                        
                        # Combine all text
                        all_text = " ".join(df[text_col].astype(str).tolist())
                        # Clean and tokenize
                        words = re.findall(r'\b\w+\b', all_text.lower())
                        # Count
                        word_counts = Counter(words).most_common(20)
                        
                        # Create bar chart
                        word_df = pd.DataFrame(word_counts, columns=['word', 'count'])
                        fig = px.bar(word_df, x='word', y='count', title='Top 20 Words')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif analysis_type == "Character Count Distribution":
                        # Calculate character counts
                        df['char_count'] = df[text_col].astype(str).apply(len)
                        
                        # Create histogram
                        fig = px.histogram(df, x='char_count', title='Character Count Distribution')
                        st.plotly_chart(fig, use_container_width=True)
                
        elif st.session_state.scraped_data['type'] == "text":
            st.subheader("Text Analysis")
            
            text_data = st.session_state.scraped_data['data']
            
            # Text statistics
            st.markdown("#### Text Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Character Count", len(text_data))
            with col2:
                st.metric("Word Count", len(text_data.split()))
            with col3:
                st.metric("Line Count", text_data.count('\n') + 1)
            
            # Word frequency analysis
            st.markdown("#### Word Frequency")
            
            import re
            from collections import Counter
            import plotly.express as px
            
            # Clean and tokenize
            words = re.findall(r'\b\w+\b', text_data.lower())
            # Count
            word_counts = Counter(words).most_common(20)
            
            # Create bar chart
            word_df = pd.DataFrame(word_counts, columns=['word', 'count'])
            fig = px.bar(word_df, x='word', y='count', title='Top 20 Words')
            st.plotly_chart(fig, use_container_width=True)
        
        elif st.session_state.scraped_data['type'] == "structured":
            # Handle structured data (list of dicts)
            data = st.session_state.scraped_data['data']
            
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Convert to dataframe for visualization
                df = pd.DataFrame(data)
                
                # Show the dataframe
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                # Column statistics
                st.subheader("Column Statistics")
                
                numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                if len(numeric_columns) > 0:
                    selected_col = st.selectbox("Select column for statistics", numeric_columns)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Mean", round(df[selected_col].mean(), 2))
                    with col2:
                        st.metric("Min", df[selected_col].min())
                    with col3:
                        st.metric("Max", df[selected_col].max())
                    with col4:
                        st.metric("Count", df[selected_col].count())
                    
                    # Histogram
                    fig = px.histogram(df, x=selected_col, title=f'Distribution of {selected_col}')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric columns available for statistics.")
            else:
                st.json(data)

# Export Data Page
elif page == "Export Data":
    st.header("Export Data")
    
    if st.session_state.scraped_data is None:
        st.warning("No data available for export. Please scrape some data first.")
    else:
        st.subheader(f"Data Source: {st.session_state.scraped_data['source']}")
        
        export_format = st.radio("Export Format", ["CSV", "JSON"])
        
        if export_format == "CSV":
            if st.session_state.scraped_data['type'] in ["dataframe", "structured"]:
                if st.session_state.scraped_data['type'] == "dataframe":
                    data = st.session_state.scraped_data['data']
                else:
                    # Convert structured data to dataframe
                    data = pd.DataFrame(st.session_state.scraped_data['data'])
                
                # Preview data
                st.subheader("Data Preview")
                st.dataframe(data.head())
                
                # Export options
                st.subheader("Export Options")
                filename = st.text_input("Filename (without extension)", "scraped_data")
                include_index = st.checkbox("Include index column")
                
                if st.button("Generate CSV", use_container_width=True):
                    csv_data = export_to_csv(data, include_index)
                    
                    # Create download button
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"{filename}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            elif st.session_state.scraped_data['type'] == "text":
                st.warning("Text data is not suitable for CSV export. Please use JSON format instead.")
        
        elif export_format == "JSON":
            # Convert data based on type
            if st.session_state.scraped_data['type'] == "dataframe":
                data = st.session_state.scraped_data['data'].to_dict(orient="records")
            elif st.session_state.scraped_data['type'] == "structured":
                data = st.session_state.scraped_data['data']
            else:  # text
                data = {"text": st.session_state.scraped_data['data']}
            
            # Preview data
            st.subheader("Data Preview")
            st.json(data if not isinstance(data, list) or len(data) <= 5 else data[:5])
            
            # Export options
            st.subheader("Export Options")
            filename = st.text_input("Filename (without extension)", "scraped_data")
            pretty_print = st.checkbox("Pretty print (formatted JSON)", value=True)
            
            if st.button("Generate JSON", use_container_width=True):
                json_data = export_to_json(data, pretty_print)
                
                # Create download button
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"{filename}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Scraping History Page
elif page == "Scraping History":
    st.header("Scraping History")
    
    if not st.session_state.scraping_history:
        st.info("No scraping history available. Start scraping data to see your history.")
    else:
        # Display history as a table
        history_df = pd.DataFrame(st.session_state.scraping_history)
        st.dataframe(history_df, use_container_width=True)
        
        # Option to clear history
        if st.button("Clear History", use_container_width=True):
            st.session_state.scraping_history = []
            st.success("History cleared!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; opacity: 0.7;">
        DataHarvest © 2023 | A mobile-friendly data scraping tool for developers
    </div>
    """,
    unsafe_allow_html=True
)
