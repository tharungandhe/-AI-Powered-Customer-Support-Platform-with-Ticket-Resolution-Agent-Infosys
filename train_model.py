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
            # Network (67 items)
            "WiFi is not working", "Internet connection is very slow", "Cannot connect to the office wifi",
            "Network drops frequently", "No internet access on my laptop", "The router seems to be offline",
            "Ethernet port is not working", "Wifi signal is too weak in the conference room",
            "Local network file share is unreachable", "Slow network speeds during downloads",
            "My wifi is disconnected", "No network connection", "Internet is down",
            "The LAN is not working", "Wifi keeps disconnecting", "Can't access the internet",
            "Network speed is terrible", "Ping is very high", "Ethernet cable is broken",
            "Cannot reach network drive", "Router needs reboot", "Lost connection to the network", 
            "WiFi password changed", "Network outage", "Bad internet connection",
            "Network switch is down", "Can't ping the default gateway", "No internet", 
            "WiFi password doesn't work", "Cannot connect to WiFi",
            "LAN cable is unplugged", "Ethernet not detected", "Wifi is super slow", 
            "Internet connection lost", "Network drive not mounting",
            "IP address conflict", "DHCP server not responding", "DNS resolution failed", 
            "Proxy server error", "Firewall blocking internet",
            "Cannot access local host", "Network is unreachable", "Ping request timed out",
            "Wi-Fi keeps dropping out", "Internet is ridiculously slow", "Cannot ping the server",
            "Connection refused by host", "Ethernet adapter disabled", "Wifi signal keeps fluctuating",
            "No internet access on my desktop", "Network latency is too high", "Wifi access point not found",
            "Guest wifi password incorrect", "Corporate wifi disconnected", "Cannot browse any websites",
            "IP address not resolving", "Network packet loss is high", "Wired connection is down",
            "Wireless connection is weak", "DNS server not responding", "Cannot access the company portal",
            "The switch port is disabled", "Network connection dropped suddenly", "Cannot resolve host address",
            "Local area connection unplugged", "Wifi network is hidden", "Need access to guest network",
            
            # VPN (67 items)
            "VPN is not connecting", "Unable to access company VPN", "Cisco AnyConnect VPN error",
            "VPN connection keeps dropping", "Cannot access internal sites while on VPN",
            "VPN authentication failed", "Getting timeout error when connecting to VPN",
            "VPN is too slow when working from home", "How do I install the VPN client?",
            "VPN is blocked on my current network", "VPN client is crashing", "VPN doesn't work",
            "I cannot connect to the VPN", "VPN keeps disconnecting every 5 minutes",
            "GlobalProtect VPN fails", "Need help with VPN access", "VPN login invalid",
            "VPN server unreachable", "Can't access intranet without VPN", "VPN configuration error",
            "VPN tunnel collapsed", "VPN software update needed", "Cannot ping over VPN", 
            "VPN is dropping my connection", "VPN error code 404",
            "VPN timeout", "Cannot connect to AnyConnect", "GlobalProtect is disconnected", 
            "VPN requires multifactor authentication", "VPN tunnel failed",
            "Cannot reach internal network over VPN", "VPN IP address not assigned", 
            "VPN client needs update", "VPN connection refused", "VPN credentials rejected",
            "VPN is blocking local network", "VPN speed is very slow", "VPN keeps reconnecting", 
            "VPN profile missing", "VPN portal is down",
            "Cannot establish VPN connection", "VPN authentication fails every time", "OpenVPN is not connecting",
            "VPN speed is crawling", "Unable to route traffic through VPN", "VPN client keeps crashing",
            "Cannot access local resources while on VPN", "VPN certificate expired", "VPN disconnects when screen locks",
            "Need help setting up VPN on mobile", "VPN login says unauthorized", "VPN gateway is not reachable",
            "My VPN connection is unstable", "VPN software won't install", "VPN fails to initialize",
            "VPN IP conflict", "VPN blocks my internet", "Cannot ping server through VPN",
            "VPN tunnel connection failed", "VPN prompts for password endlessly", "VPN access denied",
            "VPN protocol error", "Cannot open intranet via VPN", "VPN service is stopped",
            "VPN client is outdated", "VPN fails on startup", "VPN drops after 10 minutes",

            # Password (67 items)
            "I forgot my password", "Please reset my password", "My account is locked out",
            "Need a password reset for my email", "Windows login password is not working",
            "Cannot log in, says invalid credentials", "How do I change my password?",
            "SSO login is failing", "Active directory account locked", "Need to reset admin password",
            "Forgot my login password", "Password expired", "Need help resetting password",
            "Locked out of my account", "Reset my domain password", "Password isn't working",
            "Invalid username or password", "Unlock my account", "AD password reset", "Change password request",
            "Reset credentials for active directory", "I need to update my password", "Wrong password entered", 
            "Password recovery link", "Cannot authenticate user",
            "Reset active directory password", "Windows password expired", "SSO authentication failed", 
            "Need new password", "Forgot my email password",
            "Unlock my windows account", "Password reset link expired", "Cannot remember my password", 
            "Change my login password", "Account locked after too many attempts",
            "Need temporary password", "Password doesn't meet requirements", "MFA token out of sync for login", 
            "Reset my domain credentials", "Help me reset my password",
            "My password expired today", "Cannot change password on mac", "Password reset email not received",
            "Admin account password lost", "Need to unblock my account", "MFA not accepting my password",
            "Login failed due to bad password", "System does not recognize my password", "Password too weak error",
            "Cannot login to portal", "Credentials not working", "User account is locked out",
            "How to reset my AD password", "Cannot access my email account", "Email password is not working",
            "Need to reset my windows password", "SSO is redirecting in a loop", "My account is disabled",
            "Forgot my admin credentials", "Unlock my active directory user", "Need a temporary login",
            "Password change failed", "Cannot login after password change", "Domain controller cannot authenticate",
            "Authentication error on login", "Need to reset password for service account", "Forgotten password for internal tool",

            # Software (67 items)
            "Install Microsoft Office", "Application installation required", "Excel is crashing on startup",
            "Need license for Adobe Acrobat", "Zoom is not updating", "Cannot open PDF files",
            "Browser keeps crashing", "Need help installing Visual Studio",
            "Antivirus software is showing an error", "Outlook is not sending emails",
            "Word is frozen", "Teams is not loading", "Application is crashing",
            "Need software license", "Install Chrome browser", "Software update failed",
            "Cannot uninstall program", "App is unresponsive", "Error opening application", "Software is very slow",
            "Photoshop is missing", "Slack won't open anymore", "Need to install zoom app", 
            "Software license has expired", "Browser is extremely slow",
            "Install Adobe Photoshop", "Word is crashing", "Excel macro error", "Cannot open Slack", "Zoom update failed",
            "Need a license for IntelliJ", "Browser is not launching", "Teams audio not working", 
            "Application license expired", "Software is freezing",
            "Cannot install updates", "Uninstall unused software", "Requesting Microsoft Project", 
            "App is not responding", "Error in the software application",
            "Excel is not responding", "Need to install visual studio code", "Outlook crashes when opening",
            "Cannot open word document", "PowerPoint is freezing", "Acrobat reader needs update",
            "Browser is not loading pages", "Teams message not sending", "Cannot join Teams meeting",
            "Application failed to start side-by-side configuration", "Software installation error", "Need license for Microsoft Project",
            "Need to renew software license", "Cannot install Python", "Docker Desktop is not starting",
            "Git is not recognized as an internal command", "Node.js installation failed", "Slack is not sending notifications",
            "Zoom is stuck on connecting", "Need to uninstall old software", "Browser cache needs clearing",
            "Application is giving a syntax error", "Software requires admin rights to run", "Need access to specialized software",
            "Antivirus blocked my application", "Application shortcut is missing", "Cannot export data from software",

            # Hardware (66 items)
            "Laptop keyboard is not working", "Monitor display is not working", "Mouse is broken",
            "Need a new charger for my laptop", "Printer is out of toner", "Laptop battery drains too fast",
            "Screen is flickering", "Headset microphone is not picking up audio", "Need a docking station",
            "Hard drive is making a clicking noise", "My screen is cracked", "Keyboard is missing keys",
            "Laptop won't turn on", "Mouse is double clicking", "Need replacement battery",
            "Printer paper jam", "Speaker has no sound", "Webcam is not working", "USB port broken", "Need a new mouse",
            "RAM replacement needed", "Touchpad is not responding", "Headphones are broken", 
            "Monitor has no video signal", "Laptop fan is very loud",
            "Monitor is blank", "Keyboard is typing double letters", "Mouse scroll wheel broken", 
            "Laptop battery dead", "Printer is making weird noises",
            "Need a replacement charger", "Docking station not working", "Webcam image is blurry", 
            "Headset earpad broken", "Microphone is muted hardware",
            "USB drive not recognized", "Laptop hinges are broken", "Screen has dead pixels", 
            "Need a second monitor", "Motherboard failure",
            "Need an ergonomic keyboard", "Monitor stands are broken", "Laptop touchpad is too sensitive",
            "Battery is swollen", "Power adapter is sparking", "USB port is bent",
            "Headphones have static noise", "Webcam is completely black", "Printer is out of ink",
            "Paper is jammed in printer", "Scanner is not recognized", "Need a larger monitor",
            "Laptop is overheating", "Desktop is making a loud buzzing sound", "Graphics card is failing",
            "Need more RAM for my laptop", "Keyboard backlight is not working", "Mouse pointer is jumping",
            "Laptop case is damaged", "Microphone volume is too low", "Audio jack is broken",
            "Docking station HDMI not working", "Need a wireless mouse", "Webcam microphone not working",
            "Monitor power cable is missing", "Need an adapter for my monitor", 

            # System (66 items)
            "My entire production server is down", "The client meeting system stopped working",
            "Database server is unreachable", "Application deployment failed in production",
            "System is out of memory", "High CPU usage on the main server",
            "Web server is returning 500 errors", "Cannot restart the background service",
            "Backup job failed last night", "Disk space is full on the server",
            "Server is crashing", "Database connection lost", "Deployment pipeline failed",
            "Out of memory error", "CPU is at 100%", "Service is unresponsive",
            "Server reboot required", "System crash", "Error 502 bad gateway", "Backup is failing",
            "Storage is completely full", "Kernel panic on boot", "Blue screen of death on server", 
            "System restart needed urgently", "Server offline entirely",
            "Production database is down", "Server rack lost power", "Kubernetes cluster unresponsive", 
            "High memory usage on server", "CPU usage at 99%",
            "Service stopped working on production", "Error 503 Service Unavailable", "Deployment pipeline is broken", 
            "System backup failed", "Hard drive failure on server",
            "Linux kernel panic", "IIS server not starting", "Out of memory on the host", 
            "VM is not booting", "Active Directory server offline",
            "Server is running out of disk space", "Cannot RDP to the server", "Virtual machine is suspended",
            "Hypervisor is unresponsive", "Operating system update failed", "System is stuck in a boot loop",
            "Cannot mount network drive", "Active Directory replication failing", "Domain controller is down",
            "System log shows critical errors", "File server is very slow", "Cannot map network drive",
            "Permissions denied on network share", "Group policy not applying", "Exchange server is down",
            "Mail flow is stopped", "Firewall is blocking the port", "Router is misconfigured",
            "Switch configuration lost", "System requires an urgent patch", "Cannot access the control panel",
            "IIS application pool stopped", "SQL server service is down", "Database query is timing out",
            "Web application is down", "SSL certificate expired on server"
        ],
        "category": [
            "Network"] * 67 + ["VPN"] * 67 + ["Password"] * 67 + ["Software"] * 67 + ["Hardware"] * 66 + ["System"] * 66
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