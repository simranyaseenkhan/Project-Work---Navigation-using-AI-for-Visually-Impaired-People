# 🦯 Navigation using AI for Visually Impaired People

This is an AI-powered real-time assistant designed to support visually impaired individuals in navigating their environment more safely and independently. The system integrates **YOLOv5 object detection**, **voice recognition**, **speech feedback**, **weather info**, **map navigation**, and an **emergency alert system**.

## 🧠 Features

- 🔍 **Object Detection & Environment Description**  
  Detects people, vehicles, animals, and more using YOLOv5. Describes surroundings with distance and direction estimation.

- 🎤 **Voice Command Interface**  
  Hands-free interaction through speech recognition (Google Speech API).

- 🗣️ **Voice Feedback**  
  Real-time verbal feedback using `pyttsx3` and Windows voice API.

- 🌦️ **Weather Updates**  
  =Retrieves real-time weather data using the Open-Meteo API.

- 🗺️ **Map-Based Navigation**  
  Opens Google Maps with spoken destinations.

- 🆘 **Emergency Alert System**  
  Sends alert emails with live location and contact number to predefined recipients.

---

## 🚀 How It Works

1. **Real-Time Camera Feed**  
   Captures frames using OpenCV and detects objects using a lightweight YOLOv5n model.

2. **Environmental Understanding**  
   Based on detected object types, it deduces if the user is in a park, market, or crowded area and provides context-aware guidance.

3. **Voice Interaction**  
   Users can issue commands like:
   - `"Describe surroundings"`
   - `"Navigate to hospital"`
   - `"What's the weather?"`
   - `"Send alert"`
   - `"Current time"`
   - `"Stop describing"`  
   And more!

4. **Emergency Handling**  
   On voice command, it emails a formatted emergency alert with contact and location info to a list of trusted recipients.

---

## 🛠️ Technologies Used

- **Python**
- **YOLOv5 (torch hub)**
- **OpenCV**
- **Kivy** (GUI)
- **SpeechRecognition**
- **pyttsx3** (Text-to-Speech)
- **win32com.client** (Windows Voice API)
- **Open-Meteo API**
- **SMTP (Email Alerts)**
