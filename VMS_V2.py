import tkinter as tk
from tkinter import messagebox, simpledialog

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
    """Manages users, opportunities and applications (in-memory)."""
    def __init__(self):
        self.users = []          # List to store all registered users
        self.opportunities = []  # List to store all volunteer opportunities
        self.applications = []   # List to store all volunteer applications

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

        # Create user based on role
        if role == "Volunteer":
            user = Volunteer(name, email, phone, age, username, password, disabilities)
        elif role == "Recruit":
            user = Recruit(name, email, phone, age, username, password, disabilities)
        else:
            return None, "Invalid role selected."

        self.users.append(user)  # Add user to the users list
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
        return opp                     # Returns the created opportunity

    # Returns a copy of all opportunities
    def get_opportunities(self):
        return self.opportunities.copy()

    # Allows a volunteer to apply for an opportunity
    def apply_to_opportunity(self, volunteer: Volunteer, opp_index):
        if opp_index < 0 or opp_index >= len(self.opportunities):
            return None, "Invalid opportunity selection."
        opp = self.opportunities[opp_index]
        # Check for duplicate applications
        if any(app.username == volunteer.username and app.opportunity_title == opp.title for app in self.applications):
            return None, "You have already applied for this opportunity."
        app = volunteer.apply(opp)        # Create application via Volunteer class
        self.applications.append(app)     # Add application to system list
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
        return True, f"Application by {target.username} marked as {new_status}."

    # Retrieves a user by their username
    def get_user_by_username(self, username):
        for u in self.users:
            if u.username == username:
                return u
        return None

