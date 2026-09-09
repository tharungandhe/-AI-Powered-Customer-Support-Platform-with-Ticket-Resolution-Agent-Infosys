import pandas as pd
from sklearn.model_selection import train_test_split 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import joblib #[cite: 7]
import os #[cite: 7]

def train_and_save_model():
    data = {
        "ticket": [
            # Network
            "WiFi is not working", "Internet connection is very slow", "Cannot connect to the office wifi", #[cite: 7]
            "Network drops frequently", "No internet access on my laptop", "The router seems to be offline", #[cite: 7]
            "Ethernet port is not working", "Wifi signal is too weak in the conference room", #[cite: 7]
            "Local network file share is unreachable", "Slow network speeds during downloads", #[cite: 7]
            "My wifi is disconnected", "No network connection", "Internet is down",  #[cite: 7]
            "The LAN is not working", "Wifi keeps disconnecting", "Can't access the internet", #[cite: 7]
            "Network speed is terrible", "Ping is very high", "Ethernet cable is broken", #[cite: 7]
            "Cannot reach network drive", #[cite: 7]
            "Router needs reboot", "Lost connection to the network", "WiFi password changed", "Network outage", "Bad internet connection", #[cite: 7]
            "Network switch is down", "Can't ping the default gateway", "No internet", "WiFi password doesn't work", "Cannot connect to WiFi", #[cite: 7]
            "LAN cable is unplugged", "Ethernet not detected", "Wifi is super slow", "Internet connection lost", "Network drive not mounting", #[cite: 7]
            "IP address conflict", "DHCP server not responding", "DNS resolution failed", "Proxy server error", "Firewall blocking internet", #[cite: 7]
            
            # VPN
            "VPN is not connecting", "Unable to access company VPN", "Cisco AnyConnect VPN error", #[cite: 7]
            "VPN connection keeps dropping", "Cannot access internal sites while on VPN", #[cite: 7]
            "VPN authentication failed", "Getting timeout error when connecting to VPN", #[cite: 7]
            "VPN is too slow when working from home", "How do I install the VPN client?", #[cite: 7]
            "VPN is blocked on my current network", "VPN client is crashing", "VPN doesn't work", #[cite: 7]
            "I cannot connect to the VPN", "VPN keeps disconnecting every 5 minutes", #[cite: 7]
            "GlobalProtect VPN fails", "Need help with VPN access", "VPN login invalid", #[cite: 7]
            "VPN server unreachable", "Can't access intranet without VPN", "VPN configuration error", #[cite: 7]
            "VPN tunnel collapsed", "VPN software update needed", "Cannot ping over VPN", "VPN is dropping my connection", "VPN error code 404", #[cite: 7]
            "VPN timeout", "Cannot connect to AnyConnect", "GlobalProtect is disconnected", "VPN requires multifactor authentication", "VPN tunnel failed", #[cite: 7]
            "Cannot reach internal network over VPN", "VPN IP address not assigned", "VPN client needs update", "VPN connection refused", "VPN credentials rejected", #[cite: 7]
            "VPN is blocking local network", "VPN speed is very slow", "VPN keeps reconnecting", "VPN profile missing", "VPN portal is down", #[cite: 7]

            # Password
            "I forgot my password", "Please reset my password", "My account is locked out", #[cite: 7]
            "Need a password reset for my email", "Windows login password is not working", #[cite: 7]
            "Cannot log in, says invalid credentials", "How do I change my password?", #[cite: 7]
            "SSO login is failing", "Active directory account locked", "Need to reset admin password", #[cite: 7]
            "Forgot my login password", "Password expired", "Need help resetting password", #[cite: 7]
            "Locked out of my account", "Reset my domain password", "Password isn't working", #[cite: 7]
            "Invalid username or password", "Unlock my account", "AD password reset", "Change password request", #[cite: 7]
            "Reset credentials for active directory", "I need to update my password", "Wrong password entered", "Password recovery link", "Cannot authenticate user", #[cite: 7]
            "Reset active directory password", "Windows password expired", "SSO authentication failed", "Need new password", "Forgot my email password", #[cite: 7]
            "Unlock my windows account", "Password reset link expired", "Cannot remember my password", "Change my login password", "Account locked after too many attempts", #[cite: 7]
            "Need temporary password", "Password doesn't meet requirements", "MFA token out of sync for login", "Reset my domain credentials", "Help me reset my password", #[cite: 7]

            # Software
            "Install Microsoft Office", "Application installation required", "Excel is crashing on startup", #[cite: 7]
            "Need license for Adobe Acrobat", "Zoom is not updating", "Cannot open PDF files", #[cite: 7]
            "Browser keeps crashing", "Need help installing Visual Studio", #[cite: 7]
            "Antivirus software is showing an error", "Outlook is not sending emails", #[cite: 7]
            "Word is frozen", "Teams is not loading", "Application is crashing",  #[cite: 7]
            "Need software license", "Install Chrome browser", "Software update failed", #[cite: 7]
            "Cannot uninstall program", "App is unresponsive", "Error opening application", "Software is very slow", #[cite: 7]
            "Photoshop is missing", "Slack won't open anymore", "Need to install zoom app", "Software license has expired", "Browser is extremely slow", #[cite: 7]
            "Install Adobe Photoshop", "Word is crashing", "Excel macro error", "Cannot open Slack", "Zoom update failed", #[cite: 7]
            "Need a license for IntelliJ", "Browser is not launching", "Teams audio not working", "Application license expired", "Software is freezing", #[cite: 7]
            "Cannot install updates", "Uninstall unused software", "Requesting Microsoft Project", "App is not responding", "Error in the software application", #[cite: 7]

            # Hardware
            "Laptop keyboard is not working", "Monitor display is not working", "Mouse is broken", #[cite: 7]
            "Need a new charger for my laptop", "Printer is out of toner", "Laptop battery drains too fast", #[cite: 7]
            "Screen is flickering", "Headset microphone is not picking up audio", "Need a docking station", #[cite: 7]
            "Hard drive is making a clicking noise", "My screen is cracked", "Keyboard is missing keys", #[cite: 7]
            "Laptop won't turn on", "Mouse is double clicking", "Need replacement battery", #[cite: 7]
            "Printer paper jam", "Speaker has no sound", "Webcam is not working", "USB port broken", "Need a new mouse", #[cite: 7]
            "RAM replacement needed", "Touchpad is not responding", "Headphones are broken", "Monitor has no video signal", "Laptop fan is very loud", #[cite: 7]
            "Monitor is blank", "Keyboard is typing double letters", "Mouse scroll wheel broken", "Laptop battery dead", "Printer is making weird noises", #[cite: 7]
            "Need a replacement charger", "Docking station not working", "Webcam image is blurry", "Headset earpad broken", "Microphone is muted hardware", #[cite: 7]
            "USB drive not recognized", "Laptop hinges are broken", "Screen has dead pixels", "Need a second monitor", "Motherboard failure", #[cite: 7]

            # System
            "My entire production server is down", "The client meeting system stopped working", #[cite: 7]
            "Database server is unreachable", "Application deployment failed in production", #[cite: 7]
            "System is out of memory", "High CPU usage on the main server", #[cite: 7]
            "Web server is returning 500 errors", "Cannot restart the background service", #[cite: 7]
            "Backup job failed last night", "Disk space is full on the server", #[cite: 7]
            "Server is crashing", "Database connection lost", "Deployment pipeline failed", #[cite: 7]
            "Out of memory error", "CPU is at 100%", "Service is unresponsive", #[cite: 7]
            "Server reboot required", "System crash", "Error 502 bad gateway", "Backup is failing", #[cite: 7]
            "Storage is completely full", "Kernel panic on boot", "Blue screen of death on server", "System restart needed urgently", "Server offline entirely", #[cite: 7]
            "Production database is down", "Server rack lost power", "Kubernetes cluster unresponsive", "High memory usage on server", "CPU usage at 99%", #[cite: 7]
            "Service stopped working on production", "Error 503 Service Unavailable", "Deployment pipeline is broken", "System backup failed", "Hard drive failure on server", #[cite: 7]
            "Linux kernel panic", "IIS server not starting", "Out of memory on the host", "VM is not booting", "Active Directory server offline" #[cite: 7]
        ],
        "category": [
            "Network"] * 40 + ["VPN"] * 40 + ["Password"] * 40 + ["Software"] * 40 + ["Hardware"] * 40 + ["System"] * 40 #[cite: 7]
    }

    df = pd.DataFrame(data) #[cite: 7]
    X = df["ticket"] #[cite: 7]
    y = df["category"] #[cite: 7]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42 #[cite: 7]
    )

    # Removed min_df and max_df restrictions
    vectorizer = TfidfVectorizer(stop_words='english', analyzer='word', ngram_range=(1, 1))
    X_train_vector = vectorizer.fit_transform(X_train)
    X_test_vector = vectorizer.transform(X_test)

    # Increased C parameter and max_iter for better fitting
    base_svc = LinearSVC(C=50.0, random_state=42, dual="auto", max_iter=5000)
    model = CalibratedClassifierCV(base_svc, cv=5)
    
    model.fit(X_train_vector, y_train)

    accuracy = model.score(X_test_vector, y_test)
    print(f"Accuracy: {accuracy * 100:.2f}%") #[cite: 7]

    os.makedirs("models", exist_ok=True) #[cite: 7]
    
    joblib.dump(model, "models/ticket_classifier.pkl") #[cite: 7]
    joblib.dump(vectorizer, "models/vectorizer.pkl") #[cite: 7]
    print("Model and vectorizer saved to models/") #[cite: 7]

if __name__ == "__main__": #[cite: 7]
    train_and_save_model() #[cite: 7]