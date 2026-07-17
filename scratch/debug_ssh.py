import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.133', username='root', password='recalboxroot')

print("--- Script Contents ---")
stdin, stdout, stderr = ssh.exec_command('cat /recalbox/share/userscripts/arcadematrix_mqtt.sh')
print(stdout.read().decode())

print("--- Manual Execution Output ---")
stdin, stdout, stderr = ssh.exec_command('sh /recalbox/share/userscripts/arcadematrix_mqtt.sh -action rungame -statefile /tmp/test')
print(stdout.read().decode())
print("ERRORS:", stderr.read().decode())

ssh.close()
