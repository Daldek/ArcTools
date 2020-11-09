import datetime
from datetime import datetime
import pandas as pd
import numpy as np
import openpyxl

# Input file link
# input_excel = input("Paste excel file path ")  # input excel file location
input_excel = r"C:\Work\python\_programy\proba_zmazania_hanby\test2.03\deszcze.xlsx"
output_excel = r"C:\Work\python\_programy\proba_zmazania_hanby\test2.03\output_rain.xlsx"
#work_book = openpyxl.Workbook(output_excel)

# excel_sheet_name = input("Paste sheet name with rain distribution ")  # excel sheet with rain distribution data
excel_sheet_name = "Sheet1"
time_step = 5  # input("Specify time step (in minutes) ")
sheet_name = str(time_step) + ' min rain'

data_frame = pd.read_excel(input_excel,
                           sheet_name=excel_sheet_name,
                           header=1,
                           usecols="B,D")  # it counts from 0, excluding workspace(columnes used for calculation)

test_date = data_frame["data"].tolist()
nonequidistant_time_list = []

test_rain = data_frame["um/s"].tolist()
nonequidistant_rain_list = []
for rain_value in test_rain:
    nonequidistant_rain_list.append(rain_value)
original_time_series_length = len(nonequidistant_rain_list)

# getting max rain value from list
peak_rain_value = max(nonequidistant_rain_list)
index_peak_rain_value = nonequidistant_rain_list.index(peak_rain_value)

#----------------------------date interpolation part----------------------------

for date_step in test_date:  # convert all list items to numbers
    # pandas timestamp to integer
    date_string = str(date_step)
    date_number = int(datetime.fromisoformat(date_string).timestamp())
    nonequidistant_time_list.append(date_number)

decrease_equidistant_time_list = np.arange(nonequidistant_time_list[index_peak_rain_value],
                                  nonequidistant_time_list[0],
                                  (time_step*-60))  # new list arrange with time step (decreasing starting from max value)

decrease_equidistant_time_list.sort()
decrease_equidistant_time_list = decrease_equidistant_time_list[0:-1]     # new list sorted to increase values with timestep and getting rid off peak value to avoid duplication in final list

increase_equidistant_time_list = np.arange(nonequidistant_time_list[index_peak_rain_value],
                                  nonequidistant_time_list[-1],
                                  (time_step*60))  # new list arrange with time step (increasing starting from max value)

equidistant_time_list = [*decrease_equidistant_time_list, *increase_equidistant_time_list]   # whole equdistant lime series
equidistant_time_list.sort()    # sorted just in case of unexpected things that might happened

final_date_list = []
for date_step in equidistant_time_list:  # convertion from numerical list to date list
    timestamp = datetime.fromtimestamp(date_step)
    equidistant_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    final_date_list.append(equidistant_date)

#-----------------------------rain interpolation part---------------------------

# interpolation function
def rain_interpolation(first_time_step, second_time_step, last_time_step,
                       rain_step_1, rain_step_2):
    rain_intensity = rain_step_1 \
                     + ((second_time_step - first_time_step)
                        / (last_time_step - first_time_step)) \
                     * (rain_step_2 - rain_step_1)
    return rain_intensity

#-----------------------------------test----------------------------------------

# for the sake of this interpolation we split time series on two parts
peak_right_nonequidistant_time_list = nonequidistant_time_list[index_peak_rain_value:]
peak_left_nonequidistant_time_list = nonequidistant_time_list[0:(index_peak_rain_value + 1)]
peak_right_nonequidistant_rain_list = nonequidistant_rain_list[index_peak_rain_value:]
peak_left_nonequidistant_rain_list = nonequidistant_rain_list[0:(index_peak_rain_value + 1)]

# reverse_peak_left_nonequidistant_time_list = peak_left_nonequidistant_time_list[::-1]   # reversing items in list will make interpolation easier to achieve
# reverse_peak_left_nonequidistant_rain_list = peak_left_nonequidistant_rain_list[::-1]
# reverse_decrease_equidistant_time_list = decrease_equidistant_time_list[::-1]

#------------------------rain intesity decrease interpolation-------------------
count_decrease = 0
peak_right_equidistant_rain_list = []

