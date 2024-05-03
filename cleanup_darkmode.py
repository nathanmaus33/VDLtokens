import argparse
import json
import os
import re
from colors_accessibility import AccessibilityProcessor, Color

def convert_relative_to_global(path):
    # Get the path of the current script
    current_script_path = os.path.realpath(__file__)
    # Get the directory of the current script
    current_script_directory = os.path.dirname(current_script_path)
    dir_path = os.path.join(current_script_directory, path)
    dir_path = os.path.normpath(dir_path)
    return dir_path

def get_colors_data(file_path):
    colors_json_path = convert_relative_to_global(file_path)

    # Open the file and load the JSON data
    with open(colors_json_path, 'r') as f:
        colors_data = json.load(f)
    
    return colors_data

# A function that gets the global colors from the JSON data
def get_global_colors(colors_data):
    # Access the "Global" object
    global_colors = colors_data['_Global']['Olympus']['Color']['Global']
    return global_colors

# A function that gets the system colors from the JSON data
def get_system_colors(colors_data):
    # Access the "System" colors object
    light_colors = colors_data['System-Light']['Olympus']['Color']['System']["Light"]
    dark_colors = colors_data['System-Dark']['Olympus']['Color']['System']["Dark"]
    return light_colors, dark_colors

# A function that gets the system colors from the JSON data
def get_functional_colors(colors_data):
    # Access the "System" colors object
    light_colors = colors_data['Light']['Olympus']['Light']
    dark_colors = colors_data['Dark']['Olympus']['Dark']
    return light_colors, dark_colors

# A function that gets the functional colors from the JSON data
def get_background_secondary_color(colors_data):
    # Access the "color" object
    dark_background = colors_data["Dark"]['Olympus']["Dark"]["Background"]["Secondary"]
    _, dark_background_color, _ = extract_color_components(dark_background, get_global_colors(colors_data))
    return dark_background_color

# A function that extracts the color values from the JSON data and returns the red, green, blue, and alpha components
def extract_color_components(color_data, global_colors):
    # If the color type is a color convert it
    if color_data['type'] == 'color':
        alpha_component = 1.0
        red_component = 0.0
        green_component = 0.0
        blue_component = 0.0
        color = Color("rgb", color_values=[red_component, green_component, blue_component])

        color_value = color_data['value']
        # If color value is a hex string convert it using matplotlib
        if color_value.startswith('#'):
            # If the length of the hex string contains an alpha component then I need to use to_rgba

            # I need to pull out the color values data from a hex string
            # "SlateF": {
            #   "value": "#7A8585",
            #   "description": "Dark grey 3",
            #   "type": "color"
            # }
            color = Color("hex", color_values=color_value)

        # If the color_value references another color for it's rgb values
        elif 'Color.Global' in color_value:
            # I need to pull out the color values data from a hex string
            # "Red1Transparency15": {
            #   "value": "rgba( {Olympus.Color.Global.Red1} , 0.15)",
            #   "type": "color",
            #   "description": "Transparent red "
            # },
            # to 
            #  whatever the value of Olympus.Color.Global.Red1 is and 0.15 alpha
            print(color_value)

            # get the color name
            # Split the string on '{' and '}', and take the second element
            referenced_color_name_with_prefix = color_value.split('{')[1].split('}')[0]

            # Split the string on '.' and take the last element
            referenced_color_name = referenced_color_name_with_prefix.split('.')[-1]

            reference_color = global_colors[referenced_color_name]
            # get the refenece color values
            _, color, alpha_component = extract_color_components(reference_color, global_colors)

            # If there is an alpha component in the color value set it
            if len(color_value.split(',')) > 1:
                # get the alpha value for the current color
                alpha_component = color_value.split(',')[1].split(')')[0]

        elif color_value.startswith('rgb'):
            # I need to pull out the color values data from a hex string
            # "SlateF": {
            #   "value": "rgba(255,255,255,0)",
            #   "description": "Dark grey 3",
            #   "type": "color"
            # }
            # to 
            #   "components" : {
            #       "alpha" : "0.000",
            #       "blue" : "255",
            #       "green" : "255",
            #       "red" : "255"
            #     }
            #   },

            # get the rgba values
            rgba = color_value.split('(')[1].split(')')[0].split(',')
            red_component = rgba[0]
            green_component = rgba[1]
            blue_component = rgba[2]
            if len(rgba) > 3:
                alpha_component = rgba[3]
            color = Color("rgb", color_values=[red_component, green_component, blue_component])

    return color_value, color, alpha_component

