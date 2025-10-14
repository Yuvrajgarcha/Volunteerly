import tkinter as tk
from tkinter import messagebox, simpledialog
import json
from collections import deque

# Base class for all users, storing common attributes including disabilities
class Person:
    """Base class for all users."""
    def __init__(self, name, email, phone, age, username, password, role, disabilities=""):
        self.name = name           # Stores full name
        self.email = email         # Stores email address
        self.phone = phone         # Stores phone number
        self.age = int(age)        # Converts age to integer and stores it
        self.username = username    # Stores unique username
        self.password = password    # Stores password 
        self.role = role           # Stores user role 
        self.disabilities = disabilities  # Stores optional disabilities information

# Volunteer class, inherits from Person, for users who apply to opportunities
class Volunteer(Person):
    """Volunteer user: can apply to opportunities and view own applications."""
    def __init__(self, name, email, phone, age, username, password, disabilities=""):
        super().__init__(name, email, phone, age, username, password, role="Volunteer", disabilities=disabilities)
        self.my_applications = []  # Initializes an empty list to store the volunteer's applications

    # Method to apply for a volunteer opportunity
    def apply(self, opportunity):
        # Creates a new VolunteerApplication with username, opportunity title, and posted_by
        app = VolunteerApplication(self.username, opportunity.title, opportunity.posted_by)
        self.my_applications.append(app)  # Adds application to volunteer's list
        return app                       # Returns the created application

# Recruit class, inherits from Person, for users who manage opportunities and applications
class Recruit(Person):
    """Recruiter user: can post opportunities and review applications."""
    def __init__(self, name, email, phone, age, username, password, disabilities=""):
        super().__init__(name, email, phone, age, username, password, role="Recruit", disabilities=disabilities)

# Class to represent a volunteer opportunity
class VolunteerOpportunity:
    """Represents an opportunity posted by a recruiter."""
    def __init__(self, title, description, location, date, posted_by):
        self.title = title             # Stores opportunity title
        self.description = description # Stores opportunity description
        self.location = location       # Stores opportunity location
        self.date = date               # Stores opportunity date
        self.posted_by = posted_by     # Stores username of the user who posted the opportunity

# Class to represent a volunteer application
class VolunteerApplication:
    """Represents a volunteer application to a specific opportunity."""
    def __init__(self, username, opportunity_title, posted_by):
        self.username = username                # Stores applicant's username
        self.opportunity_title = opportunity_title  # Stores title of the opportunity
        self.posted_by = posted_by             # Stores username of the opportunity poster
        self.status = "Pending"                # Sets initial application status to "Pending"

