from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import random

import matplotlib.pyplot as plt

from PIL import Image, ImageDraw, ImageFont

import os





file_id = input("Please enter the file ID: ")
title = "Ethnicity Estimate"
continent_colors = {
    'europe': (44, 49, 69),
    'asia': (20, 70, 45),
    'north-america': (40, 40, 40),
    'south-america': (40, 40, 40),
    'africa': (50, 50, 50),
    'antarctica': (60, 60, 60),
    'australia': (70, 70, 70)
}

colors_for_parts = {
    "South Italian": (61, 217, 207),
    "Basque": (38, 91, 240),
    "Danish": (100, 100, 100),
}

def get_color(part:str) -> tuple:
    if part not in colors_for_parts.keys():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    else:
        return colors_for_parts[part]




SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', "https://www.googleapis.com/auth/spreadsheets"]


# Replace YOUR_API_KEY with your actual API key
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(os.getcwd() + r'\google_creds\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


service = build('sheets', 'v4', credentials=creds)

def get(dimension:list, sheet_name:str) -> dict:
    range_ = "'{}'!{}:{}".format(sheet_name, dimension[0], dimension[1])
    return service.spreadsheets().values().get(spreadsheetId=file_id, range=range_).execute()["values"]

# data
fetched = get(["A2", f"""P{input("What is the last row with entries? (only number): ")}"""], input("What is the name of the spreadsheet the data is on? (exactly the name (also capital letters)): "))

result = {}

for entry in fetched:
    continent = entry[0]
    part_of_continent = entry[1]
    part = entry[2]
    percentage = entry[3]
    smaller_entries = entry[4:]
    
    if continent not in result:
        result[continent] = {}
    
    if part_of_continent not in result[continent]:
        result[continent][part_of_continent] = []

    result[continent][part_of_continent].append({'part': part, 'percentage': percentage, 'smaller_entries': smaller_entries})



height = 115
for continent, continent_data in result.items():
    height += 58
    for part_of_continent, data in continent_data.items():
        height += 56
        for item in data:
            height += 46
            for entry in item['smaller_entries']:
                height += 46
    height += 42



# Set up image and draw objects
image = Image.new('RGB', (1000, height), color=(255, 255, 255))
draw = ImageDraw.Draw(image)

# Set up font
title_font = ImageFont.truetype(os.getcwd() + r'\fonts\Unbounded-VariableFont_wght.ttf', size=30)
continent_font = ImageFont.truetype(os.getcwd() + r'\fonts\Unbounded-VariableFont_wght.ttf', size=25)
continental_parts_font = ImageFont.truetype(os.getcwd() + r'\fonts\Unbounded-VariableFont_wght.ttf', size=25)
region_ethic_font = ImageFont.truetype('arial.ttf', size=20)
region_font = ImageFont.truetype('arial.ttf', size=18)

# Calculate y-coordinate for writing text
y_text = 115
# Calculate y-coordinate for displaying boxes
y_box = 0


draw.rectangle(((0, y_box), (image.width, 100)), fill=(44, 49, 69))
y_box += 102
# Set up title
w, h = draw.textsize(title, font=title_font)
x = (image.width - w) / 2
draw.text((x, 50), title, fill="white", font=title_font)

# Iterate through data and write to image
for continent, continent_data in result.items():
    # Write continent
    draw.rectangle(((0, y_box), (image.width, y_box + 50)), fill=continent_colors[continent.lower()])
    y_box += 50
    draw.text((30, y_text), continent, fill=(255, 255, 255), font=continent_font)
    y_text += draw.textsize(continent, font=continent_font)[1] + 30
    
    # Iterate through continent data
    for part_of_continent, data in continent_data.items():
        # Write part of continent name
        draw.text((30, y_text), part_of_continent, fill=(0, 0, 0), font=continental_parts_font)
        y_text += h + 20
        y_box += h + 20
        
        # Iterate through data
        for item in data:
            # Write part, percentage, and smaller entries
            draw.rounded_rectangle(((50, y_text), (70, y_text+20)), 2, fill=get_color(item['part']), outline='black')
            draw.text((80, y_text), item['part'], fill=(0, 0, 0), font=region_ethic_font)
            draw.text((920, y_text), f"{float(item['percentage'])}%", fill=(0, 0, 0), font=region_ethic_font)
            y_text += h + 10
            y_box += h + 10
            for entry in item['smaller_entries']:
                draw.rounded_rectangle(((72, y_text+4), (82, y_text+14)), 5, fill='black', outline='black')
                draw.text((90, y_text), entry, fill=(0, 0, 0), font=region_font)
                y_text += h + 10
                y_box += h + 10

    y_box += 50
    y_text += 42


# Save image
image.save(os.getcwd() + r"\data.png")
