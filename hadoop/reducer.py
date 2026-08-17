import sys

def main():
    current_country = None
    country_video_count = 0
    country_views = 0
    country_likes = 0
    country_comments = 0
    
    top_video = {"id": None, "title": None, "channel": None, "views": -1, "likes": 0, "comments": 0}
    
    global_video_count = 0
    global_views = 0
    global_likes = 0
    global_comments = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) < 7:
            continue
            
        country = parts[0]
        video_id = parts[1]
        title = parts[2]
        channel = parts[3]
        
        try:
            views = int(parts[4])
            likes = int(parts[5])
            comments = int(parts[6])
        except ValueError:
            continue
            
        # If we encounter a new country, output the stats of the previous country first
        if current_country != country:
            if current_country:
                # Output country stats: COUNTRY_STATS \t country \t video_count \t total_views \t total_likes \t total_comments \t top_video_title \t top_video_views
                print(f"COUNTRY_STATS\t{current_country}\t{country_video_count}\t{country_views}\t{country_likes}\t{country_comments}\t{top_video['title']}\t{top_video['views']}")
            
            # Reset country metrics
            current_country = country
            country_video_count = 0
            country_views = 0
            country_likes = 0
            country_comments = 0
            top_video = {"id": None, "title": None, "channel": None, "views": -1, "likes": 0, "comments": 0}
            
        # Accumulate country metrics
        country_video_count += 1
        country_views += views
        country_likes += likes
        country_comments += comments
        
        # Accumulate global metrics
        global_video_count += 1
        global_views += views
        global_likes += likes
        global_comments += comments
        
        # Track top video in the current country by view count
        if views > top_video["views"]:
            top_video = {
                "id": video_id,
                "title": title,
                "channel": channel,
                "views": views,
                "likes": likes,
                "comments": comments
            }
            
        # Output individual video record: VIDEO \t country \t video_id \t title \t channel \t views \t likes \t comments
        print(f"VIDEO\t{country}\t{video_id}\t{title}\t{channel}\t{views}\t{likes}\t{comments}")

    # Output the last country's stats
    if current_country:
        print(f"COUNTRY_STATS\t{current_country}\t{country_video_count}\t{country_views}\t{country_likes}\t{country_comments}\t{top_video['title']}\t{top_video['views']}")
        
    # Output global stats: GLOBAL_STATS \t total_videos \t total_views \t total_likes \t total_comments
    print(f"GLOBAL_STATS\t{global_video_count}\t{global_views}\t{global_likes}\t{global_comments}")

if __name__ == '__main__':
    main()
