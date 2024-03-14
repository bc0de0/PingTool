import socket
import struct
import time


def icmp_packet(seq_number, ttl):
    # ICMP header format: type (8 bits), code (8 bits), checksum (16 bits), id (16 bits), sequence (16 bits)
    icmp_type = 8  # ICMP echo request type
    icmp_code = 0
    icmp_checksum = 0
    icmp_id = 12345  # Arbitrary identifier

    # Convert sequence number to 16-bit unsigned integer
    seq_number = struct.pack("!H", seq_number)

    # Calculate ICMP header checksum
    icmp_header = struct.pack("!BBHH", icmp_type, icmp_code, icmp_checksum, icmp_id) + seq_number
    icmp_checksum = calculate_checksum(icmp_header)

    # Build the ICMP packet with correct checksum
    icmp_packet = struct.pack("!BBHH", icmp_type, icmp_code, socket.htons(icmp_checksum), icmp_id) + seq_number

    return icmp_packet


def calculate_checksum(data):
    checksum = 0
    # Sum up 16-bit chunks of the data
    for i in range(0, len(data), 2):
        checksum += (data[i] << 8) + (data[i + 1])
    # Add the carry
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    # Return the one's complement of the sum
    return socket.htons(~checksum & 0xFFFF)


def ping(destination, count=4, timeout=2, ttl=64):
    try:
        # Resolve hostname to IP address
        ip_address = socket.gethostbyname(destination)
        print(f"Pinging {destination} [{ip_address}] with TTL={ttl}:")

        # Create a raw socket
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # Set the TTL value in the IP header
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        for seq_number in range(1, count + 1):
            # Build the ICMP echo request packet
            icmp_packet_data = icmp_packet(seq_number, ttl)

            # Send the packet to the destination
            icmp_socket.sendto(icmp_packet_data, (ip_address, 0))

            # Record the time before sending the packet
            send_time = time.time()

            # Receive the ICMP echo reply packet
            icmp_socket.settimeout(timeout)
            try:
                reply, _ = icmp_socket.recvfrom(1024)
                receive_time = time.time()
                print(
                    f"Reply from {ip_address}: bytes={len(reply)}, time={round((receive_time - send_time) * 1000, 2)}ms")
            except socket.timeout:
                print(f"Request timed out for seq {seq_number}")

        # Close the socket
        icmp_socket.close()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    destination = "yahoo.com"  # Change this to the target host
    ping(destination)


