#2023-12-21  检测是否能获取snmp信息，用于测试，需要手动输入ip地址和community信息
import subprocess

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
  # Get the IP address and community string from the user.
  ip_address = input("Enter the IP address of the device: ")
  community_string = input("Enter the community string to use: ")

  # Check if SNMP is enabled.
  snmp_enabled = snmp_check(ip_address, community_string)

  # Print the result.
  if snmp_enabled:
    print("SNMP is enabled on the device.")
  else:
    print("SNMP is not enabled on the device.")
