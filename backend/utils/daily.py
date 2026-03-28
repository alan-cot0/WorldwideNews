from io import StringIO
import csv
import requests
import pandas as pd

EVENT_COLUMNS = [
    "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate", 
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode",
    "Actor1Religion1Code", "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",

    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode",
    "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",

    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions",
    "NumSources", "NumArticles", "AvgTone",

    "Actor1Geo_Type", "Actor1Geo_Fullname", "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",

    "Actor2Geo_Type", "Actor2Geo_Fullname", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",

    "ActionGeo_Type", "ActionGeo_Fullname", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_ADM2Code",
    "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",

    "DATEADDED", "SOURCEURL"
]


MENTIONS_COLUMNS = [
    "GlobalEventID", "EventTimeDate", "MentionTimeDate", "MentionType", "MentionSourceName",
    "MentionIdentifier", "SentenceID", "Actor1CharOffset", "Actor2CharOffset", "ActionCharOffset",

    "InRawText", "Confidence", "MentionDocLen", "MentionDocTone", "MentionDocTranslationInfo",
    "Extras"
]

GKG_COLUMNS = [
    "GKGRECORDID", "V2.1DATE", "V2SOURCECOLLECTIONIDENTIFIER", "V2SOURCECOMMONNAME", "V2DOCUMENTIDENTIFIER",
    "V1COUNTS", "V2.1COUNTS", "V1THEMES", "V2ENHANCEDTHEMES", "V1LOCATIONS", 
    "V2ENHANCEDLOCATIONS", "V1PERSONS", "V2ENHANCEDPERSONS", "V1ORGANIZATIONS", "V2ENHANCEDORGANIZATIONS",
    "V1.5TONE", "V2.1ENHANCEDDATES", "V2GCAM", "V2.1SHARINGIMAGE", "V2.1RELATEDIMAGES",
    "V2.1SOCIALIMAGEEMBEDS", "V2.1SOCIALVIDEOEMBEDS", "V2.1QUOTATIONS", "V2.1ALLNAMES", "V2.1AMOUNTS",
    "V2.1TRANSLATIONINFO", "V2EXTRASXML"
]

def get_update ():
    url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
    resp = requests.get(url)

    if (resp.status_code != 200): raise Exception("GDELT API Down")

    data = resp.text
    f = StringIO(data)
    reader = csv.reader(f, delimiter=" ")

    links = [row[2] for row in reader]
    return links

# Parses GDELT 2.0 Event CSV
# File Format http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf

def parse_event (url: str) -> pd.DataFrame:
    df = pd.read_csv(
        url, 
        sep='\\t',
        engine='python', 
        names=EVENT_COLUMNS
    )

    return df

# Parses GDELT 2.0 Mentions Table CSV
# File Format http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
# Mentions table records mentions of events in the event table 

def parse_mentions (url: str) -> pd.DataFrame:
    df = pd.read_csv(
        url, 
        sep='\\t',
        engine='python', 
        names=MENTIONS_COLUMNS
    )

    return df

# Parses GDELT 2.0 GKG CSV
# File Format http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf

def parse_gkg (url: str) -> pd.DataFrame:
    df = pd.read_csv(
        url, 
        sep='\\t',
        engine='python', 
        names=GKG_COLUMNS
    )

    return df