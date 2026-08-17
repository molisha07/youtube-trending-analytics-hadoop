# Power BI Dashboard Setup Guide

This guide walks you through setting up your interactive **YouTube Trending Analytics Dashboard** in Power BI Desktop using either the PostgreSQL database or the exported CSV files.

---

## 📂 Step 1: Connect Your Data Source

You have two choices to connect your data in Power BI:

### Option A: Import CSV Files (Easiest & Recommended)
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to the `youtube/power_bi_data/` folder and import these three files:
   - `trending_videos.csv`
   - `region_popularity.csv`
   - `global_stats.csv`
4. Click **Load** for each file.

### Option B: Connect Direct to PostgreSQL
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **More...** -> **PostgreSQL database** -> **Connect**.
3. In the dialog:
   - **Server:** `localhost`
   - **Database:** `youtube_trending`
4. Choose **Import** and click **OK**.
5. Enter your Postgres credentials (`postgres` / `1234`) when prompted.
6. Check the tables: `trending_videos`, `region_popularity`, `global_stats` and click **Load**.

---

## 🎨 Step 2: Configure Data Model (Optional but good practice)
Power BI usually links tables automatically. If not, go to the **Model View** (left sidebar):
- Connect `region_popularity[country]` (1) to `trending_videos[country]` (*) in a one-to-many relationship.

---

## 📊 Step 3: Create the Dashboard Pages

Create three pages in your Power BI report to match your previous setup:

### 🏠 Page 1: Dashboard (YT_TRENDS)
**Theme: Dark Mode** 
*(Go to View -> Themes -> Choose a dark theme or set background to `#0b1120`)*

1. **Stats Cards (KPI Cards):**
   - **Analyzed Videos:** Card using `SUM(global_stats[total_videos])`
   - **Total Views:** Card using `SUM(global_stats[total_views])`
   - **Total Engagements:** Card using `SUM(global_stats[total_likes]) + SUM(global_stats[total_comments])`
   - **Avg Engagement Rate:** Card using `AVERAGE(global_stats[avg_engagement_rate])` %

2. **Top Trending Videos (Global):**
   - Create a **Table** visual.
   - Add columns: `trending_videos[title]`, `trending_videos[channel_title]`, `trending_videos[views]`, `trending_videos[likes]`.
   - Sort the table by `views` descending.
   - In the Filters panel, set `views` filter type to **Top N**, type `10` as the value, and drag `views` as the "By value".

3. **Region Views Distribution Chart:**
   - Create a **Clustered Bar Chart** or **Column Chart** visual.
   - **X-Axis:** `region_popularity[country]`
   - **Y-Axis:** `region_popularity[total_views]`
   - Accent the columns with a neon gradient color if desired.

---

### 📈 Page 2: Market Analysis
1. **Views vs Likes Correlation:**
   - Create a **Scatter Chart** visual.
   - **Values:** `trending_videos[title]` (or Don't Summarize)
   - **X-Axis:** `trending_videos[views]`
   - **Y-Axis:** `trending_videos[likes]`
   - This will show a clear trendline of engagement intensity.

2. **Engagement Distribution (Donut Chart):**
   - Create a **Donut Chart** visual.
   - **Legend:** `trending_videos[country]`
   - **Values:** `trending_videos[views]`
   - Shows which countries dominate viewing numbers.

3. **Trending Video Repository (Table):**
   - Create a **Table** visual showing the full list of videos.
   - Add **Slicers** (Dropdown filters) for:
     - `trending_videos[country]`
     - `trending_videos[views]` (Numeric range slider)

---

### 🗺️ Page 3: Regions (Category Intelligence)
1. **Region Selector:**
   - Add a **Slicer** visual.
   - Set Field to `region_popularity[country]`.
   - Change the Slicer type to **Dropdown**.

2. **Top Video in Selected Region (Big Accent Visual):**
   - Create a **Card** or **Multi-row card** visual.
   - Display fields: `region_popularity[top_video_title]` and `region_popularity[top_video_views]` from `region_popularity`.
   - This updates dynamically as you toggle the Region Selector!

3. **Viewing Velocity (Column Chart):**
   - Create a **Column Chart** visual.
   - Axis: `trending_videos[title]`
   - Values: `trending_videos[views]`
   - Set Filters to show **Top 5** videos by views. This shows the velocity of top videos in the selected region.

---

## 🧮 Step 4: DAX Formulas (Custom Calculations)
If you want to create custom metrics, click **New Measure** on any table and paste:

* **Engagement Rate Measure:**
  ```DAX
  Engagement Rate = 
  DIVIDE(
      SUM(trending_videos[likes]) + SUM(trending_videos[comments]), 
      SUM(trending_videos[views]), 
      0
  ) * 100
  ```
