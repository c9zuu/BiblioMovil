import pandas as pd
import datetime
import os
import re
import tempfile
import subprocess

def scrape_twitter(query, limit=100):
    """
    Scrape tweets using SNScrape.
    
    Parameters:
    ----------
    query : str
        Twitter search query
    limit : int, optional
        Maximum number of tweets to scrape
        
    Returns:
    -------
    pandas.DataFrame
        DataFrame containing tweet data
    """
    try:
        import snscrape.modules.twitter as sntwitter
        
        # List to store tweet data
        tweets_list = []
        
        # Using SNScrape to get tweets
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
                
            tweets_list.append({
                'date': tweet.date,
                'id': tweet.id,
                'content': tweet.rawContent,
                'user': tweet.user.username,
                'retweet_count': tweet.retweetCount,
                'like_count': tweet.likeCount,
                'reply_count': tweet.replyCount,
                'language': tweet.lang,
                'source': tweet.sourceLabel if hasattr(tweet, 'sourceLabel') else '',
                'url': tweet.url
            })
        
        # Create DataFrame
        tweets_df = pd.DataFrame(tweets_list)
        return tweets_df
        
    except ImportError:
        # Fallback to using snscrape via subprocess if the Python module is not available
        return _scrape_twitter_subprocess(query, limit)

