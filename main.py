import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
from PIL import ImageTk, Image
import colorsys
import random

# Assuming your JSON file is named 'district.json'
with open('district.json', 'r', encoding='UTF8') as f:
    data1 = json.load(f)

districts = []

months = {
    "01": 31,
    "02": 28,
    "03": 31,
    "04": 30,
    "05": 31,
    "06": 30,
    "07": 31,
    "08": 31,
    "09": 30,
    "10": 31,
    "11": 30,
    "12": 31
}

def areaOfPolygon(polygon):
    n = len(polygon)
    area = 0

    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1]

    return 0.5 * abs(area)

def draw_dots(canvas, coords, fill_color, num_dots):
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for coord in coords:
        x, y = coord
        min_x, max_x = min(min_x, x), max(max_x, x)
        min_y, max_y = min(min_y, y), max(max_y, y)

    for _ in range(num_dots):
        x, y = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
        if point_in_polygon(x, y, coords):
            canvas.create_oval(int(x) - 1, int(y) - 1, int(x) + 1, int(y) + 1, fill=fill_color, outline='')


def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x < x_intersection:
                        inside = not inside

        p1x, p1y = p2x, p2y

    return inside

def update_day_choices(*args):
    selected_month = month_combobox.get()
    if selected_month in months:
        day_combobox['values'] = [str(i).zfill(2) for i in range(1, months[selected_month] + 1)]
    else:
        day_combobox['values'] = []

def find_data(date):
    date = date.split('-')
    data_list = []
    filename = date[1] + '월.csv'

    with open(filename, 'r', encoding='euc-kr') as data:
        for line in data:
            line = line.split(',')
            name = line[0]
            n = int(date[2])
            dust = line[n].strip()
            #print(name, dust)

            if name == '' or dust == '':
                data_list.append([name, None])
            else:
                data_list.append([name, dust])

    return data_list

def submit_date():
    year = "2023"
    month = month_combobox.get()
    day = day_combobox.get()
    date = f"{year}-{month}-{day}"
    
    data = find_data(date)
    
    if data:
        # Clear the districts list
        districts.clear()

        # Find the minimum and maximum coordinates
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for feature in data1['features']:
            name = feature['properties']['name']
            coordinates = feature['geometry']['coordinates']
            districts.append({'name': name, 'coordinates': coordinates})
    
            for polygon in coordinates:
                # Handle the possibility of nested coordinate arrays
                if isinstance(polygon[0][0], list):
                    polygon = polygon[0]
        
                for coord in polygon:
                    x, y = coord
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        # Calculate the scaling factor
        scale_x = 800 / (max_x - min_x)
        scale_y = 800 / (max_y - min_y)

        # Set up the canvas
        canvas_width = 800
        canvas_height = 800

        root = tk.Tk()
        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
        canvas.pack()

        # Draw each district
        for district in districts:
            coordinates = district['coordinates']

            # Get the district name
            district_name = district['name']

            # Find the corresponding dust value
            dust_value = None
            for data_entry in data:
                if data_entry[0] == district_name:
                    dust_value = data_entry[1]
                    break

            # Determine the fill color based on the dust value
            if dust_value is not None:
                fill_color = get_dust_color(dust_value)
            else:
                fill_color = 'white'

            for polygon in coordinates:
                # Handle the possibility of nested coordinate arrays
                if isinstance(polygon[0][0], list):
                    polygon = polygon[0]

                scaled_points = []
                for coord in polygon:
                    x = (coord[0] - min_x) * scale_x
                    y = canvas_height - (coord[1] - min_y) * scale_y  # Flip the y-coordinate
                    scaled_points.append((int(x), int(y)))

                # Draw the polygon with the assigned fill color
                canvas.create_polygon(scaled_points, outline='black', fill="white")

                 # Calculate the area of the polygon using the areaOfPolygon function
                areaPolygon = int(areaOfPolygon(scaled_points)/500)
                # Call the draw_dots function with the area of the polygon
                draw_dots(canvas, scaled_points, fill_color, int(dust_value) * areaPolygon)
                
                

                # Calculate the centroid coordinates
                centroid_x = sum(coord[0] for coord in polygon) / len(polygon)
                centroid_y = sum(coord[1] for coord in polygon) / len(polygon)

                # Adjust the label position
                label_x = (centroid_x - min_x) * scale_x
                label_y = canvas_height - (centroid_y - min_y) * scale_y  # Flip the y-coordinate

                # Draw the district name label
                # Draw the district name label
                canvas.create_text(label_x, label_y, text=district_name, font=("Arial", 20, "bold"), fill="black", anchor="center")





        root.mainloop()

