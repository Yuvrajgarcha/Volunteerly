# Defines a base class Person to store common attributes for all user types
class Person:
# Initializes a Person object with name, email, phone, age, username, password, and role
    def __init__(self, name, email, phone, age, username, password, role):
        self.name = name           # Stores full name
        self.email = email         # Stores email address
        self.phone = phone         # Stores phone number
        self.age = int(age)        # Converts age to integer and stores it
        self.username = username    # Stores unique username
        self.password = password    # Stores password 
        self.role = role           # Stores user role 


# Volunteer class inherits from Person, representing users who apply for opportunities
class Volunteer(Person):
    # Constructor initializes Volunteer with Person attributes and sets role to "Volunteer"
    def __init__(self, name, email, phone, age, username, password):
        super().__init__(name, email, phone, age, username, password, role="Volunteer")
        self.my_applications = []  # Initializes an empty list to store the volunteer's applications

    # Method to apply for a volunteer opportunity
    def apply(self, opportunity, disability_info):
        # Creates a new VolunteerApplication object with username, opportunity title, posted_by, and disability info
        app = VolunteerApplication(self.username, opportunity.title, opportunity.posted_by, disability_info)
        self.my_applications.append(app)  # Adds application to volunteer's list
        return app                        # Returns the created application


# Recruit class inherits from Person, representing users who manage applications
class Recruit(Person):
    # Constructor initializes Recruit with Person attributes and sets role to "Recruit"
    def __init__(self, name, email, phone, age, username, password):
        super().__init__(name, email, phone, age, username, password, role="Recruit")


# Lister class inherits from Person, representing users who post volunteer opportunities
class Lister(Person):
    # Constructor initializes Lister with Person attributes and sets role to "Lister"
    def __init__(self, name, email, phone, age, username, password):
        super().__init__(name, email, phone, age, username, password, role="Lister")


# Class to represent a volunteer opportunity
class VolunteerOpportunity:
    # Constructor initializes an opportunity with title, description, location, date, and the username of the poster
    def __init__(self, title, description, location, date, posted_by):
        self.title = title             # Stores opportunity title
        self.description = description # Stores opportunity description
        self.location = location       # Stores opportunity location
        self.date = date               # Stores opportunity date
        self.posted_by = posted_by     # Stores username of the user who posted the opportunity


# Class to represent a volunteer application
class VolunteerApplication:
    # Constructor initializes an application with username, opportunity title, posted_by, and disability info
    def __init__(self, username, opportunity_title, posted_by, disability_info):
        self.username = username                # Stores applicant's username
        self.opportunity_title = opportunity_title  # Stores title of the opportunity
        self.posted_by = posted_by             # Stores username of the opportunity poster
        self.disability_info = disability_info  # Stores disability information (or "No")
        self.status = "Pending"                # Sets initial application status to "Pending"
        self.notified = False                  # Tracks if applicant has been notified of status change


