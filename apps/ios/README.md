# Vehicle Damage AI — Native iOS Flutter Client

The mobile frontend for the **AI-Based Vehicle Damage Detection & Roadworthiness Assessment** platform. Built with Flutter 3.x and Dart 3.x, optimized for iOS 16.0+ devices and the Apple iOS Simulator.

---

## Features

- **Multi-Image Vehicle Capture:** High-resolution camera capture and photo gallery selection with native iOS image picker.
- **OBD-II CSV Upload:** Ingest automotive sensor and trouble code logs directly from mobile storage.
- **Interactive Overlay Viewer:** High-performance 2D `CustomPainter` rendering calibrated bounding boxes, sub-pixel polygon masks, and color-coded damage chips (`bumper_smash`, `broken_light`, `glass_crack`, `dent`, `scratch`, `flat_tire`).
- **Deterministic Risk Banner:** Displays full-width roadworthiness grading (`SAFE`, `CAUTION`, `UNSAFE`).
- **23-Language Accessibility:** Instant UI language selection across English and all 22 Eighth Schedule languages of India with persistent preferences and Right-to-Left (RTL) support.
- **Native PDF Export:** Streams and displays executive inspection reports via the native iOS share sheet.

---

## Getting Started

### 1. Prerequisites
- macOS host with Xcode 15+ installed
- Flutter SDK 3.27+ (`flutter --version`)
- Running FastAPI backend server (`http://127.0.0.1:8000`)

### 2. Run the App
```bash
# 1. Install Flutter dependencies
flutter pub get

# 2. Compile localization ARB dictionaries
flutter gen-l10n

# 3. Open iOS Simulator
open -a Simulator

# 4. Launch on Simulator
flutter run
```

### 3. Testing and Static Analysis
```bash
# Static analysis (verifies 0 errors, 0 warnings)
flutter analyze

# Widget & Unit test suite
flutter test
```

---

## Configuration

The backend API URL defaults to `http://127.0.0.1:8000` for the iOS Simulator. To configure a remote server or local network IP, open the **Settings** screen within the app and update the API Base URL.
