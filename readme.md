# Kia Kubernetes Voice Assistant

## Introduction
Kia is an AI-powered voice assistant that allows you to interact with a Kubernetes cluster using voice commands. You can create, list, and manage pods simply by speaking to Kia. 

## Features
- Voice-activated Kubernetes management
- Real-time dashboard to monitor pods
- AI-powered responses and suggestions

## Prerequisites
- Docker Desktop with Kubernetes enabled
- Python 3.8 or above
- A Kubernetes cluster running locally or in the cloud

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Yashground/kubeai.git
   cd kubeai
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit the .env file to set your OpenAI API key
   ```
5. Run the application:
   ```bash
   python assistant/kia_assistant.py
   ```

## Usage
- Start by saying "Hello Kia" or "Hi Kia" to begin.
- You can create a pod by saying "Create a pod" followed by the type of pod you want to create.
- To list all pods, say "List all pods".
- To delete a pod, say "Delete the pod" followed by the name of the pod.    
        
