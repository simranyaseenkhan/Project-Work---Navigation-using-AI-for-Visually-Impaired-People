import cv2
import numpy as np
import torch
import time
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import win32com.client
import speech_recognition as sr
import threading
from datetime import datetime
import webbrowser
import sys
import requests
import smtplib
from email.mime.text import MIMEText
import pyttsx3
from collections import defaultdict

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model.eval()

# Time and Date Class
class TimeDate:
    def get_current_time_date(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %d %B %Y")
        return f"The current time is {current_time}, and today's date is {current_date}."

# Map Navigation Class
class MapNavigation:
    def navigate_to(self, destination):
        if destination:
            url = f"https://www.google.com/maps/dir/?api=1&destination={destination}"
            webbrowser.open(url)
            return f"Opening map to {destination}. Please check your browser."
        return "Please specify a valid destination for navigation."

# Weather Class for Dandeli
class Weather:
    def get_dandeli_weather(self):
        try:
            # Using Open-Meteo API for reliable weather data
            latitude = 15.2667  # coordinates
            longitude = 74.6167
            
            # Make API request to get current weather
            url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                temperature = current.get('temperature', 'N/A')
                weathercode = current.get('weathercode', 'N/A')
                
                # Convert weather code to human-readable description
                weather_description = self._get_weather_description(weathercode)
                
                return f"Current weather is : {weather_description}, Temperature: {temperature}°C"
            else:
                return "Could not fetch weather data at this time"
        except Exception as e:
            return f"Weather service error: {str(e)}"
    
    def _get_weather_description(self, code):
        # Weather code interpretation from WMO
        weather_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_map.get(code, "Unknown weather conditions")

# Updated AlertSystem Class
class AlertSystem:
    def __init__(self):
        self.email_config = {
            'sender': 'ansarisimran7623@gmail.com',
            'password': 'seld gtue lrnl hdir',
            'recipients': [
                'simsimk143@gmail.com',
                'ravirajkhushi5@gmail.com',
                'keertikatavakar33@gmail.com',
                'simransari7623@gmail.com'
            ],
            'server': 'smtp.gmail.com',
            'port': 587
        }
        self.tts = pyttsx3.init()

class AlertSystem:
    def __init__(self):
        self.email_config = {
            'sender': 'ansarisimran7623@gmail.com',
            'password': 'seld gtue lrnl hdir',
            'recipients': [
                'simsimk143@gmail.com',
                'ravirajkhushi5@gmail.com',
                'keertikatavakar33@gmail.com',
                'simransari7623@gmail.com'
            ],
            'server': 'smtp.gmail.com',
            'port': 587
        }
        self.tts = pyttsx3.init()
        self.phone_number = "+91 1234567890"  # Replace with actual phone number
        self.live_location_link = "https://maps.app.goo.gl/yLZdK1ehvBoegcKC9"  # Your live location link

    def send_alert(self):
        """Send emergency email to multiple recipients with phone number and live location"""
        try:
            # Create HTML email with formatted content
            email_body = f"""
            <html>
                <body>
                    <h2 style="color: red;">🚨 EMERGENCY ALERT 🚨</h2>
                    <p><strong>I need immediate assistance!</strong></p>
                    
                    <h3>Contact Information:</h3>
                    <p>Phone Number: <a href="tel:{self.phone_number}">{self.phone_number}</a></p>
                    
                    <h3>Current Location:</h3>
                    <p><a href="{self.live_location_link}">Click here for live location</a></p>
                    <p>Or copy this link: {self.live_location_link}</p>
                    
                    <p><em>This is an automated alert sent from the Caring Assistant application.</em></p>
                </body>
            </html>
            """
            
            msg = MIMEText(email_body, 'html')
            msg['Subject'] = "🚨 EMERGENCY ALERT - IMMEDIATE ASSISTANCE REQUIRED"
            msg['From'] = self.email_config['sender']
            msg['To'] = ", ".join(self.email_config['recipients'])
            
            with smtplib.SMTP(self.email_config['server'], self.email_config['port']) as server:
                server.starttls()
                server.login(self.email_config['sender'], self.email_config['password'])
                server.sendmail(self.email_config['sender'], self.email_config['recipients'], msg.as_string())
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False

    def speak_alert(self, text):
        """Voice feedback for alerts"""
        self.tts.say(text)
        self.tts.runAndWait()

class RealTimeDetectionApp(App):
    def build(self):
        self.layout = BoxLayout()
        self.image = Image()
        self.layout.add_widget(self.image)
        
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Unable to open video source")
            return self.layout
        
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.speech_messages = []
        self.last_feedback_time = 0
        self.frame_counter = 0
        self.running = True
        self.describing_surroundings = False  # Flag to control description mode
        
        # Track detected objects over time
        self.object_tracker = defaultdict(lambda: {'first_detected': None, 'last_detected': None, 'warning_given': False})
        self.active_warnings = set()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        
        # Initialize utility classes
        self.time_date = TimeDate()
        self.map_navigation = MapNavigation()
        self.weather = Weather()
        self.alert_system = AlertSystem()
        
        # Start the voice command listener
        self.voice_command_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        self.voice_command_thread.start()
        
        # Initial greeting
        self.speak_feedback("Hello there! I'm your caring assistant. I'm here to help you navigate safely. How can I assist you today?")
        
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        Clock.schedule_interval(self.process_speech, 0.1)
        
        return self.layout

    def listen_for_commands(self):
        """Listen for voice commands in a separate thread."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                if not self.is_listening:
                    self.is_listening = True
                    try:
                        audio = self.recognizer.listen(source, timeout=5)
                        command = self.recognizer.recognize_google(audio).lower()
                        print(f"Detected command: {command}")
                        self.process_voice_command(command)
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        pass
                    except Exception as e:
                        print(f"Error in voice command listener: {e}")
                    self.is_listening = False

    def process_voice_command(self, command):
        """Process the detected voice command."""
        if "describe" in command or "surroundings" in command or "environment" in command and "surrounding" in command or "detection" in command:
            self.describing_surroundings = True
            self.speak_feedback("I'll now carefully describe your surroundings to help you navigate safely. Just say 'stop describing' whenever you'd like me to stop.")
        elif "stop describing" in command or "stop" in command:
            self.describing_surroundings = False
            self.speak_feedback("I've stopped describing your surroundings. Please let me know how else I can assist you.")
        elif "navigate to" in command:
            self.describing_surroundings = False
            destination = command.replace("navigate to", "").strip()
            response = self.map_navigation.navigate_to(destination)
            self.speak_feedback(response)
        elif "current time" in command or "what is the time" in command or "time" in command:
            self.describing_surroundings = False
            response = self.time_date.get_current_time_date()
            self.speak_feedback(response)
        elif "weather" in command or "temperature" in command:
            self.describing_surroundings = False
            response = self.weather.get_dandeli_weather()
            self.speak_feedback(response)
        elif any(cmd in command for cmd in ["send alert", "alert", "help"]):
            self.describing_surroundings = False
            if self.alert_system.send_alert():
                self.alert_system.speak_alert("Emergency alert sent successfully. Help is on the way.")
                self.speak_feedback("🚨 I've sent an emergency alert to your contacts. Please stay calm, help is coming.")
            else:
                self.alert_system.speak_alert("Failed to send alert. Please try again.")
                self.speak_feedback("I couldn't send the alert. Let me try again or find another way to help.")
        elif "stop navigation" in command or "close" in command or "exit" in command:
            self.describing_surroundings = False
            self.speak_feedback("Goodbye! Please take care and stay safe. Remember, I'm here whenever you need assistance.")
            self.stop_app()
        else:
            self.speak_feedback("I didn't quite catch that. You can ask me to describe your surroundings, navigate somewhere, tell you the time, or check the weather. How may I assist you?")

    def stop_app(self):
        """Stop the app and release resources."""
        self.running = False
        if self.capture.isOpened():
            self.capture.release()
        cv2.destroyAllWindows()
        sys.exit()

    def speak_feedback(self, message):
        """Add a message to the speech queue."""
        self.speech_messages.append(message)
    
    def process_speech(self, dt):
        """Process the speech queue."""
        if self.speech_messages:
            message = self.speech_messages.pop(0)
            try:
                self.speaker.Speak(message)
            except Exception as e:
                print(f"Speech synthesis error: {e}")
    
    def update(self, dt):
        """Update the video frame and perform object detection."""
        try:
            if not self.running:
                return
            
            ret, frame = self.capture.read()
            if not ret:
                return
            
            frame_resized = cv2.resize(frame, (640, 480))
            img_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            self.frame_counter += 1
            if self.frame_counter % 5 != 0:
                return
            
            # Only perform detection if we're in description mode
            if self.describing_surroundings:
                results = model(img_rgb)
                detected_objects = []
                object_details = []
                person_count, vehicle_count, animal_count = 0, 0, 0
                crowd_detected = False
                special_objects = set()
                current_time = time.time()
                
                # Track currently detected objects
                current_detections = set()
                
                for detection in results.xyxy[0]:
                    xmin, ymin, xmax, ymax, conf, cls = detection
                    xmin, ymin, xmax, ymax = map(int, (xmin.item(), ymin.item(), xmax.item(), ymax.item()))
                    label = results.names[int(cls.item())]
                    detected_objects.append(label)
                    current_detections.add(label)
                    
                    obj_height = ymax - ymin
                    distance = round((5000 / (obj_height + 1e-5)), 2)
                    object_details.append((label, distance, (xmin, ymin, xmax, ymax)))
                    
                    if label == 'person':
                        person_count += 1
                    elif label in ['car', 'bus', 'truck', 'motorcycle', 'bicycle']:
                        vehicle_count += 1
                    elif label in ['dog', 'cat', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']:
                        animal_count += 1
                    
                    if label in ['swing', 'slide', 'bench']:
                        special_objects.add('park')
                    elif label in ['shopping cart', 'handbag', 'backpack']:
                        special_objects.add('market')
                    
                    cv2.rectangle(frame_resized, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    cv2.putText(frame_resized, f"{label}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Update object tracking information
                for obj in current_detections:
                    if obj not in self.object_tracker:
                        self.object_tracker[obj]['first_detected'] = current_time
                    self.object_tracker[obj]['last_detected'] = current_time
                
                # Check for objects that are no longer detected
                disappeared_objects = set(self.object_tracker.keys()) - current_detections
                for obj in disappeared_objects:
                    # If object hasn't been seen for 3 seconds, consider it gone
                    if current_time - self.object_tracker[obj]['last_detected'] > 3:
                        if obj in self.active_warnings:
                            self.speak_feedback(f"The {obj} has passed. It's safe to move forward now.")
                            self.active_warnings.remove(obj)
                        del self.object_tracker[obj]
                
                if person_count > 5:
                    crowd_detected = True
                
                if current_time - self.last_feedback_time > 5:
                    feedback_messages = []
                    
                    if 'park' in special_objects:
                        feedback_messages.append("It seems like you're in a peaceful park. Enjoy the fresh air and nature around you!")
                    elif 'market' in special_objects:
                        feedback_messages.append("You might be in a busy market area. Please be mindful of your surroundings as there could be many people around.")
                    elif crowd_detected:
                        feedback_messages.append("There's a crowd ahead. For your safety, please proceed with caution and consider waiting if needed.")
                    
                    # Generate warnings for approaching objects
                    for label, distance, bbox in object_details:
                        if label in ['car', 'bus', 'truck', 'motorcycle', 'bicycle'] and distance < 300:  # Close vehicle
                            if not self.object_tracker[label]['warning_given']:
                                direction = self.get_direction(bbox, frame_resized.shape[1])
                                feedback_messages.append(f"Caution! There's a {label} approaching {direction}, about {int(distance)} centimeters away. Please stay still until it passes.")
                                self.object_tracker[label]['warning_given'] = True
                                self.active_warnings.add(label)
                        
                        elif label in ['dog', 'cat', 'bird', 'horse', 'sheep', 'cow'] and distance < 200:  # Close animal
                            if not self.object_tracker[label]['warning_given']:
                                direction = self.get_direction(bbox, frame_resized.shape[1])
                                feedback_messages.append(f"Please be careful, there's a {label} {direction}, about {int(distance)} centimeters away. It's best to wait until it moves away.")
                                self.object_tracker[label]['warning_given'] = True
                                self.active_warnings.add(label)
                        
                        elif label == 'person' and distance < 150:  # Close person
                            direction = self.get_direction(bbox, frame_resized.shape[1])
                            feedback_messages.append(f"A person is {direction}, about {int(distance)} centimeters away. You might want to acknowledge them or wait if needed.")
                    
                    if vehicle_count > 0 and not any('vehicle' in msg for msg in feedback_messages):
                        feedback_messages.append("I notice some vehicles nearby. Please be extra cautious when crossing or moving around them.")
                    
                    if animal_count > 0 and not any('animal' in msg for msg in feedback_messages):
                        animal_labels = [label for label in detected_objects if label in ['dog', 'cat', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']]
                        unique_animals = set(animal_labels)
                        if unique_animals:
                            animals_list = ", ".join(unique_animals)
                            feedback_messages.append(f"I see some animals around you including {animals_list}. They're beautiful but please be mindful of your movements.")
                    
                    if not feedback_messages and detected_objects:
                        unique_objects = set(detected_objects)
                        if len(unique_objects) == 1:
                            feedback_messages.append(f"I can see a {unique_objects.pop()} nearby. Everything seems clear otherwise.")
                        else:
                            objects_list = ", ".join(unique_objects)
                            feedback_messages.append(f"Your surroundings include {objects_list}. The path seems generally clear, but please proceed with care.")
                    
                    if feedback_messages:
                        final_message = " ".join(feedback_messages)
                        self.speak_feedback(final_message)
                        self.last_feedback_time = current_time
            
            # Always update the display
            buf = cv2.flip(frame_resized, 0).tobytes()
            texture = Texture.create(size=(frame_resized.shape[1], frame_resized.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
        
        except Exception as e:
            print(f"Update error: {e}")
    
    def get_direction(self, bbox, frame_width):
        """Get the direction of an object relative to the frame."""
        xmin, _, xmax, _ = bbox
        bbox_center = (xmin + xmax) / 2
        if bbox_center < frame_width / 3:
            return "to your left"
        elif bbox_center > 2 * frame_width / 3:
            return "to your right"
        else:
            return "directly ahead of you"
    
    def on_stop(self):
        """Clean up resources when the app stops."""
        self.stop_app()

if __name__ == "__main__":
    app = RealTimeDetectionApp()
    app.run()