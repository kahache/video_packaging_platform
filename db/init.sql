CREATE DATABASE IF NOT EXISTS video_files;
use video_files;

CREATE TABLE IF NOT EXISTS movie_files (
  input_content_origin VARCHAR(255),
  content_id INT PRIMARY KEY AUTO_INCREMENT,
  video_track_number INT,
  status VARCHAR(20),
  output_file_path VARCHAR(255),
  video_key TEXT,
  kid TEXT,
  packaged_content_id INT UNIQUE,
  url VARCHAR(255)
);

/* for further production environments, it should be interesting to have
/* more tables and store data like date, time ingested; as more info from the
/* video files: duration of the file, codecs, bitrate, container type,
/* more metadata from the json... etc
