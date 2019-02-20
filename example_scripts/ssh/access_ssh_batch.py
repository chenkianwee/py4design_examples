import paramiko
import os
#========================================================================================
#SPECIFY WHERE TO SAVE YOUR FILE IN THE LOCAL COM
#======================================================================================== 
ssh_file = open("C:\\Users\\chaosadmin\\Desktop\\ssh.txt", "r")
lines = ssh_file.readlines()
domain = lines[0].replace("\n", "")
username = lines[1].replace("\n", "")
password = lines[2].replace("\n", "")
ssh_file.close()

res_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox\\"
#========================================================================================
#SPECIFY THE SENSOR NAME LABEL LOCATION 
#======================================================================================== 
#filename list shld have the same count as sensor_list
parent_filename_list = ["coldtube_environment_tekanan" ] 
sensor_list = ["'tekanan'"]
#label_list = ["'humidity1'", "'humidity2'", "'air'", "'dewpoint'", "'globe'"]
label_list = ["'globe'"]
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

cnt = 0
for sensor_name in sensor_list:
    for label in label_list:
        label2 = label.replace("'", "")
        parent_filename = parent_filename_list[cnt]
        filename = parent_filename + "_" + label2.lower() + ".csv"
        #==========================================
        print "*** Exporting ...", filename
        #==========================================
        influx_command = "influx -precision 'rfc3339' -database 'everything' -execute \"select value," +\
        name_var + " from chaos where " + name_var +  " = " + sensor_name + " and label = " + label +\
        " and location = " + location  + "\" " + "-format 'csv'>" + " '" + filename + "'"
        
        stdin, stdout, stderr = client.exec_command(influx_command)
        for line in stderr:
            print('... ' + line.strip('\n'))
            
        orig_dir = "/home/chaos/"
        orig_filepath = orig_dir + filename
        res_filepath = os.path.join(res_dir, filename)
        #==========================================
        print "*** Downloading ...", res_filepath
        #==========================================
        ftp_client.get(orig_filepath, res_filepath)
        rm_command = "rm " + filename
        stdin2, stdout2, stderr2 = client.exec_command(rm_command)
    cnt+=1

ftp_client.close()        
client.close()