# Main class to manage the volunteer system
class VolunteerSystem:
    # Constructor initializes empty lists for users, opportunities, and applications
    def __init__(self):
        self.users = []          # List to store all registered users
        self.opportunities = []  # List to store all volunteer opportunities
        self.applications = []   # List to store all volunteer applications

    # VALIDATION METHODS
    # Checks if a username already exists in the system
    def username_exists(self, username):
        return any(u.username == username for u in self.users)  # Returns True if username is taken

    # Validates name (allows only letters and spaces)
    def valid_name(self, name):
        return name.replace(" ", "").isalpha()  # Removes spaces and checks if remaining characters are letters

    # Validates email (basic check for '@' and '.com')
    def valid_email(self, email):
        return "@" in email and email.endswith(".com")  # Ensures email contains '@' and ends with '.com'

    # Validates phone number (allows only digits)
    def valid_phone(self, phone):
        return phone.isdigit()  # Checks if phone contains only numbers

    # Validates age (must be between 17 and 99)
    def valid_age(self, age):
        try:
            age = int(age)      # Attempts to convert age to integer
            return 16 < age < 100  # Checks if age is within valid range
        except ValueError:
            return False        # Returns False if age is not a valid integer

    # Validates password (at least 6 characters, includes at least one digit)
    def valid_password(self, password):
        return len(password) >= 6 and any(char.isdigit() for char in password)

    # REGISTRATION
    # Handles user registration process
    def register(self):
        print("\nRegister ")

        # Get and validate full name
        name = input("Full name: ")
        while not self.valid_name(name):
            print("Invalid name. Name must contain only letters and spaces.")
            name = input("Full name: ")

        # Get and validate email
        email = input("Email: ")
        while not self.valid_email(email):
            print("Invalid email. Must include '@' and end with '.com'.")
            email = input("Email: ")

        # Get and validate phone number
        phone = input("Phone: ")
        while not self.valid_phone(phone):
            print("Invalid phone number. Must contain only digits.")
            phone = input("Phone: ")

        # Get and validate age
        age = input("Age: ")
        while not self.valid_age(age):
            print("Invalid age. Must be between 17 and 99.")
            age = input("Age: ")

        # Get and validate username
        username = input("Choose a username: ")
        if self.username_exists(username):
            print("Username already exists.")
            return

        # Get and validate password
        password = input("Password: ")
        while not self.valid_password(password):
            print("Invalid password. Must be at least 6 characters long and include at least one number.")
            password = input("Password: ")

        # Confirm password
        confirm_pw = input("Confirm password: ")
        if confirm_pw != password:
            print("Passwords do not match.")
            return

        # Get and validate role, create appropriate user object
        role = input("Role (Volunteer / Recruit / Lister): ").capitalize()
        if role == "Volunteer":
            user = Volunteer(name, email, phone, age, username, password)
        elif role == "Recruit":
            user = Recruit(name, email, phone, age, username, password)
        elif role == "Lister":
            user = Lister(name, email, phone, age, username, password)
        else:
            print("Invalid role.")
            return

        self.users.append(user)  # Add new user to the users list
        print(f"Registered successfully as {role}!")

    # LOGIN
    # Handles user login process
    def login(self):
        print("\n Login ")
        username = input("Username: ")
        password = input("Password: ")
        for u in self.users:
            if u.username == username and u.password == password:
                print(f"Welcome back, {u.name}! ({u.role})")
                return u  # Returns user object if credentials match
        print("Invalid username or password.")
        return None   # Returns None if login fails

    # LISTER FUNCTIONALITY
    # Allows Lister to post a new volunteer opportunity
    def post_opportunity(self, user):
        print("\n Post Opportunity")
        title = input("Title: ")
        desc = input("Description: ")
        loc = input("Location: ")
        date = input("Date: ")
        opp = VolunteerOpportunity(title, desc, loc, date, user.username)
        self.opportunities.append(opp)  # Adds opportunity to the opportunities list
        print("Opportunity posted successfully!")

    # VOLUNTEER FUNCTIONALITY
    # Displays all available volunteer opportunities
    def view_opportunities(self):
        print("\nAvailable Opportunities")
        if not self.opportunities:
            print("No opportunities available.")
            return False
        for i, o in enumerate(self.opportunities, 1):
            print(f"[{i}] {o.title} - {o.location} ({o.date}) | Posted by {o.posted_by}")
        return True

    # Allows Volunteer to apply for an opportunity
    def apply_to_opportunity(self, user):
        if not self.view_opportunities():  # Check if opportunities exist
            return
        try:
            choice = int(input("Select opportunity number: ")) - 1
            if choice < 0 or choice >= len(self.opportunities):
                print("Invalid choice.")
                return
            opp = self.opportunities[choice]  # Get selected opportunity
            disability = input("Do you have any disabilities? (Describe or type 'No'): ")
            app = user.apply(opp, disability)  # Create application via Volunteer class
            self.applications.append(app)      # Add application to system list
            print(f"Applied for '{opp.title}' successfully!")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # RECRUIT FUNCTIONALITY
    # Displays all volunteer applications
    def view_applications(self):
        print("\nVolunteer Applications")
        if not self.applications:
            print("No applications available.")
            return False
        for i, a in enumerate(self.applications, 1):
            print(f"[{i}] {a.username} applied for {a.opportunity_title} "
                  f"[{a.status}] | Disability: {a.disability_info}")
        return True

    # Allows Recruit to update application status
    def update_application_status(self):
        if not self.view_applications():  # Check if applications exist
            return
        try:
            idx = int(input("Select application number to update: ")) - 1
            if idx < 0 or idx >= len(self.applications):
                print("Invalid choice.")
                return
            new_status = input("Enter new status (Approved/Rejected): ").capitalize()
            if new_status not in ["Approved", "Rejected"]:
                print("Invalid status.")
                return
            app = self.applications[idx]
            app.status = new_status  # Update application status
            # Notify the applicant 
            for user in self.users:
                if isinstance(user, Volunteer) and user.username == app.username and not app.notified:
                    print(f"Notification to {user.name}: Your application for '{app.opportunity_title}' has been {new_status.lower()}. ")
                    app.notified = True  # Mark as notified
            print(f"Application updated to '{new_status}'.")
        except ValueError:
            print("Invalid input.")

    # DASHBOARDS
    # Volunteer dashboard for managing opportunities and applications
    def volunteer_dashboard(self, user):
        while True:
            print("\n Volunteer Dashboard ")
            print("1. View Opportunities")
            print("2. Apply for Opportunity")
            print("3. View My Applications")
            print("4. Logout")
            choice = input("Select option: ")
            if choice == "1":
                self.view_opportunities()  # Show available opportunities
            elif choice == "2":
                self.apply_to_opportunity(user)  # Apply for an opportunity
            elif choice == "3":
                print("\nYour Applications")
                for app in user.my_applications:
                    print(f"- {app.opportunity_title} [Status: {app.status}] | Disability Info: {app.disability_info}")
            elif choice == "4":
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

    # Recruit dashboard for managing applications
    def recruit_dashboard(self, user):
        while True:
            print("\n Recruit Dashboard")
            print("1. View Applications")
            print("2. Update Application Status")
            print("3. Logout")
            choice = input("Select option: ")
            if choice == "1":
                self.view_applications()  # Show all applications
            elif choice == "2":
                self.update_application_status()  # Update application status
            elif choice == "3":
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

    # Lister dashboard for managing opportunities
    def lister_dashboard(self, user):
        while True:
            print("\n Lister Dashboard ")
            print("1. Post Opportunity")
            print("2. View My Opportunities")
            print("3. Logout")
            choice = input("Select option: ")
            if choice == "1":
                self.post_opportunity(user)  # Post a new opportunity
            elif choice == "2":
                print(f"\n {user.username}'s Opportunities ")
                listed = [o for o in self.opportunities if o.posted_by == user.username]
                if not listed:
                    print("No opportunities posted yet.")
                else:
                    for o in listed:
                        print(f"- {o.title} ({o.date}) at {o.location}")
            elif choice == "3":
                print("Logging out...")
                break
            else:
                print("Invalid choice.")


# MAIN PROGRAM LOOP
# Main function to run the volunteer management system
def main():
    system = VolunteerSystem()  # Create a new VolunteerSystem instance
    while True:
        print("\nVOLUNTEER MANAGEMENT SYSTEM")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            system.register()  # Run registration process
        elif choice == "2":
            user = system.login()  # Run login process
            if user:
                if user.role == "Volunteer":
                    system.volunteer_dashboard(user)  # Open volunteer dashboard
                elif user.role == "Recruit":
                    system.recruit_dashboard(user)    # Open recruit dashboard
                elif user.role == "Lister":
                    system.lister_dashboard(user)     # Open lister dashboard
        elif choice == "3":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid option.")


# Entry point of the program
if __name__ == "__main__":
    main()  # Run the main function
s
