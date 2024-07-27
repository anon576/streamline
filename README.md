
# Streamline

Streamline is a Flask-based web application for selling and managing online courses. It offers an intuitive platform for users to browse, purchase, and enroll in courses, while providing course creators and admins with tools to manage their offerings efficiently.

## Features

- **Course Catalog**: Browse a wide range of online courses.
- **Course Enrollment**: Purchase and enroll in courses seamlessly.
- **Admin Dashboard**: Create, manage, and remove courses from the admin panel.
- **User Authentication**: Secure login and registration for users and administrators.
- **Payment Integration**: Process payments for course purchases.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/anon576/streamline.git
   ```

2. **Navigate to the Project Directory:**
   ```bash
   cd streamline
   ```

3. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment:**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set Up the Database:**
   ```bash
   flask db upgrade
   ```

7. **Run the Application:**
   ```bash
   flask run
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.


## Usage

- **Register/Log In**: Sign up or log in to access the platform.
- **Browse Courses**: Explore the course catalog and view details.
- **Enroll in Courses**: Purchase and enroll in courses from the course pages.
- **Admin Management**: Admins can manage courses and users from the admin dashboard.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
