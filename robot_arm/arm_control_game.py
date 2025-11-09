"""
JADE Robotic Arm - Interactive Control Interface
Real-time keyboard control with webcam feed
"""

import pygame
import cv2
import serial
import sys
import time
from threading import Thread, Lock
import numpy as np

# Configuration
SERIAL_PORT = '/dev/ttyACM0'  # Change to your Arduino port (COM3 on Windows)
BAUD_RATE = 9600
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 60

# Servo configuration
NUM_SERVOS = 5
SERVO_NAMES = ['Base (Yaw)', 'Shoulder', 'Elbow', 'Wrist', 'Gripper']
SERVO_COLORS = [
    (255, 100, 100),  # Base - Red
    (100, 255, 100),  # Shoulder - Green
    (100, 100, 255),  # Elbow - Blue
    (255, 255, 100),  # Wrist - Yellow
    (255, 100, 255),  # Gripper - Magenta
]

# Key mappings (same as Arduino)
KEY_MAPPINGS = {
    pygame.K_q: (0, 10),   # Base +
    pygame.K_a: (0, -10),  # Base -
    pygame.K_w: (1, 10),   # Shoulder +
    pygame.K_s: (1, -10),  # Shoulder -
    pygame.K_e: (2, 10),   # Elbow +
    pygame.K_d: (2, -10),  # Elbow -
    pygame.K_r: (3, 10),   # Wrist +
    pygame.K_f: (3, -10),  # Wrist -
    pygame.K_t: (4, 10),   # Gripper +
    pygame.K_g: (4, -10),  # Gripper -
}


class RobotArmController:
    """Main controller for the robotic arm"""
    
    def __init__(self, serial_port, baud_rate):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.servo_angles = [90] * NUM_SERVOS  # Start at middle position
        self.target_angles = [90] * NUM_SERVOS
        self.serial_lock = Lock()
        self.connected = False
        
    def connect(self):
        """Connect to Arduino"""
        try:
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"✓ Connected to Arduino on {self.serial_port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Arduino: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial_conn:
            self.serial_conn.close()
            self.connected = False
    
    def move_servo(self, servo_id, delta):
        """Move a servo by delta amount"""
        if 0 <= servo_id < NUM_SERVOS:
            new_angle = max(0, min(180, self.target_angles[servo_id] + delta))
            self.target_angles[servo_id] = new_angle
            self.send_command(servo_id, new_angle)
    
    def send_command(self, servo_id, angle):
        """Send command to Arduino via serial"""
        if not self.connected or not self.serial_conn:
            return
        
        try:
            with self.serial_lock:
                # Send command as "servo_id:angle;" format
                # Example: "0:90;" to set servo 0 to 90 degrees
                command = f"{servo_id}:{angle};\n"
                self.serial_conn.write(command.encode('ascii'))
                self.serial_conn.flush()
                self.servo_angles[servo_id] = angle
        except Exception as e:
            print(f"✗ Serial error: {e}")
    
    def set_position(self, servo_id, angle):
        """Set servo to specific angle"""
        if 0 <= servo_id < NUM_SERVOS:
            angle = max(0, min(180, angle))
            self.target_angles[servo_id] = angle
            self.send_command(servo_id, angle)


