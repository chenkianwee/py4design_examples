import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.WarningPolicy())
print("*** Connecting...")

client.connect('chaosbox.princeton.edu',username="chaos", password='Zer0exergy')
"""
stdin, stdout, stderr = client.exec_command('ls')
for line in stdout:
    print('... ' + line.strip('\n'))


"""
ftp_client=client.open_sftp()
dest_filepath = 'F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox\\coldtube_ct_ph19_surfacet.csv'
ftp_client.get('/home/chaos/coldtube_ct_ph19_surfacet.csv',dest_filepath)
ftp_client.close()
client.close()