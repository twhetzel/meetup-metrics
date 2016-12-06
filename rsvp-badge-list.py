# Imports to enable Python2/3 compatible code
from __future__ import print_function

import json
import requests


################################
# Read in api_key.json file, parse, prompt for which key to use based on meetup_name
# Make call to get MeetUp groupId based on meetup-name, then make call to get list of (upcoming) events
# Prompt for which event to get rsvp badge list and then based on selection get names
# Write output to timestamped file
################################

# Read file with MeetUp API Key(s)
def get_api_key():
    with open('./api_key.json') as api_key_file:
        api_key_list = json.load(api_key_file)

    # Dictionary key is meetup group name, value is api key
    meetup_api_key_dict = {}
    for api_key_dict in api_key_list:
        group_name = api_key_dict['meetup_name']
        group_api_key = api_key_dict['api_key']
        print("MeetUp Group: ", group_name)

        # Add to dictionary
        meetup_api_key_dict[group_name] = group_api_key

    # Prompt user for which MeetUp Group API Key to use
    meetup_group_name = raw_input('Enter the name of your MeetUp group from the list above: ')

    # Get API Key from dictionary for selected group
    meetup_api_key = meetup_api_key_dict[meetup_group_name]

    my_meetup_api_key_dict = {}
    my_meetup_api_key_dict[meetup_group_name] = meetup_api_key

    return my_meetup_api_key_dict


# Get list of Upcoming events
def get_upcoming_event_list(my_meetup_api_key_dict):
    key_list = my_meetup_api_key_dict.keys()
    # Dictionary contains only one key-value pair
    meetup_group_name = key_list[0]
    meetup_api_key = my_meetup_api_key_dict[meetup_group_name]

    # Event List doc: http://www.meetup.com/meetup_api/docs/:urlname/events/#list
    url = "https://api.meetup.com/"+meetup_group_name+"/events?photo-host=public&page=20&key="+meetup_api_key
    r = requests.get(url)
    if r.status_code == 200:
        print('DEBUG: Successful web service call')
        json_file_contents = r.json()

        # Check if list contains upcoming events
        if len(json_file_contents) == 0:
            print("No upcoming events found.")
        else:
            print("Events found")
            # Get list of event IDs
            event_name = json_file_contents[0]['name'].encode("utf-8")
            print("Event Name: ", event_name)

        # Prompt user for which MeetUp Group API Key to use
        # meetup_group_name = raw_input('Enter the name of your MeetUp group from the list above: ')

        event_id = json_file_contents[0]['id']
        return event_id
    else:
        print('ERROR: Unable to access URL. Failed with status code ', r.status_code)
        exit()


# Get list of people (first/last name) of RSVPs
def get_rsvp_badge_list(event_id, my_meetup_api_key_dict):
    # print('Get RSVP list')
    key_list = my_meetup_api_key_dict.keys()
    meetup_group_name = key_list[0]
    meetup_api_key = my_meetup_api_key_dict[meetup_group_name]
    f = open('december-07-2016.txt', 'w')

    event_url = "https://api.meetup.com/"+meetup_group_name+"/events/"+event_id+"/rsvps?photo-host=public&sig_id=22749361&key="+meetup_api_key+"&sign=true&fields=answers"
    r = requests.get(event_url)
    if r.status_code == 200:
        rsvp_list = r.json()

    count = 0
    name_entered_count = 0
    # Get first and last name of RSVP
    for rsvp in rsvp_list:
        rsvp_status = rsvp['response']
        rsvp_answers = rsvp['answers']

        # Get full name for members who RSVPd Yes
        if rsvp_status == 'yes':
            # Get user profile name
            user_profile_full_name = rsvp['member']['name'].strip()
            # print("\nUser Profile Name: "+user_profile_full_name)

            # Try to get full name from user entered information in 'Answers'
            for answer in rsvp_answers:
                rsvp_full_name = answer['answer']
                # print("RSVP Full Name: "+"\""+rsvp_full_name+"\"")
                # Check if user answered question of Full Name
                if rsvp_full_name != "":
                    # print("Name entered: "+rsvp_full_name)
                    count += 1
                    name_entered_count += 1
                    # Format name for printing
                    # TODO: Account for names with multiple spaces and combine appropriately
                    if " " in rsvp_full_name:
                        split_name = rsvp_full_name.split()
                        # print(split_name[0]+'\t'+split_name[1]+"\n")
                        formatted_rsvp_name = split_name[0]+'\t'+split_name[1]
                        f.write(formatted_rsvp_name.encode("utf-8")+"\n")
                else:
                    # print("Name NOT entered")
                    count += 1
                    # print("Profile Name: "+user_profile_full_name)
                    if " " in user_profile_full_name:
                        split_name = user_profile_full_name.split()
                        first_name = split_name.pop(0)
                        last_name = ""
                        for name in split_name:
                            last_name = last_name + name
                        # print(first_name+'\t'+last_name+"\n")
                        formatted_name = first_name+'\t'+last_name
                        f.write(formatted_name.encode("utf-8")+"\n")

    print("Count: ", count)
    print("Name entered count: ", name_entered_count)


# Main #
if __name__ == '__main__':
    my_meetup_api_key_dict = get_api_key()
    event_id = get_upcoming_event_list(my_meetup_api_key_dict)
    # print("Event ID: ", event_id)
    get_rsvp_badge_list(event_id, my_meetup_api_key_dict)
