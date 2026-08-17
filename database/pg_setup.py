import os
import subprocess
import csv
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_NAME = "youtube_trending"

DATASET_PATH = r"C:\Users\Molisha Jain\Downloads\archive (1)\daily_trending_videos.csv"
OUTPUT_DIR = "hadoop"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.txt")
CSV_EXPORT_DIR = "power_bi_data"

def run_mapreduce_pipeline():
    print("[INFO] Running MapReduce pipeline programmatically...")
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset file not found at: {DATASET_PATH}")
        sys.exit(1)
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Locate python executable
    python_exe = r"C:\Users\Molisha Jain\anaconda3\python.exe"
    if not os.path.exists(python_exe):
        python_exe = "python"
        
    mapper_script = os.path.join("hadoop", "mapper.py")
    reducer_script = os.path.join("hadoop", "reducer.py")
    
    try:
        # Simulate Hadoop streaming: type dataset | python mapper | sort | python reducer > output
        print("[INFO] Phase 1: Mapper reading raw dataset...")
        p_mapper = subprocess.Popen(
            [python_exe, mapper_script],
            stdin=open(DATASET_PATH, "r", encoding="utf-8", errors="ignore"),
            stdout=subprocess.PIPE,
            encoding="utf-8",
            errors="ignore"
        )
        
        print("[INFO] Phase 2: Sorting map outputs...")
        # Read mapper output and sort it in python to replicate Hadoop's Shuffle & Sort phase
        mapper_out_lines = p_mapper.communicate()[0].splitlines()
        mapper_out_lines.sort()  # Sort by country (since key is the first column)
        
        sorted_data = "\n".join(mapper_out_lines)
        
        print("[INFO] Phase 3: Reducer aggregating values...")
        p_reducer = subprocess.Popen(
            [python_exe, reducer_script],
            stdin=subprocess.PIPE,
            stdout=open(OUTPUT_FILE, "w", encoding="utf-8"),
            encoding="utf-8",
            errors="ignore"
        )
        p_reducer.communicate(input=sorted_data)
        
        print(f"[SUCCESS] MapReduce output successfully written to: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"[ERROR] Failed to run MapReduce simulation: {e}")
        sys.exit(1)

def seed_database_and_export_csv():
    # Setup directories
    os.makedirs(CSV_EXPORT_DIR, exist_ok=True)
    
    # Data holders for local CSV export (fail-safe)
    trending_videos = []
    region_popularity = []
    global_stats = []
    
    if not os.path.exists(OUTPUT_FILE):
        print(f"[ERROR] MapReduce output file not found at: {OUTPUT_FILE}")
        return
        
    print("[INFO] Parsing MapReduce output file...")
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            type_tag = parts[0]
            
            if type_tag == 'VIDEO' and len(parts) >= 8:
                # VIDEO \t country \t video_id \t title \t channel \t views \t likes \t comments
                country = parts[1]
                vid_id = parts[2]
                title = parts[3]
                channel = parts[4]
                views = int(parts[5])
                likes = int(parts[6])
                comments = int(parts[7])
                eng_rate = round(((likes + comments) / views * 100), 2) if views > 0 else 0.0
                
                trending_videos.append((vid_id, title, channel, country, views, likes, comments, eng_rate))
                
            elif type_tag == 'COUNTRY_STATS' and len(parts) >= 8:
                # COUNTRY_STATS \t country \t video_count \t total_views \t total_likes \t total_comments \t top_video_title \t top_video_views
                country = parts[1]
                v_count = int(parts[2])
                t_views = int(parts[3])
                t_likes = int(parts[4])
                t_comments = int(parts[5])
                top_title = parts[6]
                top_views = int(parts[7])
                avg_eng = round(((t_likes + t_comments) / t_views * 100), 2) if t_views > 0 else 0.0
                
                region_popularity.append((country, v_count, t_views, t_likes, t_comments, avg_eng, top_title, top_views))
                
            elif type_tag == 'GLOBAL_STATS' and len(parts) >= 5:
                # GLOBAL_STATS \t total_videos \t total_views \t total_likes \t total_comments
                tot_videos = int(parts[1])
                tot_views = int(parts[2])
                tot_likes = int(parts[3])
                tot_comments = int(parts[4])
                avg_eng = round(((tot_likes + tot_comments) / tot_views * 100), 2) if tot_views > 0 else 0.0
                
                global_stats.append((tot_videos, tot_views, tot_likes, tot_comments, avg_eng))

    # --- PostgreSQL Connection & Creation ---
    postgres_success = False
    try:
        print("[INFO] Connecting to default PostgreSQL to setup database...")
        conn = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASS, host=DB_HOST)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate active connections to drop db
        cursor.execute(f'''
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{DB_NAME}'
              AND pid <> pg_backend_pid();
        ''')
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        cursor.close()
        conn.close()
        
        print(f"[INFO] Connecting to newly created database '{DB_NAME}'...")
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        
        # Create Tables
        cursor.execute('''
            CREATE TABLE trending_videos (
                video_id VARCHAR(100),
                title TEXT,
                channel_title TEXT,
                country VARCHAR(100),
                views BIGINT,
                likes BIGINT,
                comments BIGINT,
                engagement_rate FLOAT
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE region_popularity (
                country VARCHAR(100) PRIMARY KEY,
                video_count INT,
                total_views BIGINT,
                total_likes BIGINT,
                total_comments BIGINT,
                avg_engagement_rate FLOAT,
                top_video_title TEXT,
                top_video_views BIGINT
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE global_stats (
                total_videos INT,
                total_views BIGINT,
                total_likes BIGINT,
                total_comments BIGINT,
                avg_engagement_rate FLOAT
            );
        ''')
        
        # Seed Tables
        print(f"[INFO] Seeding trending_videos table with {len(trending_videos)} records...")
        cursor.executemany('''
            INSERT INTO trending_videos (video_id, title, channel_title, country, views, likes, comments, engagement_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', trending_videos)
        
        print(f"[INFO] Seeding region_popularity table with {len(region_popularity)} records...")
        cursor.executemany('''
            INSERT INTO region_popularity (country, video_count, total_views, total_likes, total_comments, avg_engagement_rate, top_video_title, top_video_views)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', region_popularity)
        
        print(f"[INFO] Seeding global_stats table...")
        cursor.executemany('''
            INSERT INTO global_stats (total_videos, total_views, total_likes, total_comments, avg_engagement_rate)
            VALUES (%s, %s, %s, %s, %s)
        ''', global_stats)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[SUCCESS] PostgreSQL database tables successfully seeded!")
        postgres_success = True
        
    except Exception as e:
        print(f"[WARNING] PostgreSQL setup failed: {e}")
        print("[INFO] Bypassing PostgreSQL. We will export processed data directly to CSV for Power BI.")

    # --- Export to CSV files for Power BI ---
    print(f"[INFO] Exporting data to '{CSV_EXPORT_DIR}/' folder...")
    
    # 1. Export Trending Videos
    with open(os.path.join(CSV_EXPORT_DIR, "trending_videos.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "title", "channel_title", "country", "views", "likes", "comments", "engagement_rate"])
        writer.writerows(trending_videos)
        
    # 2. Export Region Popularity
    with open(os.path.join(CSV_EXPORT_DIR, "region_popularity.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["country", "video_count", "total_views", "total_likes", "total_comments", "avg_engagement_rate", "top_video_title", "top_video_views"])
        writer.writerows(region_popularity)
        
    # 3. Export Global Stats
    with open(os.path.join(CSV_EXPORT_DIR, "global_stats.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["total_videos", "total_views", "total_likes", "total_comments", "avg_engagement_rate"])
        writer.writerows(global_stats)
        
    print(f"[SUCCESS] CSV files exported to '{CSV_EXPORT_DIR}' successfully!")
    if postgres_success:
        print("\n=== SETUP COMPLETE ===")
        print("1. MapReduce ran locally, generating hadoop/output.txt")
        print("2. PostgreSQL tables created & seeded inside 'youtube_trending'")
        print("3. Power BI CSV data exported to 'power_bi_data/'")
    else:
        print("\n=== SETUP COMPLETE (CSV ONLY) ===")
        print("1. MapReduce ran locally, generating hadoop/output.txt")
        print("2. Power BI CSV data exported to 'power_bi_data/'")
        print("[NOTE] You can load the CSV files directly into Power BI without using PostgreSQL!")

if __name__ == '__main__':
    run_mapreduce_pipeline()
    seed_database_and_export_csv()