def get_dust_color(dust):
    dust = int(dust)
    if dust <= 15:
        start_color = (0, 0, 255)  # Blue
        end_color = (0, 255, 0)  # Green
        normalized_dust = dust / 15  # Normalize dust value to range [0, 1]
    elif dust <= 35:
        start_color = (0, 255, 0)  # Green
        end_color = (255, 255, 0)  # Yellow
        normalized_dust = (dust - 15) / 20  # Normalize dust value to range [0, 1]
    elif dust <= 75:
        start_color = (255, 255, 0)  # Yellow
        end_color = (255, 165, 0)  # Orange
        normalized_dust = (dust - 35) / 40  # Normalize dust value to range [0, 1]
    else:
        start_color = (255, 165, 0)  # Orange
        end_color = (255, 0, 0)  # Red
        normalized_dust = 1.0
    
    # Interpolate between start_color and end_color based on the dust value
    r, g, b = [int(c1 * (1 - normalized_dust) + c2 * normalized_dust) for c1, c2 in zip(start_color, end_color)]

    # Convert RGB values to hexadecimal color code
    hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    
    return hex_color


def go_back():
    current_month = month_combobox.get()
    current_day = day_combobox.get()
    days_in_month = months[current_month]
    
    if current_day == "01":
        previous_month = "12" if current_month == "01" else str(int(current_month) - 1).zfill(2)
        day_combobox.set(str(months[previous_month]).zfill(2))
        month_combobox.set(previous_month)
    else:
        current_index = day_combobox["values"].index(current_day)
        previous_index = current_index - 1
        day_combobox.current(previous_index)

def go_forward():
    current_month = month_combobox.get()
    current_day = day_combobox.get()
    days_in_month = months[current_month]
    
    if current_day == str(days_in_month):
        next_month = "01" if current_month == "12" else str(int(current_month) + 1).zfill(2)
        day_combobox.set("01")
        month_combobox.set(next_month)
    else:
        current_index = day_combobox["values"].index(current_day)
        next_index = current_index + 1
        day_combobox.current(next_index)


window = tk.Tk()
window.title("날짜 입력")
window.geometry("400x160")
window.configure(bg="#f0f0f0")

frame = tk.Frame(window, bg="#f0f0f0")
frame.pack(pady=10)

month_label = tk.Label(frame, text="월:", font=("Arial", 12), bg="#f0f0f0")
month_label.grid(row=0, column=0, padx=5)
month_combobox = ttk.Combobox(frame, values=list(months.keys()), state="readonly")
month_combobox.grid(row=0, column=1, padx=5)
month_combobox.bind("<<ComboboxSelected>>", update_day_choices)

day_label = tk.Label(frame, text="일:", font=("Arial", 12), bg="#f0f0f0")
day_label.grid(row=1, column=0, padx=5)
day_combobox = ttk.Combobox(frame, values=[], state="readonly")
day_combobox.grid(row=1, column=1, padx=5)

button_frame = tk.Frame(window, bg="#f0f0f0")
button_frame.pack(pady=10)

back_button = ttk.Button(button_frame, text="←", command=go_back, width=3)
back_button.pack(side="left", padx=5)

forward_button = ttk.Button(button_frame, text="→", command=go_forward, width=3)
forward_button.pack(side="left", padx=5)

submit_button = tk.Button(window, text="생성", command=submit_date, font=("Arial", 12), bg="#f0f0f0")
submit_button.pack(pady=10)

window.mainloop()
