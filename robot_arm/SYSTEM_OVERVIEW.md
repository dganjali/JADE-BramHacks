# JADE Robotic Arm - Complete System Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐           ┌──────────────────────┐    │
│  │  Game Controller    │           │   Main Application   │    │
│  │  (arm_control_      │           │   (main.py)          │    │
│  │   game.py)          │           │                      │    │
│  │                     │           │   - IK Solver        │    │
│  │  - Pygame UI        │           │   - Vision System    │    │
│  │  - Webcam Feed      │           │   - Path Planning    │    │
│  │  - Keyboard Input   │           │   - Autonomous Mode  │    │
│  └──────────┬──────────┘           └──────────┬───────────┘    │
│             │                                  │                 │
└─────────────┼──────────────────────────────────┼─────────────────┘
              │                                  │
              │         Serial Protocol          │
              │      (servo_id:angle;)           │
              │                                  │
┌─────────────┴──────────────────────────────────┴─────────────────┐
│                   COMMUNICATION LAYER                             │
│                                                                   │
│              USB Serial (9600 baud, 8N1)                         │
│              Format: "0:90;" or keyboard chars                    │
│                                                                   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
┌───────────────────────────────┴───────────────────────────────────┐
│                      ARDUINO FIRMWARE                             │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  arm_controller_game.ino                                  │   │
│  │                                                           │   │
│  │  - Serial Parser (handles both formats)                  │   │
│  │  - Keyboard Command Handler (q/a, w/s, etc.)            │   │
│  │  - Serial Command Handler (servo_id:angle;)              │   │
│  │  - Servo Control (write angles, manage 5 servos)         │   │
│  │  - Error Handling (validate commands)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────┬─────┬─────┬─────┬─────┬───────────────────────────────────┘
      │     │     │     │     │
┌─────┴─────┴─────┴─────┴─────┴───────────────────────────────────┐
│                    HARDWARE LAYER                                 │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Pin 7 → Servo 0 (Base/Yaw)      - 0° to 180°                   │
│  Pin 3 → Servo 1 (Shoulder)      - 0° to 180°                   │
│  Pin 4 → Servo 2 (Elbow)         - 0° to 180°                   │
│  Pin 5 → Servo 3 (Wrist)         - 0° to 180°                   │
│  Pin 6 → Servo 4 (Gripper)       - 0° to 180°                   │
│                                                                   │
│  External 5V Power Supply (2-3A for 5 servos)                   │
│  Common Ground (Arduino + Servos + Power)                        │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Game Controller Mode

```
User Presses Key (e.g., 'Q')
         ↓
Pygame Event Handler
         ↓
Update Target Angle (+10°)
         ↓
Format Serial Command ("0:90;\n")
         ↓
Send via pyserial
         ↓
Arduino Receives
         ↓
Parse Command (servo=0, angle=90)
         ↓
Validate (0≤id<5, 0≤angle≤180)
         ↓
Set Servo Position
         ↓
Send Confirmation ("OK: Servo 0 -> 90")
         ↓
Update UI Display
```

### Autonomous Mode

```
Vision System Detects Object
         ↓
Calculate 3D Position
         ↓
Inverse Kinematics Solver
         ↓
Generate Joint Angles
         ↓
Path Planning (smooth trajectory)
         ↓
For each waypoint:
    Format Serial Commands
    Send to Arduino
    Wait for confirmation
         ↓
Execute Gripper Action
```

## Serial Protocol Details

### Command Types

| Type | Format | Example | Description |
|------|--------|---------|-------------|
| Servo Command | `id:angle;` | `0:90;` | Set servo 0 to 90° |
| Keyboard Up | `q,w,e,r,t` | `q` | Increase servo angle |
| Keyboard Down | `a,s,d,f,g` | `a` | Decrease servo angle |

### Response Types

| Type | Format | Example | Meaning |
|------|--------|---------|---------|
| Success | `OK: ...` | `OK: Servo 0 -> 90` | Command executed |
| Error | `ERROR: ...` | `ERROR: Invalid servo ID: 5` | Command failed |