# Main system controller class to manage users, opportunities, and applications
class VolunteerSystem:
    """Manages users, opportunities and applications (with JSON persistence)."""
    def __init__(self, file_path='data.json'):
        self.file_path = file_path  # Path to JSON file for data persistence
        self.users = []            # List to store all registered users
        self.opportunities = []    # List to store all volunteer opportunities
        self.applications = deque()  # Deque to store all volunteer applications
        self.load()                # Load data from JSON file on initialization

    # SERIALIZATION HELPERS
    # Converts a user object to a dictionary for JSON serialization
    def _user_to_dict(self, user):
        return {
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'age': user.age,
            'username': user.username,
            'password': user.password,
            'role': user.role,
            'disabilities': user.disabilities,
        }

    # Creates a user object from a dictionary
    def _user_from_dict(self, d):
        role = d['role']
        disabilities = d.get('disabilities', "")
        if role == 'Volunteer':
            return Volunteer(d['name'], d['email'], d['phone'], d['age'], d['username'], d['password'], disabilities)
        elif role == 'Recruit':
            return Recruit(d['name'], d['email'], d['phone'], d['age'], d['username'], d['password'], disabilities)

    # Converts an opportunity object to a dictionary for JSON serialization
    def _opp_to_dict(self, opp):
        return {
            'title': opp.title,
            'description': opp.description,
            'location': opp.location,
            'date': opp.date,
            'posted_by': opp.posted_by,
        }

    # Creates an opportunity object from a dictionary
    def _opp_from_dict(self, d):
        return VolunteerOpportunity(d['title'], d['description'], d['location'], d['date'], d['posted_by'])

    # Converts an application object to a dictionary for JSON serialization
    def _app_to_dict(self, app):
        return {
            'username': app.username,
            'opportunity_title': app.opportunity_title,
            'posted_by': app.posted_by,
            'status': app.status,
        }

    # Creates an application object from a dictionary
    def _app_from_dict(self, d):
        app = VolunteerApplication(d['username'], d['opportunity_title'], d['posted_by'])
        app.status = d['status']
        return app

    # LOAD/SAVE METHODS
    # Loads data from the JSON file
    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.users = [self._user_from_dict(u) for u in data.get('users', [])]
                self.opportunities = [self._opp_from_dict(o) for o in data.get('opportunities', [])]
                self.applications = deque([self._app_from_dict(a) for a in data.get('applications', [])])
                # Populate volunteer my_applications from loaded applications
                for user in self.users:
                    if isinstance(user, Volunteer):
                        user.my_applications = [app for app in self.applications if app.username == user.username]
        except FileNotFoundError:
            pass  # If file doesn't exist, start with empty data

    # Saves data to the JSON file
    def save(self):
        data = {
            'users': [self._user_to_dict(u) for u in self.users],
            'opportunities': [self._opp_to_dict(o) for o in self.opportunities],
            'applications': [self._app_to_dict(a) for a in self.applications],
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)  # Save data with indentation for readability

    # VALIDATION METHODS
    # Checks if a username already exists in the system
    def username_exists(self, username):
        return any(u.username == username for u in self.users)  # Returns True if username is taken

    # Validates name (allows only letters and spaces, must not be empty)
    def valid_name(self, name):
        return name and name.replace(" ", "").isalpha()

    # Validates email (checks for '@' and ends with .com, .org, or .edu)
    def valid_email(self, email):
        return email and ("@" in email and (email.endswith(".com") or email.endswith(".org") or email.endswith(".edu")))

    # Validates phone number (allows digits or digits with a leading '+')
    def valid_phone(self, phone):
        if not phone:
            return False
        if phone.startswith("+"):
            return phone[1:].isdigit()  # Allows international format with '+'
        return phone.isdigit()          # Allows digits only for local numbers

    # Validates password (at least 6 characters, with uppercase and digit)
    def valid_password(self, pw):
        return len(pw) >= 6 and any(c.isupper() for c in pw) and any(c.isdigit() for c in pw)

    # Validates age (between 12 and 120)
    def valid_age(self, age_str):
        if not age_str.isdigit():
            return False
        n = int(age_str)
        return 12 <= n <= 120

    # REGISTRATION
    # Registers a new user with validation
    def register(self, name, email, phone, age, username, password, confirm_pw, role, disabilities):
        if self.username_exists(username):
            return None, "Username already exists."
        if not self.valid_name(name):
            return None, "Name must contain only letters and spaces."
        if not self.valid_email(email):
            return None, "Email must include '@' and end with .com/.org/.edu."
        if not self.valid_phone(phone):
            return None, "Phone must be digits only, optionally start with +."
        if not self.valid_age(age):
            return None, "Enter a valid numeric age."
        if password != confirm_pw:
            return None, "Passwords do not match."
        if not self.valid_password(password):
            return None, "Password must be 6+ chars, include uppercase and a digit."
        if role == "Volunteer" and int(age) < 16:
            return None, "Volunteers must be at least 16 years old."
        if role == "Volunteer":
            user = Volunteer(name, email, phone, age, username, password, disabilities)
        elif role == "Recruit":
            user = Recruit(name, email, phone, age, username, password, disabilities)
        else:
            return None, "Invalid role selected."
        self.users.append(user)  # Add user to the users list
        self.save()              # Save data to JSON file
        return user, f"{name} registered successfully as {role}."

    # LOGIN
    # Authenticates a user based on username and password
    def login(self, username, password):
        for u in self.users:
            if u.username == username and u.password == password:
                return u  # Returns user object if credentials match
        return None   # Returns None if login fails

    # OPPORTUNITY AND APPLICATION MANAGEMENT
    # Posts a new volunteer opportunity
    def post_opportunity(self, title, description, location, date, posted_by):
        opp = VolunteerOpportunity(title, description, location, date, posted_by)
        self.opportunities.append(opp)  # Adds opportunity to the opportunities list
        self.save()                    # Save data to JSON file
        return opp                     # Returns the created opportunity

    # Returns a copy of all opportunities
    def get_opportunities(self):
        return self.opportunities.copy()

    # Allows a volunteer to apply for an opportunity
    def apply_to_opportunity(self, volunteer: Volunteer, opp_index):
        if opp_index < 0 or opp_index >= len(self.opportunities):
            return None, "Invalid opportunity selection."
        opp = self.opportunities[opp_index]
        app = volunteer.apply(opp)        # Create application via Volunteer class
        self.applications.append(app)     # Add application to deque
        self.save()                      # Save data to JSON file
        return app, f"Applied for '{opp.title}' successfully."

    # Returns applications posted by a specific recruit
    def get_applications_for_recruit(self, recruit_username):
        return [app for app in self.applications if app.posted_by == recruit_username]

    # Updates the status of an application
    def set_application_status(self, app_index, new_status, recruit_username):
        apps = self.get_applications_for_recruit(recruit_username)
        if app_index < 0 or app_index >= len(apps):
            return False, "Invalid application selection."
        target = apps[app_index]
        target.status = new_status  # Update application status
        self.save()                 # Save data to JSON file
        return True, f"Application by {target.username} marked as {new_status}."

    # Processes the next pending application for a recruit
    def process_next_pending(self, recruit_username):
        for i, app in enumerate(self.applications):
            if app.posted_by == recruit_username and app.status == "Pending":
                pending_app = self.applications[i]
                del self.applications[i]  # Remove from deque (O(n) for deque, acceptable for small sizes)
                return pending_app, "Next pending application dequeued."
        return None, "No pending applications."

    # Retrieves a user by their username
    def get_user_by_username(self, username):
        for u in self.users:
            if u.username == username:
                return u
        return None