def _scrape_twitter_subprocess(query, limit=100):
    """
    Fallback function to scrape tweets using snscrape via subprocess.
    
    Parameters:
    ----------
    query : str
        Twitter search query
    limit : int, optional
        Maximum number of tweets to scrape
        
    Returns:
    -------
    pandas.DataFrame
        DataFrame containing tweet data
    """
    # Ensure the query is properly quoted for the command line
    escaped_query = query.replace('"', '\\"')
    
    # Create a temporary file to store the JSON output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
        tmp_filename = tmp_file.name
    
    try:
        # Run snscrape command to get tweets
        command = f'snscrape --jsonl --max-results {limit} twitter-search "{escaped_query}" > {tmp_filename}'
        subprocess.run(command, shell=True, check=True)
        
        # Read the JSON file into a DataFrame
        tweets_df = pd.read_json(tmp_filename, lines=True)
        
        # Clean up the columns to match the Python module output
        if not tweets_df.empty:
            tweets_df = tweets_df.rename(columns={
                'date': 'date',
                'id': 'id',
                'content': 'content',
                'username': 'user',
                'retweetCount': 'retweet_count',
                'likeCount': 'like_count',
                'replyCount': 'reply_count',
                'lang': 'language',
                'sourceLabel': 'source',
                'url': 'url'
            })
            
            # Extract username from user object if needed
            if 'user' in tweets_df.columns and isinstance(tweets_df['user'].iloc[0], dict):
                tweets_df['user'] = tweets_df['user'].apply(lambda x: x.get('username', ''))
        
        return tweets_df
    
    except Exception as e:
        raise Exception(f"Failed to scrape Twitter data: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

def scrape_reddit(scrape_type, query, limit=10, time_filter="all"):
    """
    Scrape Reddit data using PRAW or PSAW.
    
    Parameters:
    ----------
    scrape_type : str
        Type of scraping: 'subreddit', 'user', or 'search'
    query : str
        Subreddit name, username, or search query
    limit : int, optional
        Maximum number of posts to scrape
    time_filter : str, optional
        Time filter for results: 'day', 'week', 'month', 'year', 'all'
        
    Returns:
    -------
    pandas.DataFrame
        DataFrame containing Reddit post data
    """
    try:
        # First try to use PRAW if available
        try:
            import praw
            return _scrape_reddit_praw(scrape_type, query, limit, time_filter)
        except ImportError:
            # Fall back to using snscrape via subprocess
            return _scrape_reddit_subprocess(scrape_type, query, limit, time_filter)
    
    except Exception as e:
        raise Exception(f"Failed to scrape Reddit data: {str(e)}")

def _scrape_reddit_praw(scrape_type, query, limit=10, time_filter="all"):
    """
    Scrape Reddit data using PRAW.
    
    Parameters:
    ----------
    scrape_type : str
        Type of scraping: 'subreddit', 'user', or 'search'
    query : str
        Subreddit name, username, or search query
    limit : int, optional
        Maximum number of posts to scrape
    time_filter : str, optional
        Time filter for results: 'day', 'week', 'month', 'year', 'all'
        
    Returns:
    -------
    pandas.DataFrame
        DataFrame containing Reddit post data
    """
    import praw
    
    # Initialize Reddit API client
    # Try to get credentials from environment variables, use anonymous browsing if not available
    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    user_agent = os.getenv("REDDIT_USER_AGENT", "DataHarvest:v1.0 (by /u/DataHarvestApp)")
    
    if client_id and client_secret:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    else:
        # Use read-only mode if no credentials are provided
        reddit = praw.Reddit(
            client_id="dummy",
            client_secret="dummy",
            user_agent=user_agent,
            check_for_updates=False,
            comment_kind="t1",
            message_kind="t4",
            redditor_kind="t2",
            submission_kind="t3",
            subreddit_kind="t5",
            trophy_kind="t6",
            oauth_url="https://oauth.reddit.com",
            reddit_url="https://www.reddit.com",
            short_url="https://redd.it",
            ratelimit_seconds=5,
            timeout=16
        )
    
    # List to store post data
    posts_list = []
    
    # Scrape data based on type
    if scrape_type == "subreddit":
        # Get posts from a subreddit
        subreddit = reddit.subreddit(query)
        
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            posts_list.append({
                'id': post.id,
                'title': post.title,
                'score': post.score,
                'author': str(post.author),
                'created_utc': datetime.datetime.fromtimestamp(post.created_utc),
                'num_comments': post.num_comments,
                'url': post.url,
                'selftext': post.selftext,
                'subreddit': post.subreddit.display_name,
                'permalink': f"https://www.reddit.com{post.permalink}"
            })
    
    elif scrape_type == "user":
        # Get posts from a user
        user = reddit.redditor(query)
        
        for post in user.submissions.new(limit=limit):
            posts_list.append({
                'id': post.id,
                'title': post.title,
                'score': post.score,
                'author': str(post.author),
                'created_utc': datetime.datetime.fromtimestamp(post.created_utc),
                'num_comments': post.num_comments,
                'url': post.url,
                'selftext': post.selftext,
                'subreddit': post.subreddit.display_name,
                'permalink': f"https://www.reddit.com{post.permalink}"
            })
    
    elif scrape_type == "search":
        # Search for posts
        for post in reddit.subreddit("all").search(query, time_filter=time_filter, limit=limit):
            posts_list.append({
                'id': post.id,
                'title': post.title,
                'score': post.score,
                'author': str(post.author),
                'created_utc': datetime.datetime.fromtimestamp(post.created_utc),
                'num_comments': post.num_comments,
                'url': post.url,
                'selftext': post.selftext,
                'subreddit': post.subreddit.display_name,
                'permalink': f"https://www.reddit.com{post.permalink}"
            })
    
    # Create DataFrame
    posts_df = pd.DataFrame(posts_list)
    return posts_df

def _scrape_reddit_subprocess(scrape_type, query, limit=10, time_filter="all"):
    """
    Fallback function to scrape Reddit using snscrape via subprocess.
    
    Parameters:
    ----------
    scrape_type : str
        Type of scraping: 'subreddit', 'user', or 'search'
    query : str
        Subreddit name, username, or search query
    limit : int, optional
        Maximum number of posts to scrape
    time_filter : str, optional
        Time filter for results: 'day', 'week', 'month', 'year', 'all'
        
    Returns:
    -------
    pandas.DataFrame
        DataFrame containing Reddit post data
    """
    # Create a command based on the scrape type
    if scrape_type == "subreddit":
        snscrape_query = f"reddit-subreddit {query}"
    elif scrape_type == "user":
        snscrape_query = f"reddit-user {query}"
    elif scrape_type == "search":
        snscrape_query = f"reddit-search {query}"
    else:
        raise ValueError(f"Invalid scrape type: {scrape_type}")
    
    # Create a temporary file to store the JSON output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
        tmp_filename = tmp_file.name
    
    try:
        # Run snscrape command to get Reddit data
        command = f'snscrape --jsonl --max-results {limit} {snscrape_query} > {tmp_filename}'
        subprocess.run(command, shell=True, check=True)
        
        # Read the JSON file into a DataFrame
        posts_df = pd.read_json(tmp_filename, lines=True)
        
        # Clean up the columns to match the expected output
        if not posts_df.empty:
            # Map common fields
            posts_df['created_utc'] = pd.to_datetime(posts_df['date'])
            
            # Handle different column names depending on the version of snscrape
            if 'title' not in posts_df.columns and 'content' in posts_df.columns:
                posts_df['title'] = posts_df['content']
            
            if 'author' not in posts_df.columns and 'username' in posts_df.columns:
                posts_df['author'] = posts_df['username']
                
            if 'score' not in posts_df.columns and 'upvoteCount' in posts_df.columns:
                posts_df['score'] = posts_df['upvoteCount']
                
            if 'num_comments' not in posts_df.columns and 'commentCount' in posts_df.columns:
                posts_df['num_comments'] = posts_df['commentCount']
                
            if 'permalink' not in posts_df.columns and 'url' in posts_df.columns:
                posts_df['permalink'] = posts_df['url']
        
        return posts_df
    
    except Exception as e:
        raise Exception(f"Failed to scrape Reddit data: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
