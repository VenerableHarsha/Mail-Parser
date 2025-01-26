import tkinter as tk
from tkinter import messagebox
from Backend.authentication import authenticate_gmail
from Backend.gui import RulesManager
from Backend.email_fetching import fetch_emails,fetch_all_labels

def launch_rules_gui(labels,service):
    """
    Launch the Rules Manager GUI.
    """
    root = tk.Tk()
    app = RulesManager(root,labels,service)
    root.mainloop()

def show_retry_window():
    """
    Show a retry window if authentication fails.
    """
    retry_root = tk.Tk()
    retry_root.title("Authentication Failed")
    retry_root.geometry("300x150")
    
    tk.Label(retry_root, text="Authentication failed. Please retry.", font=("Arial", 12)).pack(pady=10)
    
    def retry_auth():
        retry_root.destroy()
        main()  # Retry authentication by calling main()

    retry_button = tk.Button(retry_root, text="Retry", command=retry_auth, font=("Arial", 12))
    retry_button.pack(pady=10)
    
    retry_root.mainloop()

def main():
    """
    Main function to authenticate and launch the Rules Manager GUI.
    """
    try:
        service = authenticate_gmail() 
        print("authentication done")
        if service:
            fetch_emails(service)
            labels=fetch_all_labels(service)
            print("emails geto")
            launch_rules_gui(labels,service) 
    except Exception as e:
        print(f"Error during authentication: {e}")
        show_retry_window() 

if __name__ == "__main__":
    main()
