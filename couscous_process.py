import csv
from collections import defaultdict
from datetime import datetime
import hashlib
import sys
import os


############################################################################################################################## BASIC FUNCTIONS

# Function to check if a time is a palindrome
def time_palindrome(hour, minutes):
    str_num1 = str(hour)
    str_num2 = str(minutes)

    # Concatenate the strings
    concatenated_str = str_num1 + str_num2

    # Check if the concatenated string is a palindrome
    return concatenated_str == concatenated_str[::-1]

# Check if string is palindrome
def is_kayak(s):
    return s == s[::-1]

def is_couscous(s):
    if len(s)%2 != 0:
        return False
    else :
        firstpart, secondpart = s[:len(s)//2], s[len(s)//2:]
        return firstpart == secondpart
    
def is_ck(s) :
    word_list = s.split()
    if len(word_list) == 1 :
        return is_kayak(s) and is_couscous(s)
    elif len(word_list) == 2 :
        return is_couscous(word_list[0]) and is_kayak(word_list[1])
    else:
        return False
        
        
def format_time(hour, minutes):
    if hour < 10:
        out_h = "0" + str(hour)
    else:
        out_h = str(hour)
    if minutes < 10:
        out_m = "0" + str(minutes)
    else :
        out_m = str(minutes)
    return out_h, out_m



############################################################################################################################## LOADING CSV FUNCTIONS



# Load results from a CSV file for a specific category (couscous, kayak, couscous_kayak)
def load_results_from_csv():
    categories = ['couscous', 'kayak', 'ck']
    results = {}

    for category in categories:
        file_path = f'./results/global-{category}.csv'
        category_dict = defaultdict(lambda: defaultdict(int))

        with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')

            for row in reader:
                user = row['User']
                for month in range(1, 13):
                    count = int(row[str(month)])
                    category_dict[month][user] = count

        results[category] = category_dict
        
    return results


def load_timestamps():
    filepath = "./timestamps.csv"
    result = {}
    
    with open(filepath, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        
        for row in reader:
            user = row['User']
            result[user] = int(row['time-diff'])
    
    return result


# Save results to a CSV file for a specific category (couscous, kayak, couscous_kayak)
def save_results_to_csv(user_counts, yearly_total):
    categories = ['couscous', 'kayak', 'ck']
    
    for category in categories:
        file_path = f'./results/global-{category}.csv'
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')

            # Write header
            writer.writerow(['User'] + list(range(1, 13)) + ['Total'])

            # Write data
            for user in yearly_total[category]:  
               writer.writerow([user] + [str(user_counts[category][month][user]) for month in range(1, 13)] + [str(yearly_total[category][user])])



def save_global_results(yearly_totals, global_totals):
    categories = ['couscous', 'kayak', 'ck']
    file_path = "./results/global.csv"
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')

            # Write header
            writer.writerow(['User'] + ["couscous"] + ["kayak"] + ["ck"] + ["Total"])

            # Write data
            for user in yearly_totals["couscous"]:  
               writer.writerow([user] + [str(yearly_totals[category][user]) for category in ['couscous', 'kayak', 'ck']] + [str(global_totals[user])])


############################################################################################################################## PROCESS



# Process the new CSV file and update counts for a specific category (couscous, kayak, couscous_kayak)
def process_csv(file_path, user_counts):
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        timestamp_dict = {
            'fr': [],
            'sf': []
        }
        time_diff = load_timestamps()

        for row in reader:
            # Convert timestamp to datetime object
            timestamp = datetime.strptime(row['timestamp'], '%d/%m %H:%M')
            user = row['user'].lower()
            
            if user in list(time_diff.keys()):
                message = str(row['message']).lower()
                hour = (timestamp.hour + time_diff[user]) %24                                                       # Winter time, to be changed
                minutes = timestamp.minute
                hour, minutes = format_time(hour, minutes)
            
                if user == "skynox11":
                    place = 'sf'
                else :
                    place = 'fr'
                
                
                if (len(message) > 3) and not(timestamp_dict[place] and (timestamp_dict[place] == timestamp)) :
                    if hour == minutes:
                        if time_palindrome(hour, minutes):
                            if is_ck(message):  
                                user_counts['ck'][timestamp.month][user] += 1
                                timestamp_dict[place].append(timestamp)
                        else :
                            if is_couscous(message):
                                user_counts['couscous'][timestamp.month][user] += 1
                                timestamp_dict[place].append(timestamp)
                    elif time_palindrome(hour, minutes):
                        if is_kayak(message) :
                            user_counts['kayak'][timestamp.month][user] += 1
                            timestamp_dict[place].append(timestamp)


    return user_counts


# Calculate yearly totals for a specific category (couscous, kayak, couscous_kayak)
def calculate_yearly_totals(user_counts):
    yearly_totals = defaultdict(int)

    for month_counts in user_counts.values():
        for user, count in month_counts.items():
            yearly_totals[user] += count

    return yearly_totals


############################################################################################################################## UPDATE FUNCTIONS

def update_time_diff(user, new_tz):
    timezones = load_timestamps()
    
    timezones[user] = new_tz
    
    with open('timestamps.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['User', 'time-diff'])  # Write header
        for user, time_diff in timezones.items():
            writer.writerow([user, time_diff])


        
def add_user_to_game(user):
    categories = ['couscous', 'kayak', 'ck']
    
    for category in categories:
        file_path = f'./results/global-{category}.csv'
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([user] + [0] * 13)
    
    # add tow to global
    with open("./results/global.csv", 'a', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([user] + [0] * 4)
    
    # add row to timestamps
    with open('timestamps.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([user, 1])
        
    
    
    




############################################################################################################################## MAIN FUNCTION

def run_couscous_update (file_path):
    user_counts = load_results_from_csv()

    # Process the new CSV file and update counts for each category
    user_counts = process_csv(file_path, user_counts)
    
    # Calculate yearly totals
    yearly_totals = {category: calculate_yearly_totals(user_counts[category]) for category in ['couscous', 'kayak', 'ck']}
    
    global_totals = defaultdict(int)
    for user in yearly_totals["couscous"] :
        value = 0
        for category in ['couscous', 'kayak', 'ck']:
            value += yearly_totals[category][user]
        global_totals[user] = value
    
    save_results_to_csv(user_counts, yearly_totals)

    save_global_results(yearly_totals, global_totals)


def add_one_point (username, month, category):
    user_counts = load_results_from_csv()
    
    user_counts[category][month][username] += 1
    
    # Calculate yearly totals
    yearly_totals = {category: calculate_yearly_totals(user_counts[category]) for category in ['couscous', 'kayak', 'ck']}
    
    global_totals = defaultdict(int)
    for user in yearly_totals["couscous"] :
        value = 0
        for category in ['couscous', 'kayak', 'ck']:
            value += yearly_totals[category][user]
        global_totals[user] = value
    
    save_results_to_csv(user_counts, yearly_totals)

    save_global_results(yearly_totals, global_totals)
    

def add_n_points (username, month, category, amount):
    user_counts = load_results_from_csv()

    user_counts[category][month][username] += amount
    
    # Calculate yearly totals
    yearly_totals = {category: calculate_yearly_totals(user_counts[category]) for category in ['couscous', 'kayak', 'ck']}
    
    global_totals = defaultdict(int)
    for user in yearly_totals["couscous"] :
        value = 0
        for category in ['couscous', 'kayak', 'ck']:
            value += yearly_totals[category][user]
        global_totals[user] = value
    
    save_results_to_csv(user_counts, yearly_totals)

    save_global_results(yearly_totals, global_totals)
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3.10 couscous-process.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    
    run_couscous_update(csv_file_path)


