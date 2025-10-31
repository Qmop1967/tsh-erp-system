# PRSS Technician Mobile App

Flutter mobile application for field technicians to handle maintenance jobs and inspections.

## Features

- 📱 Scan serial numbers with QR code
- 🔧 Manage maintenance jobs
- 📸 Capture photos and notes
- ✅ Complete job cards
- 🔄 Offline sync support

## Getting Started

### Prerequisites

- Flutter SDK 3.0+
- Dart 3.0+
- Android Studio / VS Code
- Android device or emulator

### Installation

```bash
cd apps/prss/mobile-tech
flutter pub get
flutter run
```

### Build

```bash
# Android
flutter build apk

# iOS
flutter build ios
```

## Configuration

Update `lib/config/api_config.dart` with your API base URL:

```dart
const String apiBaseUrl = 'http://your-server:8001/v1';
```

## Architecture

```
lib/
├── main.dart
├── config/
├── models/
├── services/
├── screens/
└── widgets/
```

## Login

Default credentials for testing:
- Username: `technician`
- Password: `tech123`
