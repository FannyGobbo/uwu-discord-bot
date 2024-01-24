import csv
from collections import defaultdict
from datetime import datetime
import hashlib
import sys
import os

# Function to check if a string is a palindrome
def is_palindrome(hour, minutes):
    str_num1 = str(hour)
    str_num2 = str(minutes)

    # Concatenate the strings
    concatenated_str = str_num1 + str_num2

    # Check if the concatenated string is a palindrome
    return concatenated_str == concatenated_str[::-1]

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


# Process the new CSV file and update counts for a specific category (couscous, kayak, couscous_kayak)
def process_csv(file_path, user_counts):
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Convert timestamp to datetime object
            timestamp = datetime.strptime(row['timestamp'], '%d/%m %H:%M')
            user = row['user'].lower()
            message = str(row['message']).lower()
            hour = timestamp.hour + 1
            minutes = timestamp.minute

            # Process "couscous" message
            if message == 'couscous':
                if hour== minutes:
                    user_counts['couscous'][timestamp.month][user] += 1

            # Process "kayak" message
            elif message == 'kayak':
                if is_palindrome(hour, minutes):
                    user_counts['kayak'][timestamp.month][user] += 1

            # Process "couscous kayak" message
            elif message == 'couscous kayak':
                if is_palindrome(hour, minutes) and hour == minutes:
                    user_counts['ck'][timestamp.month][user] += 1


    return user_counts

# Calculate yearly totals for a specific category (couscous, kayak, couscous_kayak)
def calculate_yearly_totals(user_counts):
    yearly_totals = defaultdict(int)

    for month_counts in user_counts.values():
        for user, count in month_counts.items():
            yearly_totals[user] += count

    return yearly_totals

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3.10 couscous-process.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]


    user_counts = load_results_from_csv()
    
    #print(user_counts)

    # Process the new CSV file and update counts for each category
    user_counts = process_csv(csv_file_path, user_counts)
    
#    print(user_counts["couscous"])
 #   print(user_counts["kayak"])
  #  print(user_counts["ck"])

    # Calculate yearly totals for each category
    yearly_totals = {category: calculate_yearly_totals(user_counts[category]) for category in ['couscous', 'kayak', 'ck']}
    
    global_totals = defaultdict(int)
    for user in yearly_totals["couscous"] :
        value = 0
        for category in ['couscous', 'kayak', 'ck']:
            value += yearly_totals[category][user]
        global_totals[user] = value
    
    save_results_to_csv(user_counts, yearly_totals)

    save_global_results(yearly_totals, global_totals)
