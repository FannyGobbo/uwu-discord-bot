import csv
from collections import defaultdict
from datetime import datetime
import hashlib
import sys
import os

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
        



##############################################################################################################################



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




##############################################################################################################################


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



# Process the new CSV file and update counts for a specific category (couscous, kayak, couscous_kayak)
def process_csv(file_path, user_counts):
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        timestamp_list = []

        for row in reader:
            # Convert timestamp to datetime object
            timestamp = datetime.strptime(row['timestamp'], '%d/%m %H:%M')
            user = row['user'].lower()
            message = str(row['message']).lower()
            hour = (timestamp.hour + 1) %24                                                       # Winter time, to be changed
            minutes = timestamp.minute
            hour, minutes = format_time(hour, minutes)
            
            if (len(message) > 3) and not(timestamp_list and (timestamp_list[-1] == timestamp)) :
                if hour == minutes:
                    if time_palindrome(hour, minutes):
                        if is_ck(message):  
                            user_counts['ck'][timestamp.month][user] += 1
                            timestamp_list.append(timestamp)
                    else :
                        if is_couscous(message):
                            user_counts['couscous'][timestamp.month][user] += 1
                            timestamp_list.append(timestamp)
                elif time_palindrome(hour, minutes):
                    if is_kayak(message) :
                        user_counts['kayak'][timestamp.month][user] += 1
                        timestamp_list.append(timestamp)


    return user_counts

# Calculate yearly totals for a specific category (couscous, kayak, couscous_kayak)
def calculate_yearly_totals(user_counts):
    yearly_totals = defaultdict(int)

    for month_counts in user_counts.values():
        for user, count in month_counts.items():
            yearly_totals[user] += count

    return yearly_totals


##############################################################################################################################



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3.10 couscous-process.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]

    user_counts = load_results_from_csv()

    # Process the new CSV file and update counts for each category
    user_counts = process_csv(csv_file_path, user_counts)
    
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