for de_non_eq_date_step in peak_right_nonequidistant_time_list:
    de_eq_boundary_list = []
    # eq_date_list = [] CONTROL STEP
    if de_non_eq_date_step == peak_right_nonequidistant_time_list[0]:
        count_decrease += 1

    else:
        de_date_lower_boundary = peak_right_nonequidistant_time_list[(count_decrease - 1)]
        de_date_upper_boundary = peak_right_nonequidistant_time_list[count_decrease]
        de_rain_lower_boundary = peak_right_nonequidistant_rain_list[(count_decrease - 1)]
        de_rain_upper_boundary = peak_right_nonequidistant_rain_list[count_decrease]

        # for eq_date_step in range(date_lower_boundary, date_upper_boundary, (time_step*60)):

        for de_eq_date_step in increase_equidistant_time_list:
            if de_eq_date_step >= de_date_lower_boundary:
                if de_eq_date_step <= de_date_upper_boundary:
                    de_eq_boundary_list.append(de_eq_date_step)
                    # for eq_date_step2 in de_eq_boundary_list:  # CONTROL STEP convertion from numerical list to date list
                    #     timestamp = datetime.fromtimestamp(eq_date_step2)
                    #     equidistant_date = timestamp.strftime(
                    #         '%Y-%m-%d %H:%M:%S')
                    #     eq_date_list.append(equidistant_date)
        for de_eq_boundary_list_step in de_eq_boundary_list:  # equidistant rain value calculation
            de_eq_rain_value = rain_interpolation(
                de_date_lower_boundary, de_eq_boundary_list_step,
                de_date_upper_boundary,
                de_rain_lower_boundary, de_rain_upper_boundary)
            peak_right_equidistant_rain_list.append(de_eq_rain_value)
        count_decrease += 1

#------------------------rain intesity increase interpolation-------------------
count_increase = 0
peak_left_equidistant_rain_list = []
eq_date_list = []
for non_eq_date_step in peak_left_nonequidistant_time_list:
    eq_boundary_list = []
    # eq_date_list = [] # CONTROL STEP
    if non_eq_date_step == peak_left_nonequidistant_rain_list[0]:
        count_increase += 1

    else:
        date_lower_boundary = peak_left_nonequidistant_time_list[(count_increase - 1)]
        date_upper_boundary = peak_left_nonequidistant_time_list[count_increase]
        rain_lower_boundary = peak_left_nonequidistant_rain_list[(count_increase - 1)]
        rain_upper_boundary = peak_left_nonequidistant_rain_list[count_increase]

        # for eq_date_step in range(date_lower_boundary, date_upper_boundary, (time_step*60)):

        for eq_date_step in decrease_equidistant_time_list:
            if eq_date_step >= date_lower_boundary:
                if eq_date_step <= date_upper_boundary:
                    eq_boundary_list.append(eq_date_step)
                    # for eq_date_step2 in eq_boundary_list:  # CONTROL STEP convertion from numerical list to date list
                    #     timestamp = datetime.fromtimestamp(eq_date_step2)
                    #     equidistant_date = timestamp.strftime(
                    #         '%Y-%m-%d %H:%M:%S')
                    #     eq_date_list.append(equidistant_date)
        for eq_boundary_list_step in eq_boundary_list:  # equidistant rain value calculation
            eq_rain_value = rain_interpolation(
                date_lower_boundary, eq_boundary_list_step,
                date_upper_boundary,
                rain_lower_boundary, rain_upper_boundary)
            peak_left_equidistant_rain_list.append(eq_rain_value)
        count_increase += 1

if time_step <= 5:
    peak_left_equidistant_rain_list = peak_left_equidistant_rain_list[0:-1]
else:
    peak_left_equidistant_rain_list = peak_left_equidistant_rain_list[0:]     # it is done to get rid off duble peak value

equidistant_rain_list = peak_left_equidistant_rain_list + peak_right_equidistant_rain_list

#------------------------------make_peak_at_12----------------------------------
#this is for extracting a hour from the date
peak_position = equidistant_rain_list.index(max(equidistant_rain_list))
convert = equidistant_time_list[peak_position]
years = convert // (365 * 24 * 60 * 60)
days = (convert - (years * 365 * 24 * 60 * 60)) // (24 * 60 * 60)
hour_time = convert - (years * 365 * 24 * 60 * 60) - (days * 24 * 60 * 60)

move = hour_time - 10 * 60 * 60 #amount of time needed to move peak to 12

adjusted_equidistant_time_list = []
for eq_time_step in equidistant_time_list:
    adjusted_eq_time_step = eq_time_step - move
    adjusted_equidistant_time_list.append(adjusted_eq_time_step)

#-------------------adding_last_step_at_the_end_of_list-------------------------
last_time_step = adjusted_equidistant_time_list[
                     len(adjusted_equidistant_time_list)- 1] + time_step * 60
last_rain_step = len(nonequidistant_rain_list) - 1
adjusted_equidistant_time_list.append(last_time_step)
equidistant_rain_list.append(nonequidistant_rain_list[last_rain_step])

# print(len(peak_right_equidistant_rain_list))
# print(len(increase_equidistant_time_list))
# print(len(peak_left_equidistant_rain_list))
# print(len(decrease_equidistant_time_list))
df = {'Date': adjusted_equidistant_time_list, 'um/s': equidistant_rain_list}
pd_df = pd.DataFrame.from_dict(df)

with pd.ExcelWriter(output_excel) as writer:
    pd_df.to_excel(writer, sheet_name)