def update_global_colors(global_colors):
    # Access the "Global" object
    colors_data['_Global']['Olympus']['Color']['Global'] = global_colors
    return

def update_dark_system_colors(dark_system_colors):
    # Access the "System" colors object
    colors_data['System-Dark']['Olympus']['Color']['System']["Dark"] = dark_system_colors
    return
    

def extract_number_from_end(s):
    match = re.search(r'\d+$', s)
    return int(match.group()) if match else None

# A function that gets the 'Green' and '1' out of a string like {Olympus.Color.Global.Green3}
def get_color_name_and_value(color_value):
    # Split the string on '{' and '}', and take the second element
    referenced_color_name_with_prefix = color_value.split('{')[1].split('}')[0]

    # Split the string on '.' and take the last element
    referenced_color_name = referenced_color_name_with_prefix.split('.')[-1]
    print("referenced_color_name: " + referenced_color_name)
    number = extract_number_from_end(referenced_color_name)
    return referenced_color_name[:-len(str(number))], number

# A function that gets the hex value from a color object
def get_hex_from_color(color):
    representation = color.get_representations('hex')
    hex_value = representation.hex
    return hex_value.normalized

def cleanup_darkmode_colors(colors_data):
    # Get the global colors
    global_colors = get_global_colors(colors_data)
    dark_background_color = get_background_secondary_color(colors_data)
    # Get the light mode and dark mode colors
    light_colors, dark_colors = get_system_colors(colors_data)

    # Check if the light mode colors have a corresponding dark mode color
    for color_name in light_colors:
        if color_name not in dark_colors:
            print(f"\n")
            print(f"Key {color_name} is not present in the dark mode colors.")
            global_color_name, color, alpha = extract_color_components(light_colors[color_name], global_colors)
            print(f"Original color: {global_color_name}")
            print(f"Color: {color}")
            print(f"Alpha: {alpha}")
            print(f"Dark background color: {dark_background_color}")
            original_hex = get_hex_from_color(color)
            # Convert the color to a dark mode accessible color
            processor = AccessibilityProcessor(color, dark_background_color)
            accessible_colors = processor.get_all_wcag_compliant_color()
            # print(f"Accessible colors: {accessible_colors}")
            new_dark_mode_color = accessible_colors.get('lightness').get('foreground').get('normal_aa')[0]
            print(f"New dark mode color: {new_dark_mode_color}")
            new_hex = get_hex_from_color(new_dark_mode_color).upper()
            print(f"New hex: {new_hex}")
            if new_hex != original_hex:
                # Add a new key to the global colors
                original_color_name, count = get_color_name_and_value(global_color_name)
                count += 1
                new_color_name = f"{original_color_name}{count}"
                global_colors[new_color_name] = {
                    "value": new_hex,
                    "type": "color",
                    "description": f"A generated dark mode {original_color_name} color."
                }
                update_global_colors(global_colors)
                
                #Save the new global_color_name 
                global_color_name = f"{{Olympus.Color.Global.{new_color_name}}}"
                print(f"New color is different from the original color.")
            # Save the new color to the dark mode colors
            dark_colors[color_name] = {
                "value": global_color_name,
                "type": "color",
                "description": f"A generated dark mode color for {color_name}.",
            }

            print(f"\n")
        else:
            print(f"Key {color_name} is present in the dark mode colors.")

    return colors_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cleanup the dark mode colors.')
    parser.add_argument('--filename',
                        type=str,
                        default='./tokens.json',
                        help='The name of the JSON file to parse.')
    args = parser.parse_args()

    # Check if the file has a .json extension
    _, ext = os.path.splitext(args.filename)

    if ext.lower() == '.json':
        colors_data = get_colors_data(args.filename)
        updated_colors_date = cleanup_darkmode_colors(colors_data)
        # Write the updated colors data to the file
        with open(args.filename, 'w') as f:
            json.dump(updated_colors_date, f, indent=2)
        # Make sure that each Light mode color has a corresponding Dark mode color
        
    else:
        raise ValueError("Input file must be a .json file")