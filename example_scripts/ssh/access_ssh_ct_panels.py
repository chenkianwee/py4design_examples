import paramiko
import os
#========================================================================================
#SPECIFY WHERE TO SAVE YOUR FILE IN THE LOCAL COM
#======================================================================================== 
domain = ""
username = ""
password = ""
res_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox\\"
#========================================================================================
#SPECIFY THE SENSOR NAME LABEL LOCATION 
#======================================================================================== 
sensor_list = ["'CT_PH19'", "'CT_PH12'", "'CT_PH10'", "'CT_PH15'", "'CT_PH16'", "'CT_PH18'",
               "'CT_PH11'", "'CT_PH13'", "'CT_PH22'"]

label_list = ["'humid'", "'airT'", "'dewpointT'", "'surfaceT'", "'supplyT'", "'returnT'"]
location = "'ColdTube'"

#========================================================================================
#CONNECT SSH
#========================================================================================
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.WarningPolicy())
print("*** Connecting...")
client.connect(domain,username=username, password=password)
print("*** Connected...")
#=======================================================================================
#EXPORT THE DATA 
#=======================================================================================
ftp_client=client.open_sftp()

name_var = "\"\\\"\"name\"\\\"\""

cnt = 1
for sensor_name in sensor_list:
    for label in label_list:
        sensor_name2 = sensor_name.replace("'", "") 
        label2 = label.replace("'", "")
        filename = "coldtube_panel" + str(cnt) + "_" + label2.lower() + ".csv"
        print filename
        res_filepath = os.path.join(res_dir, filename)

        influx_command = "influx -precision 'rfc3339' -database 'everything' -execute \"select value," +\
        name_var + " from chaos where " + name_var +  " = " + sensor_name + " and label = " + label +\
        " and location = " + location  + "\" " + "-format 'csv'>" + " '" + filename + "'"
        
        stdin, stdout, stderr = client.exec_command(influx_command)
        for line in stderr:
            print('... ' + line.strip('\n'))

        orig_dir = "/home/chaos/"
        orig_filepath = orig_dir + filename
        ftp_client.get(orig_filepath, res_filepath)
        rm_command = "rm " + filename
        stdin2, stdout2, stderr2 = client.exec_command(rm_command)
    cnt+=1

ftp_client.close()        
client.close()
