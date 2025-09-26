# TSH Admin Application

## Overview
The TSH Admin Application is a mobile application designed for administrators to manage the TSH ERP system efficiently. Built using React Native, this application provides a user-friendly interface for controlling various aspects of the ERP system from your mobile device.

## Features
- **API Integration**: Seamlessly interact with the TSH ERP backend using the provided API functions.
- **Reusable Components**: Utilize a library of reusable UI components to ensure a consistent look and feel throughout the application.
- **Navigation**: Easy navigation between different screens, including the Admin Dashboard, Settings, and Home.
- **State Management**: Manage application state effectively using Redux or Context API.
- **TypeScript Support**: Leverage TypeScript for type safety and better development experience.

## Project Structure
```
tsh-admin-app
├── src
│   ├── api               # API calls to the TSH ERP system
│   ├── components        # Reusable UI components
│   ├── navigation        # Navigation setup
│   ├── screens           # Main application screens
│   ├── store             # State management
│   └── types             # TypeScript interfaces and types
├── App.tsx               # Main entry point of the application
├── babel.config.js       # Babel configuration
├── index.js              # React Native entry point
├── metro.config.js       # Metro bundler configuration
├── package.json          # npm configuration
├── tsconfig.json         # TypeScript configuration
└── README.md             # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd tsh-admin-app
   ```
3. Install dependencies:
   ```
   npm install
   ```

## Running the Application
To run the application on your mobile device or emulator, use the following command:
```
npm start
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.