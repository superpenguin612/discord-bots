import json
import re
import math
from datetime import date,datetime,time,timedelta

with open("bot/school_info.json") as f:
    SCHOOL_INFO_DICT = json.load(f)

def get_current_day(user_info=None):
    if user_info:
        current_day = SCHOOL_INFO_DICT["days"][user_info["cohort"]][datetime.now().strftime("%m/%d/%Y")]
    else:
        current_day = SCHOOL_INFO_DICT["days"]["carmel"][datetime.now().strftime("%m/%d/%Y")], SCHOOL_INFO_DICT["days"]["greyhound"][datetime.now().strftime("%m/%d/%Y")]
    return current_day

def get_day(date, user_info=None):
    if user_info:
        current_day = SCHOOL_INFO_DICT["days"][user_info["cohort"]][date]
    else:
        current_day = SCHOOL_INFO_DICT["days"]["carmel"][date], SCHOOL_INFO_DICT["days"]["greyhound"][date]
    return current_day

def get_week(user_info=None):
    if user_info:
        current_week = []
        for i in range (7):
            target_day = datetime.now() + timedelta(days = i + 1)
            current_week.append(target_day.strftime("%a, %b %d, %Y: ")
                + SCHOOL_INFO_DICT["days"][user_info["cohort"]][target_day.strftime("%m/%d/%Y")])
        return current_week
    else:
        current_week_1 = []
        current_week_2 = []
        for i in range (7):
            target_day = datetime.now() + timedelta(days = i + 1)
            current_week_1.append(target_day.strftime("%a, %b %d, %Y: ")
                + SCHOOL_INFO_DICT["days"]['carmel'][target_day.strftime("%m/%d/%Y")])
            current_week_2.append(target_day.strftime("%a, %b %d, %Y: ")
                + SCHOOL_INFO_DICT["days"]['greyhound'][target_day.strftime("%m/%d/%Y")])
        return current_week_1, current_week_2

# def get_current_block(user_info=None):
#     if user_info:
#         pass
#     else:
#         current_day = get_current_day(user_info)
#         day_type = re.search("(Blue|Gold)",current_day)
#         overview_dict = SCHOOL_INFO_DICT["overview"][day_type][user_info["cohort"]]
#         current_block = overview_dict[]
#     return current_block


# # setting values
# current_day = SCHOOL_INFO_DICT["days"][user_information["cohort"]][datetime.now().strftime("%m/%d/%Y")]
# if("Late" in current_day):
#     day_type = "late"
# elif(re.search("(Blue|Gold)",current_day)):
#     day_type = "normal"
# else:
#     day_type = "none"

# if(day_type != "none"):
#     day_lunch = re.search("(Blue|Gold)",current_day).group().lower() + "Lunch"
#     day_classes = user_information[re.search("(Blue|Gold)",current_day).group().lower() + "day_classes"]
#     current_class_dict = SCHOOL_INFO_DICT["currentClass"][day_type][user_information[day_lunch]]
#     overview_dict = SCHOOL_INFO_DICT["overview"][day_type][user_information[day_lunch]]
# else:
#     day_lunch = ""
#     day_classes = ""
#     current_class_dict = ""
#     overview_dict = ""

# # currentClass
# current_class_result = "Current Class\n"
# day_overview_raw_blocks = [""]
# day_status = ""
# if(day_type != "none"):
#     for item in sorted(current_class_dict.keys()):
#         if(not current_class_result):
#             formatted_item = datetime.combine(datetime.now(),datetime.strptime(item,"%H:%M").time())
#             time_between_dates = formatted_item - datetime.now()
#             if(time_between_dates > timedelta()): # if time_between_dates is greater than zero
#                 new_item = datetime.strptime(item,"%H:%M").strftime("%I:%M %p")
#                 current_class_result += "%s%s minute(s) (%s)." % (current_class_dict[formatted_item.strftime("%H:%M")],
#                 math.ceil(time_between_dates.seconds/60),new_item)
#         elif(current_class_result):
#             day_overview_raw_blocks.append(overview_dict[item])
#     if(not current_class_result):
#         time_between_dates = datetime.strptime("15:45","%H:%M") - datetime.now()
#         current_class_result += "Block 4 ended %s minutes ago (3:45 PM)." % (time_between_dates)
#         day_status = "finished"
# else:
#     current_class_result += "There is no school today."

# if(day_type != "none"): # replace block name
#     if(""):
#         current_class_result = re.sub("(Block\s[0-9])",day_classes[re.search("(Block\s[0-9])",current_class_result).group()],current_class_result)

# # dayOverview
# day_overview_result = "Day Overview\n"
# if(re.search("(3:45)",current_class_result)):
#     day_overview_result += "There are no more classes today."
# elif(re.search("(today)",current_class_result)):
#     day_overview_result += "There are no classes today."
# elif(not re.search("(3:45|today)",current_class_result)):
#     for item in day_overview_raw_blocks:
#         if ("Lunch" not in item and ""):
#             item = re.sub("Block\s[0-9]",day_classes[re.search("(Block\s[0-9])",item).group()],item)

# # weekOverview
# week_overview_result = "Week Overview"
# for i in range (7):
#     week_overview_result += ("\n" + (datetime.now() + timedelta(days = i + 1)).strftime("%a, %b %d, %Y: ")
#     + SCHOOL_INFO_DICT["days"][user_information["cohort"]][(datetime.now() + timedelta(days = i + 1)).strftime("%m/%d/%Y")])

# # finalResult
# final_result = date_result + "\n\n" + current_class_result + "\n\n" + day_overview_result + "\n\n" + week_overview_result
# print(final_result)

# final_result_file = open("/Applications/AppleScriptTemp/ClassScheduleResult.txt","w")
# final_result_file.write(final_result)
# final_result_file.close()