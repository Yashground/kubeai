import os
import openai
import speech_recognition as sr
import subprocess
import re
import pyttsx3
from fuzzywuzzy import process
from kubernetes import client, config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize Kubernetes client
config.load_kube_config()  # Loads local kubeconfig file
v1 = client.CoreV1Api()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    """Capture voice input and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("I'm listening to your command.")
        audio = recognizer.listen(source)
    try:
        command_text = recognizer.recognize_google(audio)
        return command_text
    except Exception as e:
        response = "Sorry, I couldn't understand you."
        print(f"Kia: {response}")
        speak(response)
        return None

def generate_kubectl_command(prompt):
    """Use OpenAI's GPT-3.5 to generate a kubectl command from the user's prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "As a Kubernetes assistant named Kia, your task is to translate the user's request into a valid 'kubectl' command. "
                    "If the user asks to create a resource from a pod definition file, ensure the file path is 'kubernetes/pod-definition.yaml'."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0
    )
    kubectl_command = response.choices[0].message['content'].strip()

    # If the command is creating a pod from a file, ensure the file path is correct
    if 'pod-definition.yaml' in kubectl_command:
        kubectl_command = kubectl_command.replace('pod-definition.yaml', 'kubernetes\pod-definition.yaml')

    return kubectl_command

def get_pod_names():
    """Retrieve a list of all pod names in the cluster."""
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pod_names = [pod.metadata.name for pod in pods.items]
    return pod_names

def find_closest_pod_name(user_input_pod_name, pod_names):
    """Find the closest matching pod name using fuzzy matching."""
    match, score = process.extractOne(user_input_pod_name, pod_names)
    if score >= 60:  # Adjust threshold as needed
        return match
    else:
        return None

def replace_pod_name_in_command(command):
    """Replace the pod name in the command with the closest matching pod name from the cluster."""
    pod_names = get_pod_names()
    # Extract the pod name from the command using regex
    match = re.search(r'pod\s+(\S+)', command)
    if match:
        user_pod_name = match.group(1)
        closest_pod_name = find_closest_pod_name(user_pod_name, pod_names)
        if closest_pod_name:
            # Replace the pod name in the command
            command = command.replace(user_pod_name, closest_pod_name)
            response = f"Using pod '{closest_pod_name}' for the command."
            print(f"Kia: {response}")
            speak(response)
            return command
        else:
            response = "Sorry, I couldn't find a matching pod name."
            print(f"Kia: {response}")
            speak(response)
            return None
    else:
        return command

def validate_kubectl_command(command):
    """Validate the kubectl command against a list of allowed commands."""
    allowed_patterns = [
        r'^kubectl\s+get\s+pods.*',
        r'^kubectl\s+get\s+services.*',
        r'^kubectl\s+describe\s+pod\s+.*',
        r'^kubectl\s+create\s+deployment\s+.*',
        r'^kubectl\s+delete\s+pod\s+.*',
        r'^kubectl\s+scale\s+deployment\s+.*',
        r'^kubectl\s+get\s+nodes.*',
        r'^kubectl\s+apply\s+-f\s+.*',
        r'^kubectl\s+create\s+-f\s+.*',
        # Add more patterns as needed
   ]
    for pattern in allowed_patterns:
        if re.match(pattern, command):
            return True
    response = "Command not allowed for execution."
    print(f"Kia: {response}")
    speak(response)
    return False

def execute_kubectl_command(kubectl_command):
    """Execute the kubectl command and display the output."""
    try:
        print(f"Kia: Executing command: {kubectl_command}")
        speak(f"Executing command: {kubectl_command}")
        result = subprocess.run(kubectl_command.split(), capture_output=True, text=True)
        if result.stdout:
            print("Output:")
            print(result.stdout)
            speak("Command executed successfully.")
        if result.stderr:
            print("Error:")
            print(result.stderr)
            speak("There was an error executing the command.")
    except Exception as e:
        response = "An unexpected error occurred while executing the command."
        print(f"Kia: {response}")
        speak(response)

def main():
    """Main function to run the voice assistant."""
    print("Kia: Hello! I'm Kia, your Kubernetes assistant.")
    speak("Hello Yash! I'm Kia, your Kubernetes assistant.")
    while True:
        user_command = recognize_speech()
        if user_command:
            print(f"You said: {user_command}")
            kubectl_cmd = generate_kubectl_command(user_command)
            print(f"Kia: Generated command: {kubectl_cmd}")

            # Replace pod name if needed
            kubectl_cmd = replace_pod_name_in_command(kubectl_cmd)
            if not kubectl_cmd:
                continue  # Skip execution if pod name couldn't be matched

            if validate_kubectl_command(kubectl_cmd):
                execute_kubectl_command(kubectl_cmd)
            else:
                response = "Sorry, I cannot execute that command."
                print(f"Kia: {response}")
                speak(response)
        else:
            continue
        cont = input("Do you want to issue another command? (y/n): ")
        if cont.lower() != 'y':
            print("Kia: Goodbye Yash!")
            speak("Goodbye Yash!")
            break

if __name__ == "__main__":
    main()
