# 🎮 JADE Robotic Arm - Game Controller Interface

Interactive game-like control interface for the JADE robotic arm with real-time webcam feed.

![Interface Preview](docs/interface_preview.png)

## Features

- 🎮 **Game-style keyboard controls** - Intuitive QWEASD keys
- 📹 **Live webcam feed** - Monitor arm operations in real-time
- 📊 **Visual servo feedback** - Color-coded progress bars for each servo
- 🎯 **Smooth control** - Rate-limited movements for precision
- ⚡ **Real-time updates** - 60 FPS interface refresh
- 🔄 **Quick reset** - Press SPACE to reset all servos to 90°

## Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│  CAMERA VIEW              │  SERVO CONTROLS                 │
│  ┌──────────────────────┐ │  ┌─────────────────────────┐   │
│  │                      │ │  │ 0: Base (Yaw)    90°    │   │
│  │  Live Webcam Feed    │ │  │ [████████░░░░░░░░░░░░]  │   │
│  │  640x480             │ │  │                          │   │
│  │                      │ │  │ 1: Shoulder      75°    │   │
│  │                      │ │  │ [██████░░░░░░░░░░░░░░]  │   │
│  │                      │ │  │                          │   │
│  └──────────────────────┘ │  │ 2: Elbow         120°   │   │
│                            │  │ [████████████░░░░░░░░]  │   │
│                            │  │                          │   │
│                            │  │ 3: Wrist         60°    │   │
│                            │  │ [████░░░░░░░░░░░░░░░░]  │   │
│                            │  │                          │   │
│                            │  │ 4: Gripper       45°    │   │
│                            │  │ [██░░░░░░░░░░░░░░░░░░]  │   │
│                            │  └─────────────────────────┘   │
├────────────────────────────────────────────────────────────┤
│  CONTROLS                                                   │
│  Q/A: Base    W/S: Shoulder    E/D: Elbow                  │
│  R/F: Wrist   T/G: Gripper     SPACE: Reset All            │
│  ESC: Exit                                                  │
├────────────────────────────────────────────────────────────┤
│  ✓ Connected: /dev/ttyACM0            FPS: 60              │
└────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd robot_arm
pip install -r requirements.txt
```

### 2. Upload Arduino Code

Open `arduino/arm_controller_game.ino` in Arduino IDE and upload to your board.

**Important**: Use `arm_controller_game.ino` (not the original `arm_controller.ino`) for game controller compatibility.

### 3. Configure Serial Port

Edit `arm_control_game.py` and set your serial port:

```python
# Line 12
SERIAL_PORT = '/dev/ttyACM0'  # Linux/macOS
# or
SERIAL_PORT = 'COM3'          # Windows
```

### 4. Connect Webcam

Plug in your USB webcam. To use a different camera:

```python
# Line 327
webcam = WebcamFeed(camera_id=0)  # Change to 1, 2, etc.
```

### 5. Run the Controller

```bash
python arm_control_game.py
```

## Controls

### Keyboard Mapping

| Key | Servo | Action |
|-----|-------|--------|
| **Q** | Base (Yaw) | Increase angle (+10°) |
| **A** | Base (Yaw) | Decrease angle (-10°) |
| **W** | Shoulder | Increase angle (+10°) |
| **S** | Shoulder | Decrease angle (-10°) |
| **E** | Elbow | Increase angle (+10°) |
| **D** | Elbow | Decrease angle (-10°) |
| **R** | Wrist | Increase angle (+10°) |
| **F** | Wrist | Decrease angle (-10°) |
| **T** | Gripper | Open (+10°) |
| **G** | Gripper | Close (-10°) |
| **SPACE** | All Servos | Reset to 90° |
| **ESC** | - | Exit program |

### Tips for Smooth Control

1. **Hold keys** for continuous movement
2. **Tap keys** for precise positioning
3. **Use SPACE** to return to safe position
4. **Watch the target markers** (yellow lines) on progress bars

## Hardware Setup

### Required Components

- Arduino Uno/Nano or compatible
- 5x Servo motors (SG90 or similar)
- USB Webcam
- 5V power supply for servos (separate from Arduino)

### Wiring Diagram

```
Arduino     Servo
Pin 7   →   Base (Servo 0)
Pin 3   →   Shoulder (Servo 1)
Pin 4   →   Elbow (Servo 2)
Pin 5   →   Wrist (Servo 3)
Pin 6   →   Gripper (Servo 4)

