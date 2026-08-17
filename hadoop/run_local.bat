@echo off
SET DATASET_PATH=C:\Users\Molisha Jain\Downloads\archive (1)\daily_trending_videos.csv
SET PYTHON_PATH=C:\Users\Molisha Jain\anaconda3\python.exe

if not exist "%PYTHON_PATH%" (
    SET PYTHON_PATH=python
)

if not exist "%DATASET_PATH%" (
    echo [ERROR] Dataset not found at: %DATASET_PATH%
    echo Please make sure the CSV file exists.
    exit /b 1
)

echo [INFO] Running MapReduce locally (Mapper -^> Sort -^> Reducer)...
echo [INFO] Reading dataset: %DATASET_PATH%

type "%DATASET_PATH%" | "%PYTHON_PATH%" hadoop\mapper.py | sort | "%PYTHON_PATH%" hadoop\reducer.py > hadoop\output.txt

echo [INFO] MapReduce successfully completed!
echo [INFO] Output stored in: hadoop\output.txt
