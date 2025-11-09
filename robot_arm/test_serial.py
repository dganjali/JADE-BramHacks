#!/usr/bin/env python3
"""
Serial communication test for JADE Robotic Arm
Tests the serial protocol without the full game interface
"""

import serial
import time
import sys

SERIAL_PORT = '/dev/ttyACM0'  # Change to your port
BAUD_RATE = 9600

def test_serial():
    """Test serial communication with Arduino"""
    
    print("=" * 60)
    print("JADE Arm - Serial Communication Test")
    print("=" * 60)
    
    # Connect to Arduino
    try:
        print(f"\n[1/3] Connecting to {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        print("✓ Connected!")
        
        # Read startup message
        while ser.in_waiting:
            line = ser.readline().decode('ascii').strip()
            print(f"  Arduino: {line}")
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nTips:")
        print("  - Check the serial port (ls /dev/tty* on Linux/Mac)")
        print("  - Close Arduino IDE Serial Monitor")
        print("  - Try: sudo chmod 666 /dev/ttyACM0")
        return False
    
    # Test servo commands
    print("\n[2/3] Testing servo commands...")
    test_commands = [
        (0, 90, "Base to center"),
        (1, 45, "Shoulder to 45°"),
        (2, 135, "Elbow to 135°"),
        (3, 60, "Wrist to 60°"),
        (4, 90, "Gripper to center"),
    ]
    
    for servo_id, angle, description in test_commands:
        command = f"{servo_id}:{angle};\n"
        print(f"\n  Sending: {command.strip()} ({description})")
        ser.write(command.encode('ascii'))
        ser.flush()
        time.sleep(0.5)
        
        # Read response
        if ser.in_waiting:
            response = ser.readline().decode('ascii').strip()
            print(f"  Response: {response}")
            
            if "OK" in response:
                print("  ✓ Success")
            else:
                print("  ✗ Unexpected response")
        else:
            print("  ⚠ No response from Arduino")
    
    # Test sweep pattern
    print("\n[3/3] Testing sweep pattern...")
    print("  Sweeping servo 0 from 0° to 180° and back...")
    
    # Sweep up
    for angle in range(0, 181, 10):
        command = f"0:{angle};\n"
        ser.write(command.encode('ascii'))
        ser.flush()
        print(f"  Position: {angle}°", end='\r')
        time.sleep(0.1)
    
    print("\n  Sweeping back to center...")
    # Sweep down
    for angle in range(180, 89, -10):
        command = f"0:{angle};\n"
        ser.write(command.encode('ascii'))
        ser.flush()
        print(f"  Position: {angle}°", end='\r')
        time.sleep(0.1)
    
    print("\n  ✓ Sweep complete!")
    
    # Return to neutral
    print("\n  Returning all servos to 90°...")
    for servo_id in range(5):
        command = f"{servo_id}:90;\n"
        ser.write(command.encode('ascii'))
        ser.flush()
        time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("✓ All tests complete!")
    print("=" * 60)
    
    ser.close()
    return True

def main():
    try:
        success = test_serial()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