Ground  →   All servo grounds + power supply ground
5V Ext  →   All servo power (DO NOT use Arduino 5V for all servos)
```

⚠️ **Important**: Power servos from external 5V supply, not Arduino!

## Serial Communication Protocol

The system uses a simple text-based serial protocol for communication between Python and Arduino.

### Command Format

```
servo_id:angle;\n
```

**Examples**:
- `0:90;` - Set servo 0 (Base) to 90 degrees
- `1:45;` - Set servo 1 (Shoulder) to 45 degrees
- `4:180;` - Set servo 4 (Gripper) to 180 degrees (fully open)

### Response Format

Arduino sends confirmation messages:
```
OK: Servo 0 -> 90
OK: Servo 1 -> 45
```

Or error messages:
```
ERROR: Invalid servo ID: 5
ERROR: Invalid angle: 200
```

### Keyboard Commands

Single character commands are also supported for manual control via Serial Monitor:
- `q`/`a` - Base increase/decrease
- `w`/`s` - Shoulder increase/decrease
- `e`/`d` - Elbow increase/decrease
- `r`/`f` - Wrist increase/decrease
- `t`/`g` - Gripper increase/decrease

### Python → Arduino Flow

```python
# Python sends
command = f"{servo_id}:{angle};\n"
serial_conn.write(command.encode('ascii'))

# Arduino receives
# Parses: "0:90;"
# Extracts: servo_id=0, angle=90
# Executes: servos[0].write(90)
# Responds: "OK: Servo 0 -> 90"
```

## Configuration

### Customizing Servo Settings

Edit `arm_control_game.py`:

```python
# Number of servos (line 18)
NUM_SERVOS = 5

# Servo names (line 19)
SERVO_NAMES = ['Base (Yaw)', 'Shoulder', 'Elbow', 'Wrist', 'Gripper']

# Servo colors (line 20)
SERVO_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
]
```

### Adjusting Movement Speed

```python
# Line 179 - Update rate (lower = faster)
if key not in self.last_key_time or current_time - self.last_key_time[key] > 0.1:
    # Change 0.1 to 0.05 for faster, 0.2 for slower
```

### Changing Camera Resolution

```python
# Lines 14-15
CAMERA_WIDTH = 640   # Increase for better quality
CAMERA_HEIGHT = 480  # Decrease for better performance
```

## Troubleshooting

### Camera Not Working

```python
# Try different camera indices
webcam = WebcamFeed(camera_id=1)  # or 2, 3, etc.

# Check available cameras
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
```

### Serial Connection Failed

1. **Check port**: Run `ls /dev/tty*` (Linux/Mac) or check Device Manager (Windows)
2. **Check permissions**: `sudo chmod 666 /dev/ttyACM0` (Linux)
3. **Close other programs**: Arduino IDE Serial Monitor conflicts
4. **Try different port**: Edit `SERIAL_PORT` in code

### Servos Not Moving

1. **Check Arduino upload**: Verify firmware uploaded successfully
2. **Check wiring**: Ensure all connections are secure
3. **Check power**: Servos need external 5V supply
4. **Check serial**: Look for "✓ Connected" in status bar

### Low FPS

1. **Lower camera resolution** (320x240)
2. **Reduce servo update rate**
3. **Close other programs**
4. **Check CPU usage**

## Advanced Features

### Custom Presets

Add preset positions to the code:

```python
# In GameInterface class, add to handle_events:
elif event.key == pygame.K_1:  # Preset 1: Home position
    for i in range(NUM_SERVOS):
        self.controller.set_position(i, [90, 90, 90, 90, 45][i])

elif event.key == pygame.K_2:  # Preset 2: Reach position
    for i in range(NUM_SERVOS):
        self.controller.set_position(i, [90, 45, 135, 90, 90][i])
```

### Recording Movements

Add to controller class:

```python
# Record movements
self.recorded_moves = []

def record_position(self):
    self.recorded_moves.append(self.servo_angles.copy())

def playback(self):
    for position in self.recorded_moves:
        for i, angle in enumerate(position):
            self.set_position(i, angle)
        time.sleep(0.5)
```

### Adding More Servos

1. Update `NUM_SERVOS` 
2. Add to `SERVO_NAMES`
3. Add to `SERVO_COLORS`
4. Add key mappings
5. Update Arduino code with additional pins

## Architecture

```
┌─────────────────────────────────────┐
│     GameInterface (Pygame)          │
│  - Rendering                        │
│  - Event Handling                   │
│  - Display Management               │
└─────────────┬───────────────────────┘
              │
              ├──────────┬─────────────┐
              ▼          ▼             ▼
    ┌─────────────┐  ┌────────┐  ┌──────────┐
    │ Controller  │  │Webcam  │  │ Arduino  │
    │  - Serial   │  │- CV2   │  │ - Servos │
    │  - Commands │  │- Thread│  │ - USB    │
    └─────────────┘  └────────┘  └──────────┘
```

## Performance

- **Rendering**: 60 FPS
- **Webcam**: ~30 FPS
- **Serial**: 10 updates/sec per servo
- **Latency**: <100ms end-to-end
- **CPU Usage**: ~15-25%

## Future Enhancements

- [ ] Inverse kinematics integration
- [ ] Predefined motion sequences
- [ ] Recording and playback
- [ ] Multiple camera views
- [ ] Joystick/gamepad support
- [ ] Network control (websockets)
- [ ] AR overlay on camera feed
- [ ] Voice commands

## License

MIT License - See main project LICENSE file

## Credits

Part of the JADE Autonomous Satellite Servicing System
