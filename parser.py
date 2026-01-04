import re

def parse_title(name: str):
    name = re.sub(r"\.(mkv|mp4|avi)$", "", name, flags=re.I)
    name = re.sub(r"(720p|1080p|2160p|x264|x265|HEVC|WEB[- ]DL|BluRay).*", "", name, flags=re.I)
    return name.replace(".", " ").strip()

def parse_quality(name: str):
    m = re.search(r"(2160p|1080p|720p|480p)", name)
    return m.group(1) if m else "unknown"