### Timing

- **Baud Rate**: 9600 bps
- **Command Rate**: Up to 10 Hz per servo (100ms between commands)
- **Response Time**: <10ms typical
- **USB Latency**: ~1-5ms
- **Total Latency**: <20ms end-to-end

## File Structure

```
robot_arm/
├── arm_control_game.py          # Game controller interface ⭐ NEW
├── test_serial.py               # Serial communication tester ⭐ NEW
├── main.py                      # Main autonomous application
├── config.py                    # Hardware configuration
├── requirements.txt             # Python dependencies (updated)
│
├── arduino/
│   ├── arm_controller_game.ino  # Game-compatible firmware ⭐ NEW
│   └── arm_controller.ino       # Original firmware
│
├── vision/
│   ├── tracker.py               # Object tracking
│   └── depth.py                 # Depth estimation
│
├── planning/
│   ├── kinematics.py            # IK solver
│   └── trajectory.py            # Path planning
│
├── control/
│   ├── arm_control.py           # High-level control
│   └── serial_comm.py           # Serial communication
│
├── tests/
│   └── test_ik.py              # Unit tests
│
└── docs/
    ├── GAME_CONTROLLER.md       # Game controller guide ⭐ NEW
    └── README.md                # This file
```

## Quick Start Guide

### For Game Controller (Manual Control)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Upload Arduino firmware
# Open arduino/arm_controller_game.ino in Arduino IDE
# Upload to board

# 3. Test serial connection
python test_serial.py

# 4. Launch game controller
python arm_control_game.py
```

### For Autonomous Operation

```bash
# 1. Configure hardware
# Edit config.py with your measurements

# 2. Upload Arduino firmware
# Use either arm_controller.ino or arm_controller_game.ino

# 3. Test components
python tests/test_ik.py

# 4. Run main application
python main.py
```

## Troubleshooting

### Serial Connection Issues

**Problem**: `Failed to connect to Arduino`

**Solutions**:
```bash
# Linux: Check permissions
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM0

# Find correct port
ls /dev/tty*    # Linux/Mac
# or check Device Manager on Windows

# Close conflicting programs
# - Arduino IDE Serial Monitor
# - Other serial terminals
```

### Servo Not Moving

**Problem**: Commands sent but servo doesn't move

**Checks**:
1. **Power**: External 5V supply connected?
2. **Wiring**: Signal, power, ground all connected?
3. **Pin**: Correct pin number in Arduino code?
4. **Angle**: Valid range (0-180)?
5. **Servo**: Test with Arduino example sketch

### Webcam Not Detected

**Problem**: "No Camera Feed" in game controller

**Solutions**:
```python
# Try different camera IDs
webcam = WebcamFeed(camera_id=1)  # or 2, 3, etc.

# List available cameras
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
```

### Slow Performance

**Problem**: Low FPS or lag

**Solutions**:
1. Lower camera resolution (320x240)
2. Reduce servo update rate
3. Close other applications
4. Use faster computer or RPi 4+

## Hardware Recommendations

### Tested Servos
- ✅ SG90 (9g micro servo) - Budget option
- ✅ MG90S (metal gear) - Better durability
- ✅ MG996R (high torque) - For larger arms

### Power Supply
- 5V 2-3A for 5x SG90 servos
- 5V 5A for 5x MG996R servos
- Separate from Arduino power!

### Webcam
- Any USB webcam (640x480 or higher)
- Logitech C270/C920 recommended
- Higher FPS = smoother tracking

## Next Steps

1. ✅ Test serial communication
2. ✅ Run game controller
3. 🔄 Calibrate servo ranges
4. 🔄 Tune IK solver
5. 🔄 Train vision models
6. 🔄 Integrate with Gazebo simulation
7. 🔄 Deploy to real hardware

## Support

For issues or questions:
- Check [GAME_CONTROLLER.md](GAME_CONTROLLER.md) for game controller specific help
- Review [main README](../README.md) for overall system documentation
- Test with `test_serial.py` to isolate serial issues
- Verify Arduino firmware uploaded correctly

