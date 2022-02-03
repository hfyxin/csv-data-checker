import time
import os
import sys

program_info = "\n" + \
    "+-------------------------- CSV data checker --------------------------+\n" + \
    "|  Check CSV data of D&V machine for data loss and out-of-sync issue.  |\n" + \
    "|  Works on single column CSV files only.                              |\n" + \
    "|    - ver 1.0 by by Elliot Huangfu Feb.2 2022                         |\n" + \
    "+----------------------------------------------------------------------+\n"
print(program_info)


while True:
    # automatically locate the latest CSV folder
    csv_parent_folder = r'C:\Users\eHuangfu\source\repos\CsvCheckerConsole\buildTest'    #
    csv_parent_folder = r'D:\D&V Electronics Ltd\Application Output\HT-250\VI_WAVdata'   # on tester PC
    if not os.path.exists(csv_parent_folder):
        csv_parent_folder = r'./'
    files = os.listdir(csv_parent_folder)
    files = [os.path.join(csv_parent_folder, f) for f in files]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)   # sort by date descending
    csv_folder = files[0]

    # Validate data folder
    print("The default folder to check csv files is:\n  " + csv_folder)
    while True:
        in_str = input("Press Enter to continue or, input desired folder path:\n")
        if in_str == "":
            break
        else:
            if os.path.exists(in_str):
                csv_folder = in_str
                break
            else:
                print("Input invalid:", in_str, end="\n")

    # get subfolders
    print("Examining files in folder:\n  " + csv_folder)
    try:
        fn_list = os.listdir(csv_folder)
    except:
        print("{} is not a valid CSV data folder.".format(csv_folder))
        input("Press Enter to exist.\n")
        sys.exit()

    # global variables
    sampling_rate = {
        "Current1.csv":200000,
        "Current2.csv":200000,
        "Current3.csv":200000,
        "Voltage1.csv":200000,
        "Voltage2.csv":200000,
        "Voltage3.csv":200000,
        "CurrentDC1.csv":20000,
        "DynoSpeed.csv":1000,
        "SV100ch1soundPressure.csv":48000,
    }
    n_rows = []
    duration = []
    zero_values = []

    print("|" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+" + "-"*14 + "|")
    print("|{:^30s}|{:^12s}|{:^12s}|{:^14s}|".format("filename", "size", "length (s)", "data loss"))
    print("|" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+" + "-"*14 + "|")

    for fn in fn_list:
        #with open(os.path.join(csv_folder, fn), newline='') as csvfile:
        #    values = csv.reader(csvfile, delimiter=' ', quotechar='|')
        #    for row in values:
        #        print(len(row), " - ", row)
        #        break

        data_loss_line = -1   # line of data loss

        try:
            with open(os.path.join(csv_folder, fn)) as file:
                lines = [float(line.rstrip()) for line in file]
            # data size
            n_rows.append(len(lines))
            # data duration
            if fn in sampling_rate:
                duration.append(len(lines) / sampling_rate[fn])
            else:
                duration.append(0)
            # check data valid, segment by segment
            seg_size = int(sampling_rate[fn] * 0.01)   # each segment is 0.01 sec, for DynoSpeed it's 10 points, for Current1 it's 2,000 points
            n_seg = int(len(lines) / seg_size)
            for i in range(n_seg):
                if lines[i*seg_size] == 0:
                    # double check if it's consecutive zeros
                    n_check = int(sampling_rate[fn] * 0.005)  # This must be smaller than seg_size
                    n_zeros = sum([v==0 for v in lines[i*seg_size: i*seg_size+n_check]])
                    if n_zeros == n_check:
                        # there is a data loss
                        data_loss_line = i*seg_size
                        break
            if data_loss_line == -1:
                zero_values.append(False)
            else:
                zero_values.append(True)
        except:
            n_rows.append(-1)
            duration.append(-1)
            zero_values.append(False)
            raise


        data_loss_print = "Good" if not zero_values[-1] else "line " + "{:d}".format(data_loss_line)
        print("|{:^30s}|{:^12d}|{:^12.3f}|{:^14}|".format(fn, n_rows[-1], duration[-1],data_loss_print))


    print("|"+"-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+" + "-"*14 + "|")

    # print result
    if len(duration) != 0:
        time_diff = max(duration) - min(duration)
        if time_diff > 0.05:
            print("WARNING: signal lengths have a difference of {:.3f}s. Please check data.".format(time_diff))
        if sum(zero_values) != 0:
            print("WARNING: data loss found. Please check data.")

        if time_diff <= 0.05 and sum(zero_values) == 0:
            print("Data looks good.")

    input("Press Enter to refresh and start over.\n")