class WebcamFeed:
    """Handle webcam capture and display"""
    
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = Lock()
        self.thread = None
        
    def start(self):
        """Start webcam capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            if not self.cap.isOpened():
                print("✗ Failed to open webcam")
                return False
            
            self.running = True
            self.thread = Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            print("✓ Webcam started")
            return True
        except Exception as e:
            print(f"✗ Webcam error: {e}")
            return False
    
    def _capture_loop(self):
        """Continuous capture loop"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            time.sleep(0.03)  # ~30 FPS
    
    def get_frame(self):
        """Get latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        """Stop webcam"""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()


class GameInterface:
    """Pygame-based game interface"""
    
    def __init__(self, controller, webcam):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("JADE Robotic Arm Control")
        self.clock = pygame.time.Clock()
        self.controller = controller
        self.webcam = webcam
        self.running = True
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Key states
        self.keys_pressed = set()
        self.last_key_time = {}
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Reset all servos to 90 degrees
                    for i in range(NUM_SERVOS):
                        self.controller.set_position(i, 90)
                elif event.key in KEY_MAPPINGS:
                    self.keys_pressed.add(event.key)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.discard(event.key)
    
    def update(self):
        """Update game state"""
        current_time = time.time()
        
        # Process held keys with rate limiting
        for key in self.keys_pressed:
            if key in KEY_MAPPINGS:
                # Rate limit to 10 updates per second per key
                if key not in self.last_key_time or current_time - self.last_key_time[key] > 0.1:
                    servo_id, delta = KEY_MAPPINGS[key]
                    self.controller.move_servo(servo_id, delta)
                    self.last_key_time[key] = current_time
    
    def render(self):
        """Render the interface"""
        self.screen.fill((20, 20, 30))  # Dark background
        
        # Draw webcam feed
        self.draw_webcam()
        
        # Draw servo controls
        self.draw_servo_panel()
        
        # Draw controls help
        self.draw_controls_help()
        
        # Draw status bar
        self.draw_status_bar()
        
        pygame.display.flip()
    
    def draw_webcam(self):
        """Draw webcam feed"""
        frame = self.webcam.get_frame()
        
        # Position on left side
        x, y = 20, 20
        width, height = 640, 480
        
        if frame is not None:
            # Convert to pygame surface
            frame_resized = cv2.resize(frame, (width, height))
            surface = pygame.surfarray.make_surface(np.transpose(frame_resized, (1, 0, 2)))
            self.screen.blit(surface, (x, y))
        else:
            # Draw placeholder
            pygame.draw.rect(self.screen, (40, 40, 50), (x, y, width, height))
            text = self.font_medium.render("No Camera Feed", True, (150, 150, 150))
            text_rect = text.get_rect(center=(x + width//2, y + height//2))
            self.screen.blit(text, text_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (100, 100, 255), (x, y, width, height), 2)
        
        # Title
        title = self.font_medium.render("CAMERA VIEW", True, (100, 200, 255))
        self.screen.blit(title, (x + 10, y - 35))
    
    def draw_servo_panel(self):
        """Draw servo control panel"""
        x, y = 680, 20
        panel_width = 580
        panel_height = 480
        
        # Background panel
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 255), (x, y, panel_width, panel_height), 2)
        
        # Title
        title = self.font_medium.render("SERVO CONTROLS", True, (100, 200, 255))
        self.screen.blit(title, (x + 10, y - 35))
        
        # Draw each servo
        servo_y = y + 20
        servo_spacing = 85
        
        for i in range(NUM_SERVOS):
            self.draw_servo_control(x + 20, servo_y + i * servo_spacing, i)
    
    def draw_servo_control(self, x, y, servo_id):
        """Draw individual servo control"""
        angle = self.controller.servo_angles[servo_id]
        target = self.controller.target_angles[servo_id]
        color = SERVO_COLORS[servo_id]
        
        # Servo name
        name_text = self.font_small.render(f"{servo_id}: {SERVO_NAMES[servo_id]}", True, color)
        self.screen.blit(name_text, (x, y))
        
        # Angle display
        angle_text = self.font_medium.render(f"{angle}°", True, (255, 255, 255))
        self.screen.blit(angle_text, (x + 250, y - 5))
        
        # Progress bar (0-180 degrees)
        bar_x = x
        bar_y = y + 30
        bar_width = 500
        bar_height = 25
        
        # Background
        pygame.draw.rect(self.screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill based on angle
        fill_width = int((angle / 180.0) * bar_width)
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Target marker
        target_x = bar_x + int((target / 180.0) * bar_width)
        pygame.draw.line(self.screen, (255, 255, 0), 
                        (target_x, bar_y), (target_x, bar_y + bar_height), 3)
        
        # Min/Max labels
        min_text = self.font_small.render("0°", True, (150, 150, 150))
        max_text = self.font_small.render("180°", True, (150, 150, 150))
        self.screen.blit(min_text, (bar_x - 5, bar_y + 30))
        self.screen.blit(max_text, (bar_x + bar_width - 25, bar_y + 30))
    
    def draw_controls_help(self):
        """Draw control instructions"""
        x, y = 20, 520
        width = 1240
        height = 150
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, width, height))
        pygame.draw.rect(self.screen, (100, 100, 255), (x, y, width, height), 2)
        
        # Title
        title = self.font_medium.render("CONTROLS", True, (100, 200, 255))
        self.screen.blit(title, (x + 10, y - 35))
        
        # Control mappings
        controls = [
            ("Q/A: Base", "W/S: Shoulder", "E/D: Elbow"),
            ("R/F: Wrist", "T/G: Gripper", "SPACE: Reset All"),
            ("ESC: Exit", "", "")
        ]
        
        text_y = y + 20
        for row in controls:
            text_x = x + 30
            for ctrl in row:
                if ctrl:
                    text = self.font_small.render(ctrl, True, (200, 200, 200))
                    self.screen.blit(text, (text_x, text_y))
                text_x += 400
            text_y += 35
    
    def draw_status_bar(self):
        """Draw status bar at bottom"""
        y = WINDOW_HEIGHT - 40
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 30), (0, y, WINDOW_WIDTH, 40))
        pygame.draw.rect(self.screen, (100, 100, 255), (0, y, WINDOW_WIDTH, 2))
        
        # Connection status
        if self.controller.connected:
            status_text = f"✓ Connected: {self.controller.serial_port}"
            color = (100, 255, 100)
        else:
            status_text = "✗ Not Connected"
            color = (255, 100, 100)
        
        text = self.font_small.render(status_text, True, color)
        self.screen.blit(text, (20, y + 10))
        
        # FPS counter
        fps_text = self.font_small.render(f"FPS: {int(self.clock.get_fps())}", True, (200, 200, 200))
        self.screen.blit(fps_text, (WINDOW_WIDTH - 100, y + 10))


def main():
    """Main entry point"""
    print("=" * 60)
    print("JADE Robotic Arm - Interactive Control Interface")
    print("=" * 60)
    
    # Initialize controller
    print("\n[1/3] Initializing Arduino connection...")
    controller = RobotArmController(SERIAL_PORT, BAUD_RATE)
    
    # Try to connect (non-blocking if fails)
    controller.connect()
    
    # Initialize webcam
    print("\n[2/3] Starting webcam...")
    webcam = WebcamFeed(camera_id=0)
    webcam.start()
    
    # Initialize game interface
    print("\n[3/3] Launching interface...")
    print("\n" + "=" * 60)
    print("Interface ready! Use keyboard to control the arm.")
    print("=" * 60 + "\n")
    
    game = GameInterface(controller, webcam)
    
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        # Cleanup
        webcam.stop()
        controller.disconnect()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()
