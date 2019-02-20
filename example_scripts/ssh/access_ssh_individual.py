import paramiko
import os
#========================================================================================
#SPECIFY THE SSH TO CONNECT TO
#======================================================================================== 
ssh_file = open("C:\\Users\\chaosadmin\\Desktop\\ssh.txt", "r")
lines = ssh_file.readlines()
domain = lines[0].replace("\n", "")
username = lines[1].replace("\n", "")
password = lines[2].replace("\n", "")
ssh_file.close()

#========================================================================================
#SPECIFY THE SENSOR NAME LABEL LOCATION 
#======================================================================================== 
sensor_name = "'CT_PH21'"
label = "'returnT'"
location = "'ColdTube'"
#========================================================================================
#SPECIFY WHERE TO SAVE YOUR FILE IN THE LOCAL COM
#========================================================================================
res_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox\\"
label2 = label.replace("'", "")
filename = "coldtube_panel2" + "_" + label2.lower() + ".csv"
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

print "*** Exporting ..."
influx_command = "influx -precision 'rfc3339' -database 'everything' -execute \"select value," +\
name_var + " from chaos where " + name_var +  " = " + sensor_name + " and label = " + label +\
" and location = " + location  + "\" " + "-format 'csv'>" + " '" + filename + "'"

stdin, stdout, stderr = client.exec_command(influx_command)
for line in stderr:
    print('... ' + line.strip('\n'))

print "*** Exported ...", filename
print "*** Downloading ..."
orig_dir = "/home/chaos/"
orig_filepath = orig_dir + filename
res_filepath = os.path.join(res_dir, filename)
ftp_client.get(orig_filepath, res_filepath)
print "*** Downloaded ..."
print "*** Deleting File on Server ..."
#ONCE YOU HAVE DOWNLOADED THE FILE DELTE THE FILE GENERATED ON THE SERVER
rm_command = "rm " + filename
stdin2, stdout2, stderr2 = client.exec_command(rm_command)
print "*** Deleted..."

ftp_client.close()        
client.close()
print "*** Disconnected..."