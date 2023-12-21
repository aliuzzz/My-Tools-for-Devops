#准备一个ip.txt表，用于批量测试。会将snmp通的输出到snmp_enabled.txt,不通的输出到snmp_disabled.txt
import subprocess
import os

def snmp_check(ip_address, community_string):
  # Construct the SNMP walk command.
  command = ['snmpwalk', '-v', '2c', '-c', community_string, ip_address, '1.3.6.1.2.1.1.1.0']

  # Execute the command and capture the output.
  try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    # If the command failed, it means SNMP is not enabled.
    return False

  # Check if the output contains any information.
  if output.strip():
    # If there is output, it means SNMP is enabled.
    return True
  else:
    # If there is no output, it means SNMP is not enabled.
    return False


if __name__ == "__main__":
  # Get the community string from the user.
  community_string = input("Enter the community string to use: ")

  # Read the IP addresses from the ip.txt file.
  with open('ip.txt', 'r') as f:
    ip_addresses = f.readlines()

  # Open two files for writing: one for SNMP enabled devices and one for SNMP disabled devices.
  with open('snmp_enabled.txt', 'w') as f_enabled, open('snmp_disabled.txt', 'w') as f_disabled:
    # Check SNMP for each IP address.
    for ip_address in ip_addresses:
      # Remove any whitespace from the IP address.
      ip_address = ip_address.strip()

      # Check if SNMP is enabled on the device.
      snmp_enabled = snmp_check(ip_address, community_string)

      # Write the IP address to the appropriate file.
      if snmp_enabled:
        f_enabled.write(f"{ip_address}\n")
      else:
        f_disabled.write(f"{ip_address}\n")

  # Print a message to the user.
  print("SNMP enabled devices have been written to snmp_enabled.txt.")
  print("SNMP disabled devices have been written to snmp_disabled.txt.")