# GUI IMPLEMENTATION USING TKINTER (GREEN THEME)
# Create the main VolunteerSystem instance
system = VolunteerSystem()

# Define color constants for green theme
GREEN_BG = "#d8f3dc"       # Light green background
DARK_GREEN = "#1b4332"     # Dark green for text
BUTTON_GREEN = "#95d5b2"   # Button background
BUTTON_ACTIVE = "#74c69d"  # Button active background

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Volunteering Management System")
root.geometry("520x360")  # Set window size
root.configure(bg=GREEN_BG)  # Apply green background
title_label = tk.Label(root, text="Volunteering Management System", font=("Arial", 16, "bold"), fg=DARK_GREEN, bg=GREEN_BG)
title_label.pack(pady=10)

# BUTTON HELPER
# Creates a styled button with consistent green theme
def make_button(parent, text, command, width=16):
    return tk.Button(parent, text=text, width=width, command=command, bg=BUTTON_GREEN, fg=DARK_GREEN, activebackground=BUTTON_ACTIVE, font=("Arial", 10, "bold"), relief="raised", bd=3)

# REGISTER WINDOW
# Opens a new window for user registration
def open_register_window():
    reg = tk.Toplevel(root)  # Create a new top-level window
    reg.title("Register")
    reg.geometry("420x520")  # Set window size
    reg.configure(bg=GREEN_BG)  # Apply green background
    tk.Label(reg, text="Register", font=("Arial", 14, "bold"), fg=DARK_GREEN, bg=GREEN_BG).pack(pady=8)
    # Create entry fields for registration details
    tk.Label(reg, text="Full name", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_name = tk.Entry(reg, width=40); entry_name.pack(padx=12, pady=2)
    tk.Label(reg, text="Email", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_email = tk.Entry(reg, width=40); entry_email.pack(padx=12, pady=2)
    tk.Label(reg, text="Phone", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_phone = tk.Entry(reg, width=40); entry_phone.pack(padx=12, pady=2)
    tk.Label(reg, text="Age", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_age = tk.Entry(reg, width=40); entry_age.pack(padx=12, pady=2)
    tk.Label(reg, text="Username", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_username = tk.Entry(reg, width=40); entry_username.pack(padx=12, pady=2)
    tk.Label(reg, text="Password", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_password = tk.Entry(reg, show="*", width=40); entry_password.pack(padx=12, pady=2)
    tk.Label(reg, text="Confirm Password", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_confirm = tk.Entry(reg, show="*", width=40); entry_confirm.pack(padx=12, pady=2)
    tk.Label(reg, text="Disabilities (if any)", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_disabilities = tk.Entry(reg, width=40); entry_disabilities.pack(padx=12, pady=2)
    tk.Label(reg, text="Role", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    role_var = tk.StringVar(value="Volunteer")
    tk.OptionMenu(reg, role_var, "Volunteer", "Recruit").pack(padx=12, pady=6)

    # Function to handle registration submission
    def submit_registration():
        name = entry_name.get().strip()
        email = entry_email.get().strip().lower()
        phone = entry_phone.get().strip()
        age = entry_age.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get()
        confirm = entry_confirm.get()
        disabilities = entry_disabilities.get().strip()
        role = role_var.get()
        user, msg = system.register(name, email, phone, age, username, password, confirm, role, disabilities)
        if user:
            messagebox.showinfo("Success", msg)  # Show success message
            reg.destroy()                       # Close registration window
        else:
            messagebox.showerror("Registration error", msg)  # Show error message

    # Buttons for registration and closing the window
    make_button(reg, "Register", submit_registration, width=18).pack(pady=10)
    make_button(reg, "Close", reg.destroy, width=10).pack()

# LOGIN WINDOW
# Opens a new window for user login
def open_login_window():
    login = tk.Toplevel(root)  # Create a new top-level window
    login.title("Login")
    login.geometry("360x220")  # Set window size
    login.configure(bg=GREEN_BG)  # Apply green background
    tk.Label(login, text="Login", font=("Arial", 14, "bold"), fg=DARK_GREEN, bg=GREEN_BG).pack(pady=8)
    tk.Label(login, text="Username", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_username = tk.Entry(login, width=34); entry_username.pack(padx=12, pady=2)
    tk.Label(login, text="Password", fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", padx=12)
    entry_password = tk.Entry(login, show="*", width=34); entry_password.pack(padx=12, pady=6)

    # Function to handle login submission
    def submit_login():
        username = entry_username.get().strip()
        pw = entry_password.get()
        user = system.login(username, pw)
        if user:
            messagebox.showinfo("Welcome", f"Welcome, {user.name} ({user.role})!")  # Show welcome message
            login.destroy()  # Close login window
            open_dashboard(user)  # Open role-specific dashboard
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")  # Show error message

    # Buttons for login and closing the window
    make_button(login, "Login", submit_login, width=14).pack(pady=6)
    make_button(login, "Close", login.destroy, width=8).pack()

# DASHBOARD WINDOWS
# Opens a role-specific dashboard for the logged-in user
def open_dashboard(user):
    dash = tk.Toplevel(root)  # Create a new top-level window
    dash.title(f"{user.role} Dashboard - {user.username}")
    dash.geometry("700x520")  # Set window size
    dash.configure(bg=GREEN_BG)  # Apply green background
    header = tk.Label(dash, text=f"{user.role} Dashboard", font=("Arial", 14, "bold"), fg=DARK_GREEN, bg=GREEN_BG)
    header.pack(pady=8)

    # VOLUNTEER DASHBOARD
    if user.role == "Volunteer":
        left = tk.Frame(dash, bg=GREEN_BG)
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(left, text="Available Opportunities:", font=("Arial", 11, "bold"), fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w")
        opp_listbox = tk.Listbox(left, width=50, height=18, bg="white", fg=DARK_GREEN)
        opp_listbox.pack(padx=6, pady=6)
        tk.Label(left, text="Description:", font=("Arial", 11, "bold"), fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w")
        desc_text = tk.Text(left, width=50, height=5, wrap="word", bg="white", fg=DARK_GREEN)
        desc_text.pack(padx=6, pady=6)
        desc_text.config(state="disabled")  # Make description text read-only

        # Function to refresh the opportunities listbox
        def refresh_opps():
            opp_listbox.delete(0, tk.END)
            for i, opp in enumerate(system.get_opportunities()):
                opp_listbox.insert(tk.END, f"[{i+1}] {opp.title} - {opp.location} ({opp.date})")

        refresh_opps()

        # Function to display the description of the selected opportunity
        def show_description(event):
            selection = opp_listbox.curselection()
            if selection:
                idx = selection[0]
                opp = system.get_opportunities()[idx]
                desc_text.config(state="normal")  # Enable editing to update text
                desc_text.delete("1.0", tk.END)
                desc_text.insert(tk.END, opp.description)
                desc_text.config(state="disabled")  # Make read-only again

        opp_listbox.bind("<<ListboxSelect>>", show_description)

        right = tk.Frame(dash, bg=GREEN_BG)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        # Function to apply to the selected opportunity
        def apply_selected():
            selection = opp_listbox.curselection()
            if not selection:
                messagebox.showwarning("No selection", "Select an opportunity to apply for.")
                return
            idx = selection[0]
            app, msg = system.apply_to_opportunity(user, idx)
            if app:
                messagebox.showinfo("Applied", msg)
                refresh_apps()
            else:
                messagebox.showerror("Apply failed", msg)

        make_button(right, "Apply to Selected Opportunity", apply_selected, width=28).pack(pady=6)
        tk.Label(right, text="My Applications:", font=("Arial", 11, "bold"), fg=DARK_GREEN, bg=GREEN_BG).pack(anchor="w", pady=(18, 4))
        apps_listbox = tk.Listbox(right, width=40, height=12, bg="white", fg=DARK_GREEN)
        apps_listbox.pack(padx=6, pady=6)

        # Function to refresh the applications listbox
        def refresh_apps():
            apps_listbox.delete(0, tk.END)
            for i, app in enumerate([a for a in system.applications if a.username == user.username]):
                apps_listbox.insert(tk.END, f"{app.opportunity_title} - {app.status}")

        # Function to show details of a selected application
        def show_application_details(event):
            selection = apps_listbox.curselection()
            if selection:
                idx = selection[0]
                apps = [a for a in system.applications if a.username == user.username]
                if 0 <= idx < len(apps):
                    app = apps[idx]
                    opp = next(o for o in system.opportunities if o.title == app.opportunity_title and o.posted_by == app.posted_by)
                    recruit = system.get_user_by_username(app.posted_by)
                    details = f"Opportunity Title: {app.opportunity_title}\nStatus: {app.status}\nLocation: {opp.location}\nDate: {opp.date}\nPosted By: {recruit.name if recruit else 'Unknown'}\nRecruit Email: {recruit.email if recruit else 'N/A'}"
                    app_window = tk.Toplevel(dash)
                    app_window.title("Application Details")
                    app_window.geometry("300x200")
                    app_window.configure(bg=GREEN_BG)
                    tk.Label(app_window, text=details, font=("Arial", 10), fg=DARK_GREEN, bg=GREEN_BG, justify="left").pack(padx=10, pady=10)
                    make_button(app_window, "Close", app_window.destroy, width=10).pack(pady=10)

        refresh_apps()
        apps_listbox.bind("<<ListboxSelect>>", show_application_details)

        make_button(right, "Refresh Opportunities", refresh_opps, width=28).pack(pady=4)
        make_button(right, "Refresh My Applications", refresh_apps, width=28).pack(pady=4)
        make_button(right, "Logout", dash.destroy, width=28).pack(pady=12)

    # RECRUIT DASHBOARD
    elif user.role == "Recruit":
        create_frame = tk.LabelFrame(dash, text="Create Opportunity", padx=8, pady=8, bg=GREEN_BG, fg=DARK_GREEN)
        create_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(create_frame, text="Title", fg=DARK_GREEN, bg=GREEN_BG).grid(row=0, column=0, sticky="w")
        e_title = tk.Entry(create_frame, width=60); e_title.grid(row=0, column=1, pady=2)
        tk.Label(create_frame, text="Location", fg=DARK_GREEN, bg=GREEN_BG).grid(row=1, column=0, sticky="w")
        e_location = tk.Entry(create_frame, width=60); e_location.grid(row=1, column=1, pady=2)
        tk.Label(create_frame, text="Date", fg=DARK_GREEN, bg=GREEN_BG).grid(row=2, column=0, sticky="w")
        e_date = tk.Entry(create_frame, width=60); e_date.grid(row=2, column=1, pady=2)
        tk.Label(create_frame, text="Description", fg=DARK_GREEN, bg=GREEN_BG).grid(row=3, column=0, sticky="nw")
        e_desc = tk.Text(create_frame, width=45, height=4, bg="white", fg=DARK_GREEN); e_desc.grid(row=3, column=1, pady=4)

        # Function to submit a new opportunity
        def submit_opportunity():
            title = e_title.get().strip()
            loc = e_location.get().strip()
            date = e_date.get().strip()
            desc = e_desc.get("1.0", tk.END).strip()
            if len(title) < 3:
                messagebox.showerror("Invalid", "Title must be at least 3 characters.")
                return
            if len(loc) < 2:
                messagebox.showerror("Invalid", "Location must be at least 2 characters.")
                return
            if len(date) < 4:
                messagebox.showerror("Invalid", "Enter a valid date.")
                return
            if len(desc) < 8:
                messagebox.showerror("Invalid", "Description too short.")
                return
            system.post_opportunity(title, desc, loc, date, user.username)
            messagebox.showinfo("Posted", f"Opportunity '{title}' posted.")
            e_title.delete(0, tk.END); e_location.delete(0, tk.END); e_date.delete(0, tk.END); e_desc.delete("1.0", tk.END)
            refresh_opps_listboxes()

        make_button(create_frame, "Post Opportunity", submit_opportunity).grid(row=4, column=1, sticky="e", pady=6)

        mid_frame = tk.LabelFrame(dash, text="Your Opportunities & Applications", padx=8, pady=8, bg=GREEN_BG, fg=DARK_GREEN)
        mid_frame.pack(fill="both", expand=True, padx=10, pady=8)
        tk.Label(mid_frame, text="Your Opportunities:", fg=DARK_GREEN, bg=GREEN_BG).grid(row=0, column=0, sticky="w")
        my_opp_listbox = tk.Listbox(mid_frame, width=40, height=8, bg="white", fg=DARK_GREEN)
        my_opp_listbox.grid(row=1, column=0, padx=6, pady=4)
        tk.Label(mid_frame, text="Applications to your opportunities:", fg=DARK_GREEN, bg=GREEN_BG).grid(row=0, column=1, sticky="w", padx=8)
        my_app_listbox = tk.Listbox(mid_frame, width=48, height=8, bg="white", fg=DARK_GREEN)
        my_app_listbox.grid(row=1, column=1, padx=8, pady=4)

        # Function to refresh opportunities and applications listboxes
        def refresh_opps_listboxes():
            my_opp_listbox.delete(0, tk.END)
            for i, opp in enumerate(system.get_opportunities()):
                if opp.posted_by == user.username:
                    my_opp_listbox.insert(tk.END, f"[{i+1}] {opp.title} - {opp.location} ({opp.date})")
            my_app_listbox.delete(0, tk.END)
            apps = system.get_applications_for_recruit(user.username)
            for i, app in enumerate(apps):
                my_app_listbox.insert(tk.END, f"[{i+1}] {app.username} -> {app.opportunity_title} ({app.status})")

        refresh_opps_listboxes()

        app_btn_frame = tk.Frame(mid_frame, bg=GREEN_BG)
        app_btn_frame.grid(row=2, column=1, pady=6)

        # Function to accept a selected application
        def accept_selected():
            s = my_app_listbox.curselection()
            if not s:
                messagebox.showwarning("Select", "Select an application to accept.")
                return
            idx = s[0]
            ok, msg = system.set_application_status(idx, "Accepted", user.username)
            if ok:
                messagebox.showinfo("Updated", msg)
                refresh_opps_listboxes()
            else:
                messagebox.showerror("Error", msg)

        # Function to reject a selected application
        def reject_selected():
            s = my_app_listbox.curselection()
            if not s:
                messagebox.showwarning("Select", "Select an application to reject.")
                return
            idx = s[0]
            ok, msg = system.set_application_status(idx, "Rejected", user.username)
            if ok:
                messagebox.showinfo("Updated", msg)
                refresh_opps_listboxes()
            else:
                messagebox.showerror("Error", msg)

        # Function to view details of the applicant for a selected application
        def view_selected():
            s = my_app_listbox.curselection()
            if not s:
                messagebox.showwarning("Select", "Select an application to view.")
                return
            idx = s[0]
            apps = system.get_applications_for_recruit(user.username)
            app = apps[idx]
            applicant = system.get_user_by_username(app.username)
            if applicant:
                details = f"Name: {applicant.name}\nEmail: {applicant.email}\nPhone: {applicant.phone}\nAge: {applicant.age}\nUsername: {applicant.username}\nDisabilities: {applicant.disabilities}"
                messagebox.showinfo("Applicant Details", details)
            else:
                messagebox.showerror("Error", "Applicant not found.")

        # Function to process the next pending application
        def process_next():
            app, msg = system.process_next_pending(user.username)
            if app:
                status = simpledialog.askstring("Process Application", f"Application by {app.username} for {app.opportunity_title}. Accept or Reject?")
                if status in ["Accept", "Reject"]:
                    app.status = "Accepted" if status == "Accept" else "Rejected"
                    system.applications.append(app)  # Re-enqueue at end for history
                    system.save()                   # Save updated data
                    messagebox.showinfo("Processed", f"Application marked as {app.status}.")
                    refresh_opps_listboxes()
                else:
                    messagebox.showerror("Invalid", "Enter 'Accept' or 'Reject'.")
            else:
                messagebox.showinfo("None", msg)

        make_button(app_btn_frame, "Accept", accept_selected, width=10).pack(side="left", padx=4)
        make_button(app_btn_frame, "View Applicant Details", view_selected, width=20).pack(side="left", padx=4)
        make_button(app_btn_frame, "Reject", reject_selected, width=10).pack(side="left", padx=4)
        make_button(mid_frame, "Refresh", refresh_opps_listboxes).grid(row=2, column=0, padx=6, pady=6, sticky="w")
        make_button(mid_frame, "Process Next Pending", process_next).grid(row=3, column=0, pady=8, sticky="w")
        make_button(mid_frame, "Logout", dash.destroy).grid(row=3, column=1, pady=8, sticky="e")

# MAIN WINDOW BUTTONS
# Create a frame for main buttons
btn_frame = tk.Frame(root, bg=GREEN_BG)
btn_frame.pack(pady=16)
# Buttons for opening register/login windows and quitting the application
make_button(btn_frame, "Register", open_register_window).grid(row=0, column=0, padx=8)
make_button(btn_frame, "Login", open_login_window).grid(row=0, column=1, padx=8)
make_button(btn_frame, "Quit", root.quit).grid(row=0, column=2, padx=8)

# Start the Tkinter event loop
root.mainloop()