# GUI IMPLEMENTATION USING TKINTER
# Create the main VolunteerSystem instance
system = VolunteerSystem()

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Volunteering Management System")
root.geometry("520x360")  # Set window size
title_label = tk.Label(root, text="Volunteering Management System", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# REGISTER WINDOW
# Opens a new window for user registration
def open_register_window():
    reg = tk.Toplevel(root)  # Create a new top-level window
    reg.title("Register")
    reg.geometry("420x520")  # Set window size
    tk.Label(reg, text="Register", font=("Arial", 14, "bold")).pack(pady=8)

    # Create entry fields for registration details
    tk.Label(reg, text="Full name").pack(anchor="w", padx=12)
    entry_name = tk.Entry(reg, width=40); entry_name.pack(padx=12, pady=2)
    tk.Label(reg, text="Email").pack(anchor="w", padx=12)
    entry_email = tk.Entry(reg, width=40); entry_email.pack(padx=12, pady=2)
    tk.Label(reg, text="Phone").pack(anchor="w", padx=12)
    entry_phone = tk.Entry(reg, width=40); entry_phone.pack(padx=12, pady=2)
    tk.Label(reg, text="Age").pack(anchor="w", padx=12)
    entry_age = tk.Entry(reg, width=40); entry_age.pack(padx=12, pady=2)
    tk.Label(reg, text="Username").pack(anchor="w", padx=12)
    entry_username = tk.Entry(reg, width=40); entry_username.pack(padx=12, pady=2)
    tk.Label(reg, text="Password").pack(anchor="w", padx=12)
    entry_password = tk.Entry(reg, show="*", width=40); entry_password.pack(padx=12, pady=2)
    tk.Label(reg, text="Confirm Password").pack(anchor="w", padx=12)
    entry_confirm = tk.Entry(reg, show="*", width=40); entry_confirm.pack(padx=12, pady=2)
    tk.Label(reg, text="Disabilities (if any)").pack(anchor="w", padx=12)
    entry_disabilities = tk.Entry(reg, width=40); entry_disabilities.pack(padx=12, pady=2)
    tk.Label(reg, text="Role").pack(anchor="w", padx=12)
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
    tk.Button(reg, text="Register", width=18, command=submit_registration).pack(pady=10)
    tk.Button(reg, text="Close", width=10, command=reg.destroy).pack()

# LOGIN WINDOW
# Opens a new window for user login
def open_login_window():
    login = tk.Toplevel(root)  # Create a new top-level window
    login.title("Login")
    login.geometry("360x220")  # Set window size
    tk.Label(login, text="Login", font=("Arial", 14, "bold")).pack(pady=8)
    tk.Label(login, text="Username").pack(anchor="w", padx=12)
    entry_username = tk.Entry(login, width=34); entry_username.pack(padx=12, pady=2)
    tk.Label(login, text="Password").pack(anchor="w", padx=12)
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
    tk.Button(login, text="Login", width=14, command=submit_login).pack(pady=6)
    tk.Button(login, text="Close", width=8, command=login.destroy).pack()

# DASHBOARD WINDOWS
# Opens a role-specific dashboard for the logged-in user
def open_dashboard(user):
    dash = tk.Toplevel(root)  # Create a new top-level window
    dash.title(f"{user.role} Dashboard - {user.username}")
    dash.geometry("700x520")  # Set window size
    header = tk.Label(dash, text=f"{user.role} Dashboard", font=("Arial", 14, "bold"))
    header.pack(pady=8)

    # VOLUNTEER DASHBOARD
    if user.role == "Volunteer":
        left = tk.Frame(dash)
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(left, text="Available Opportunities:", font=("Arial", 11, "bold")).pack(anchor="w")
        opp_listbox = tk.Listbox(left, width=50, height=18)
        opp_listbox.pack(padx=6, pady=6)
        tk.Label(left, text="Description:", font=("Arial", 11, "bold")).pack(anchor="w")
        desc_text = tk.Text(left, width=50, height=5, wrap="word")
        desc_text.pack(padx=6, pady=6)

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
                desc_text.delete("1.0", tk.END)
                desc_text.insert(tk.END, opp.description)

        opp_listbox.bind("<<ListboxSelect>>", show_description)

        right = tk.Frame(dash)
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

        tk.Button(right, text="Apply to Selected Opportunity", width=28, command=apply_selected).pack(pady=6)
        tk.Label(right, text="My Applications:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(18, 4))
        apps_listbox = tk.Listbox(right, width=40, height=12)
        apps_listbox.pack(padx=6, pady=6)

        # Function to refresh the applications listbox
        def refresh_apps():
            apps_listbox.delete(0, tk.END)
            for app in [a for a in system.applications if a.username == user.username]:
                apps_listbox.insert(tk.END, f"{app.opportunity_title} - {app.status}")

        refresh_apps()

        tk.Button(right, text="Refresh Opportunities", command=refresh_opps).pack(pady=4)
        tk.Button(right, text="Refresh My Applications", command=refresh_apps).pack(pady=4)
        tk.Button(right, text="Logout", command=dash.destroy).pack(pady=12)

    # RECRUIT DASHBOARD
    elif user.role == "Recruit":
        create_frame = tk.LabelFrame(dash, text="Create Opportunity", padx=8, pady=8)
        create_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(create_frame, text="Title").grid(row=0, column=0, sticky="w")
        e_title = tk.Entry(create_frame, width=60); e_title.grid(row=0, column=1, pady=2)
        tk.Label(create_frame, text="Location").grid(row=1, column=0, sticky="w")
        e_location = tk.Entry(create_frame, width=60); e_location.grid(row=1, column=1, pady=2)
        tk.Label(create_frame, text="Date").grid(row=2, column=0, sticky="w")
        e_date = tk.Entry(create_frame, width=60); e_date.grid(row=2, column=1, pady=2)
        tk.Label(create_frame, text="Description").grid(row=3, column=0, sticky="nw")
        e_desc = tk.Text(create_frame, width=45, height=4); e_desc.grid(row=3, column=1, pady=4)

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

        tk.Button(create_frame, text="Post Opportunity", command=submit_opportunity).grid(row=4, column=1, sticky="e", pady=6)

        mid_frame = tk.LabelFrame(dash, text="Your Opportunities & Applications", padx=8, pady=8)
        mid_frame.pack(fill="both", expand=True, padx=10, pady=8)
        tk.Label(mid_frame, text="Your Opportunities:").grid(row=0, column=0, sticky="w")
        my_opp_listbox = tk.Listbox(mid_frame, width=40, height=8)
        my_opp_listbox.grid(row=1, column=0, padx=6, pady=4)
        tk.Label(mid_frame, text="Applications to your opportunities:").grid(row=0, column=1, sticky="w", padx=8)
        my_app_listbox = tk.Listbox(mid_frame, width=48, height=8)
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

        app_btn_frame = tk.Frame(mid_frame)
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

        tk.Button(app_btn_frame, text="Accept Selected Application", command=accept_selected).pack(side="left", padx=4)
        tk.Button(app_btn_frame, text="View Applicant Details", command=view_selected).pack(side="left", padx=4)
        tk.Button(app_btn_frame, text="Reject Selected Application", command=reject_selected).pack(side="left", padx=4)
        tk.Button(mid_frame, text="Refresh", command=refresh_opps_listboxes).grid(row=2, column=0, padx=6, pady=6, sticky="w")
        tk.Button(mid_frame, text="Logout", command=dash.destroy).grid(row=3, column=1, pady=8, sticky="e")

# MAIN WINDOW BUTTONS
# Create a frame for main buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=16)
# Buttons for opening register/login windows and quitting the application
tk.Button(btn_frame, text="Register", width=16, command=open_register_window).grid(row=0, column=0, padx=8)
tk.Button(btn_frame, text="Login", width=16, command=open_login_window).grid(row=0, column=1, padx=8)
tk.Button(btn_frame, text="Quit", width=16, command=root.quit).grid(row=0, column=2, padx=8)

# Start the Tkinter event loop
root.mainloop()
