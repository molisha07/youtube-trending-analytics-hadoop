import sys
import csv

def main():
    # Set up csv reader to read from standard input
    # We use csv.reader to handle commas and double quotes in titles correctly
    reader = csv.reader(sys.stdin)
    
    # Try to skip the header if it contains 'video_id'
    try:
        header = next(reader, None)
        if header and header[0] != 'video_id':
            # If the first row wasn't the header, we process it
            process_row(header)
    except Exception:
        pass
        
    for row in reader:
        process_row(row)

def process_row(row):
    if len(row) < 7:
        return
    try:
        video_id = row[0]
        title = row[1]
        channel = row[2]
        country = row[3]
        views = int(row[4])
        likes = int(row[5])
        comments = int(row[6])
        
        # Emit fields separated by tabs. 
        # Format: country \t video_id \t title \t channel \t views \t likes \t comments
        # We replace any tab characters in strings with spaces to avoid breaking MapReduce parsing
        title_clean = title.replace('\t', ' ')
        channel_clean = channel.replace('\t', ' ')
        
        print(f"{country}\t{video_id}\t{title_clean}\t{channel_clean}\t{views}\t{likes}\t{comments}")
    except ValueError:
        # Ignore lines with invalid integer values for views, likes, or comments
        pass

if __name__ == '__main__':
    main()
