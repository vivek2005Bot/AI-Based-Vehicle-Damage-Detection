import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_as.dart';
import 'app_localizations_bn.dart';
import 'app_localizations_brx.dart';
import 'app_localizations_doi.dart';
import 'app_localizations_en.dart';
import 'app_localizations_gu.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_kn.dart';
import 'app_localizations_kok.dart';
import 'app_localizations_ks.dart';
import 'app_localizations_mai.dart';
import 'app_localizations_ml.dart';
import 'app_localizations_mni.dart';
import 'app_localizations_mr.dart';
import 'app_localizations_ne.dart';
import 'app_localizations_or.dart';
import 'app_localizations_pa.dart';
import 'app_localizations_sa.dart';
import 'app_localizations_sat.dart';
import 'app_localizations_sd.dart';
import 'app_localizations_ta.dart';
import 'app_localizations_te.dart';
import 'app_localizations_ur.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('as'),
    Locale('bn'),
    Locale('brx'),
    Locale('doi'),
    Locale('en'),
    Locale('gu'),
    Locale('hi'),
    Locale('kn'),
    Locale('kok'),
    Locale('ks'),
    Locale('mai'),
    Locale('ml'),
    Locale('mni'),
    Locale('mr'),
    Locale('ne'),
    Locale('or'),
    Locale('pa'),
    Locale('sa'),
    Locale('sat'),
    Locale('sd'),
    Locale('ta'),
    Locale('te'),
    Locale('ur'),
  ];

  /// Localization key for appTitle
  ///
  /// In en, this message translates to:
  /// **'Vehicle Damage AI'**
  String get appTitle;

  /// Localization key for signIn
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signIn;

  /// Localization key for createAccount
  ///
  /// In en, this message translates to:
  /// **'Create Account'**
  String get createAccount;

  /// Localization key for welcomeBack
  ///
  /// In en, this message translates to:
  /// **'Welcome Back'**
  String get welcomeBack;

  /// Localization key for loginSubtitle
  ///
  /// In en, this message translates to:
  /// **'Sign in to capture inspections, upload telemetry, and generate grounded safety reports.'**
  String get loginSubtitle;

  /// Localization key for registerSubtitle
  ///
  /// In en, this message translates to:
  /// **'Register an inspector account to start vehicle roadworthiness assessments.'**
  String get registerSubtitle;

  /// Localization key for emailLabel
  ///
  /// In en, this message translates to:
  /// **'Email Address'**
  String get emailLabel;

  /// Localization key for emailHint
  ///
  /// In en, this message translates to:
  /// **'inspector@example.com'**
  String get emailHint;

  /// Localization key for passwordLabel
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get passwordLabel;

  /// Localization key for passwordHint
  ///
  /// In en, this message translates to:
  /// **'••••••••••••'**
  String get passwordHint;

  /// Localization key for confirmPasswordLabel
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get confirmPasswordLabel;

  /// Localization key for confirmPasswordHint
  ///
  /// In en, this message translates to:
  /// **'••••••••••••'**
  String get confirmPasswordHint;

  /// Localization key for signInButton
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signInButton;

  /// Localization key for registerButton
  ///
  /// In en, this message translates to:
  /// **'Create Inspector Account'**
  String get registerButton;

  /// Localization key for needAccount
  ///
  /// In en, this message translates to:
  /// **'Need an account? Register here'**
  String get needAccount;

  /// Localization key for alreadyHaveAccount
  ///
  /// In en, this message translates to:
  /// **'Already have an account? Sign In'**
  String get alreadyHaveAccount;

  /// Localization key for forgotPassword
  ///
  /// In en, this message translates to:
  /// **'Forgot Password?'**
  String get forgotPassword;

  /// Localization key for onboardingTitle
  ///
  /// In en, this message translates to:
  /// **'Vehicle Damage & Telemetry AI'**
  String get onboardingTitle;

  /// Localization key for onboardingDesc
  ///
  /// In en, this message translates to:
  /// **'Capture vehicle photos and OBD-II telemetry for AI-assisted damage detection and roadworthiness assessment.'**
  String get onboardingDesc;

  /// Localization key for getStarted
  ///
  /// In en, this message translates to:
  /// **'Get Started'**
  String get getStarted;

  /// Localization key for skip
  ///
  /// In en, this message translates to:
  /// **'Skip'**
  String get skip;

  /// Localization key for permissionsInstruction
  ///
  /// In en, this message translates to:
  /// **'Camera and storage permissions are required to capture vehicle photos and upload telemetry logs.'**
  String get permissionsInstruction;

  /// Localization key for home
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// Localization key for dashboard
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get dashboard;

  /// Localization key for startInspection
  ///
  /// In en, this message translates to:
  /// **'Start Inspection'**
  String get startInspection;

  /// Localization key for inspectionHistory
  ///
  /// In en, this message translates to:
  /// **'Inspection History'**
  String get inspectionHistory;

  /// Localization key for profile
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profile;

  /// Localization key for settings
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// Localization key for save
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// Localization key for cancel
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// Localization key for back
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get back;

  /// Localization key for next
  ///
  /// In en, this message translates to:
  /// **'Next'**
  String get next;

  /// Localization key for retry
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// Localization key for search
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get search;

  /// Localization key for searchHint
  ///
  /// In en, this message translates to:
  /// **'Search by make, model, VIN...'**
  String get searchHint;

  /// Localization key for loading
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// Localization key for emptyInspections
  ///
  /// In en, this message translates to:
  /// **'No inspections found.'**
  String get emptyInspections;

  /// Localization key for success
  ///
  /// In en, this message translates to:
  /// **'Success'**
  String get success;

  /// Localization key for error
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// Localization key for confirm
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get confirm;

  /// Localization key for close
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// Localization key for selectLanguage
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get selectLanguage;

  /// Localization key for serverSettings
  ///
  /// In en, this message translates to:
  /// **'Server Settings'**
  String get serverSettings;

  /// Localization key for backendUrl
  ///
  /// In en, this message translates to:
  /// **'Backend API Base URL'**
  String get backendUrl;

  /// Localization key for updateUrl
  ///
  /// In en, this message translates to:
  /// **'Update URL'**
  String get updateUrl;

  /// Localization key for urlUpdated
  ///
  /// In en, this message translates to:
  /// **'Backend URL updated successfully'**
  String get urlUpdated;

  /// Localization key for logOut
  ///
  /// In en, this message translates to:
  /// **'Log Out'**
  String get logOut;

  /// Localization key for logOutConfirmTitle
  ///
  /// In en, this message translates to:
  /// **'Log Out'**
  String get logOutConfirmTitle;

  /// Localization key for logOutConfirmMessage
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to log out of this device? Local authentication tokens will be removed.'**
  String get logOutConfirmMessage;

  /// Localization key for delete
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// Localization key for newInspectionTitle
  ///
  /// In en, this message translates to:
  /// **'New Inspection'**
  String get newInspectionTitle;

  /// Localization key for vehicleDetails
  ///
  /// In en, this message translates to:
  /// **'Vehicle Details'**
  String get vehicleDetails;

  /// Localization key for vehicleMake
  ///
  /// In en, this message translates to:
  /// **'Make'**
  String get vehicleMake;

  /// Localization key for vehicleModel
  ///
  /// In en, this message translates to:
  /// **'Model'**
  String get vehicleModel;

  /// Localization key for vehicleYear
  ///
  /// In en, this message translates to:
  /// **'Year'**
  String get vehicleYear;

  /// Localization key for vehicleMileage
  ///
  /// In en, this message translates to:
  /// **'Mileage (km / mi)'**
  String get vehicleMileage;

  /// Localization key for vehicleVin
  ///
  /// In en, this message translates to:
  /// **'VIN (Optional)'**
  String get vehicleVin;

  /// Localization key for step1Details
  ///
  /// In en, this message translates to:
  /// **'1. Details'**
  String get step1Details;

  /// Localization key for step2Photos
  ///
  /// In en, this message translates to:
  /// **'2. Photos'**
  String get step2Photos;

  /// Localization key for step3Telemetry
  ///
  /// In en, this message translates to:
  /// **'3. Telemetry'**
  String get step3Telemetry;

  /// Localization key for capturePhotos
  ///
  /// In en, this message translates to:
  /// **'Vehicle Photos'**
  String get capturePhotos;

  /// Localization key for takePhoto
  ///
  /// In en, this message translates to:
  /// **'Take Photo'**
  String get takePhoto;

  /// Localization key for chooseGallery
  ///
  /// In en, this message translates to:
  /// **'Choose from Gallery'**
  String get chooseGallery;

  /// Localization key for noPhotosSelected
  ///
  /// In en, this message translates to:
  /// **'No vehicle photos selected yet.'**
  String get noPhotosSelected;

  /// Localization key for uploadTelemetry
  ///
  /// In en, this message translates to:
  /// **'OBD-II Telemetry Log'**
  String get uploadTelemetry;

  /// Localization key for chooseCsv
  ///
  /// In en, this message translates to:
  /// **'Select CSV File'**
  String get chooseCsv;

  /// Localization key for telemetryOptionalNote
  ///
  /// In en, this message translates to:
  /// **'Optional: Attach OBD-II telemetry CSV for powertrain and sensor diagnostics.'**
  String get telemetryOptionalNote;

  /// Localization key for submitInspection
  ///
  /// In en, this message translates to:
  /// **'Start AI Assessment'**
  String get submitInspection;

  /// Localization key for submittingInspection
  ///
  /// In en, this message translates to:
  /// **'Submitting inspection...'**
  String get submittingInspection;

  /// Localization key for analysisProgressTitle
  ///
  /// In en, this message translates to:
  /// **'Analysis in Progress'**
  String get analysisProgressTitle;

  /// Localization key for processingStageVision
  ///
  /// In en, this message translates to:
  /// **'Detecting exterior vehicle damage with Mask R-CNN...'**
  String get processingStageVision;

  /// Localization key for processingStageObd
  ///
  /// In en, this message translates to:
  /// **'Analyzing telemetry PIDs with Isolation Forest...'**
  String get processingStageObd;

  /// Localization key for processingStageRag
  ///
  /// In en, this message translates to:
  /// **'Retrieving grounded repair & safety standards...'**
  String get processingStageRag;

  /// Localization key for processingStageRules
  ///
  /// In en, this message translates to:
  /// **'Evaluating deterministic roadworthiness rules...'**
  String get processingStageRules;

  /// Localization key for analysisCompleted
  ///
  /// In en, this message translates to:
  /// **'Analysis Complete!'**
  String get analysisCompleted;

  /// Localization key for viewReport
  ///
  /// In en, this message translates to:
  /// **'View Inspection Report'**
  String get viewReport;

  /// Localization key for obdTelemetryTitle
  ///
  /// In en, this message translates to:
  /// **'OBD-II Telemetry & Diagnostic Codes'**
  String get obdTelemetryTitle;

  /// Localization key for telemetryAnalyzed
  ///
  /// In en, this message translates to:
  /// **'Telemetry Analyzed (Isolation Forest)'**
  String get telemetryAnalyzed;

  /// Localization key for noTelemetryProvided
  ///
  /// In en, this message translates to:
  /// **'No OBD-II telemetry log provided with this inspection.'**
  String get noTelemetryProvided;

  /// Localization key for anomalyDetected
  ///
  /// In en, this message translates to:
  /// **'Anomaly Flagged'**
  String get anomalyDetected;

  /// Localization key for flaggedSensors
  ///
  /// In en, this message translates to:
  /// **'Flagged Telemetry Sensors'**
  String get flaggedSensors;

  /// Localization key for activeDtcs
  ///
  /// In en, this message translates to:
  /// **'Active DTC Codes'**
  String get activeDtcs;

  /// Localization key for yes
  ///
  /// In en, this message translates to:
  /// **'YES'**
  String get yes;

  /// Localization key for no
  ///
  /// In en, this message translates to:
  /// **'NO'**
  String get no;

  /// Localization key for diagnosticTroubleCodes
  ///
  /// In en, this message translates to:
  /// **'Diagnostic Trouble Code Explanations'**
  String get diagnosticTroubleCodes;

  /// Localization key for urgency
  ///
  /// In en, this message translates to:
  /// **'Urgency'**
  String get urgency;

  /// Localization key for whatItMeans
  ///
  /// In en, this message translates to:
  /// **'What it means'**
  String get whatItMeans;

  /// Localization key for whatWeFound
  ///
  /// In en, this message translates to:
  /// **'What we found'**
  String get whatWeFound;

  /// Localization key for whatDoesThisMean
  ///
  /// In en, this message translates to:
  /// **'What does this number mean?'**
  String get whatDoesThisMean;

  /// Localization key for howOften
  ///
  /// In en, this message translates to:
  /// **'How often did this happen?'**
  String get howOften;

  /// Localization key for whatShouldYouDo
  ///
  /// In en, this message translates to:
  /// **'What should you do?'**
  String get whatShouldYouDo;

  /// Localization key for symptomsAndCauses
  ///
  /// In en, this message translates to:
  /// **'Symptoms, Causes & Technical Details'**
  String get symptomsAndCauses;

  /// Localization key for possibleCauses
  ///
  /// In en, this message translates to:
  /// **'Possible Causes'**
  String get possibleCauses;

  /// Localization key for possibleSymptoms
  ///
  /// In en, this message translates to:
  /// **'Possible Symptoms'**
  String get possibleSymptoms;

  /// Localization key for technicalDetails
  ///
  /// In en, this message translates to:
  /// **'Technical Details'**
  String get technicalDetails;

  /// Localization key for limitations
  ///
  /// In en, this message translates to:
  /// **'Important Limitations'**
  String get limitations;

  /// Localization key for sourceReference
  ///
  /// In en, this message translates to:
  /// **'Source Reference'**
  String get sourceReference;

  /// Localization key for diagnosticNotice
  ///
  /// In en, this message translates to:
  /// **'Diagnostic Notice'**
  String get diagnosticNotice;

  /// Localization key for outsideMonitoringRange
  ///
  /// In en, this message translates to:
  /// **'Outside Monitoring Range'**
  String get outsideMonitoringRange;

  /// Localization key for reading
  ///
  /// In en, this message translates to:
  /// **'Reading'**
  String get reading;

  /// Localization key for verifiedGuidance
  ///
  /// In en, this message translates to:
  /// **'Verified Repair & Safety Guidance'**
  String get verifiedGuidance;

  /// Localization key for canIKeepDriving
  ///
  /// In en, this message translates to:
  /// **'Can I keep driving?'**
  String get canIKeepDriving;

  /// Localization key for mechanicCheck
  ///
  /// In en, this message translates to:
  /// **'What a mechanic should check'**
  String get mechanicCheck;

  /// Localization key for whyThisMatters
  ///
  /// In en, this message translates to:
  /// **'Why this matters'**
  String get whyThisMatters;

  /// Localization key for roadworthinessStatus
  ///
  /// In en, this message translates to:
  /// **'Roadworthiness Assessment'**
  String get roadworthinessStatus;

  /// Localization key for safeStatus
  ///
  /// In en, this message translates to:
  /// **'SAFE'**
  String get safeStatus;

  /// Localization key for cautionStatus
  ///
  /// In en, this message translates to:
  /// **'CAUTION'**
  String get cautionStatus;

  /// Localization key for unsafeStatus
  ///
  /// In en, this message translates to:
  /// **'UNSAFE'**
  String get unsafeStatus;

  /// Localization key for unavailableStatus
  ///
  /// In en, this message translates to:
  /// **'UNAVAILABLE'**
  String get unavailableStatus;

  /// Localization key for safeDescription
  ///
  /// In en, this message translates to:
  /// **'No critical safety defects detected. Vehicle appears safe for normal operation.'**
  String get safeDescription;

  /// Localization key for cautionDescription
  ///
  /// In en, this message translates to:
  /// **'Advisory items or non-critical anomalies detected. Professional inspection advised.'**
  String get cautionDescription;

  /// Localization key for unsafeDescription
  ///
  /// In en, this message translates to:
  /// **'Critical hazards detected. Driving not recommended until professionally repaired.'**
  String get unsafeDescription;

  /// Localization key for downloadPdf
  ///
  /// In en, this message translates to:
  /// **'Download PDF Report'**
  String get downloadPdf;

  /// Localization key for downloadingPdf
  ///
  /// In en, this message translates to:
  /// **'Downloading PDF report...'**
  String get downloadingPdf;

  /// Localization key for pdfSaved
  ///
  /// In en, this message translates to:
  /// **'PDF Report saved successfully'**
  String get pdfSaved;

  /// Localization key for failedDownloadPdf
  ///
  /// In en, this message translates to:
  /// **'Failed to download PDF report'**
  String get failedDownloadPdf;

  /// Localization key for shareReport
  ///
  /// In en, this message translates to:
  /// **'Share Report'**
  String get shareReport;

  /// Localization key for damageClassScratch
  ///
  /// In en, this message translates to:
  /// **'Scratch'**
  String get damageClassScratch;

  /// Localization key for damageClassDent
  ///
  /// In en, this message translates to:
  /// **'Dent'**
  String get damageClassDent;

  /// Localization key for damageClassBumperSmash
  ///
  /// In en, this message translates to:
  /// **'Bumper Damage'**
  String get damageClassBumperSmash;

  /// Localization key for damageClassGlassCrack
  ///
  /// In en, this message translates to:
  /// **'Glass / Windshield Crack'**
  String get damageClassGlassCrack;

  /// Localization key for damageClassBrokenLight
  ///
  /// In en, this message translates to:
  /// **'Broken Light'**
  String get damageClassBrokenLight;

  /// Localization key for damageClassFlatTire
  ///
  /// In en, this message translates to:
  /// **'Flat / Deflated Tire'**
  String get damageClassFlatTire;

  /// Localization key for damageClassPanelCrush
  ///
  /// In en, this message translates to:
  /// **'Crushed Panel / Structural Damage'**
  String get damageClassPanelCrush;

  /// Localization key for damageSeverityLow
  ///
  /// In en, this message translates to:
  /// **'Low Severity'**
  String get damageSeverityLow;

  /// Localization key for damageSeverityMedium
  ///
  /// In en, this message translates to:
  /// **'Medium Severity'**
  String get damageSeverityMedium;

  /// Localization key for damageSeverityHigh
  ///
  /// In en, this message translates to:
  /// **'High Severity'**
  String get damageSeverityHigh;

  /// Localization key for pleaseEnterEmailAndPassword
  ///
  /// In en, this message translates to:
  /// **'Please enter both email and password.'**
  String get pleaseEnterEmailAndPassword;

  /// Localization key for errorOccurred
  ///
  /// In en, this message translates to:
  /// **'An error occurred. Please try again.'**
  String get errorOccurred;

  /// Localization key for recentInspections
  ///
  /// In en, this message translates to:
  /// **'Recent Inspections'**
  String get recentInspections;

  /// Localization key for allInspections
  ///
  /// In en, this message translates to:
  /// **'All Inspections'**
  String get allInspections;

  /// Localization key for historyTitle
  ///
  /// In en, this message translates to:
  /// **'Inspection History'**
  String get historyTitle;

  /// Localization key for settingsTitle
  ///
  /// In en, this message translates to:
  /// **'Settings & Compliance'**
  String get settingsTitle;

  /// Localization key for reportTitle
  ///
  /// In en, this message translates to:
  /// **'Inspection Report'**
  String get reportTitle;

  /// Localization key for vehicleOdometer
  ///
  /// In en, this message translates to:
  /// **'Odometer'**
  String get vehicleOdometer;

  /// Localization key for emailRequired
  ///
  /// In en, this message translates to:
  /// **'Please enter both email and password.'**
  String get emailRequired;

  /// Localization key for signOut
  ///
  /// In en, this message translates to:
  /// **'Sign Out'**
  String get signOut;

  /// Localization key for signOutSubtitle
  ///
  /// In en, this message translates to:
  /// **'End current session and clear local security tokens'**
  String get signOutSubtitle;

  /// Localization key for logoutConfirmation
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to log out of this device? Local authentication tokens will be removed.'**
  String get logoutConfirmation;

  /// Localization key for settingsAndCompliance
  ///
  /// In en, this message translates to:
  /// **'Settings & Compliance'**
  String get settingsAndCompliance;

  /// Localization key for languageSectionHeader
  ///
  /// In en, this message translates to:
  /// **'APPLICATION LANGUAGE / भाषा'**
  String get languageSectionHeader;

  /// Localization key for languageSettingSubtitle
  ///
  /// In en, this message translates to:
  /// **'Select from English or any of the 22 Scheduled Languages of India. Updates the entire application immediately.'**
  String get languageSettingSubtitle;

  /// Localization key for backendConnection
  ///
  /// In en, this message translates to:
  /// **'BACKEND CONNECTION'**
  String get backendConnection;

  /// Localization key for apiServerUrl
  ///
  /// In en, this message translates to:
  /// **'API Server Base URL'**
  String get apiServerUrl;

  /// Localization key for apiServerUrlSubtitle
  ///
  /// In en, this message translates to:
  /// **'Configure host for local development (e.g., http://localhost:8000 or your LAN IP)'**
  String get apiServerUrlSubtitle;

  /// Localization key for saveEndpoint
  ///
  /// In en, this message translates to:
  /// **'Save Endpoint'**
  String get saveEndpoint;

  /// Localization key for backendUrlUpdated
  ///
  /// In en, this message translates to:
  /// **'Backend URL updated successfully'**
  String get backendUrlUpdated;

  /// Localization key for sessionManagement
  ///
  /// In en, this message translates to:
  /// **'SESSION MANAGEMENT'**
  String get sessionManagement;

  /// Localization key for stepVehicle
  ///
  /// In en, this message translates to:
  /// **'Vehicle'**
  String get stepVehicle;

  /// Localization key for stepPhotos
  ///
  /// In en, this message translates to:
  /// **'Photos'**
  String get stepPhotos;

  /// Localization key for stepObd
  ///
  /// In en, this message translates to:
  /// **'OBD-II'**
  String get stepObd;

  /// Localization key for stepReview
  ///
  /// In en, this message translates to:
  /// **'Review'**
  String get stepReview;

  /// Localization key for submitAndAnalyze
  ///
  /// In en, this message translates to:
  /// **'Submit for Analysis'**
  String get submitAndAnalyze;

  /// Localization key for newInspection
  ///
  /// In en, this message translates to:
  /// **'New Vehicle Inspection'**
  String get newInspection;

  /// Localization key for startNewInspection
  ///
  /// In en, this message translates to:
  /// **'Start New Inspection'**
  String get startNewInspection;

  /// Localization key for aiInspectionCapabilities
  ///
  /// In en, this message translates to:
  /// **'AI Inspection Capabilities'**
  String get aiInspectionCapabilities;

  /// Localization key for stage1Filter
  ///
  /// In en, this message translates to:
  /// **'Stage 1 Filter'**
  String get stage1Filter;

  /// Localization key for objectDetection
  ///
  /// In en, this message translates to:
  /// **'Object Detection'**
  String get objectDetection;

  /// Localization key for obdAnomaly
  ///
  /// In en, this message translates to:
  /// **'OBD Anomaly'**
  String get obdAnomaly;

  /// Localization key for ragStandards
  ///
  /// In en, this message translates to:
  /// **'RAG Standards'**
  String get ragStandards;

  /// Localization key for viewAll
  ///
  /// In en, this message translates to:
  /// **'View All'**
  String get viewAll;

  /// Localization key for noInspectionsYet
  ///
  /// In en, this message translates to:
  /// **'No inspections yet'**
  String get noInspectionsYet;

  /// Localization key for noInspectionsSubtitle
  ///
  /// In en, this message translates to:
  /// **'Tap \"Start New Inspection\" above to photograph a vehicle and run the AI assessment.'**
  String get noInspectionsSubtitle;

  /// Localization key for statusSafe
  ///
  /// In en, this message translates to:
  /// **'SAFE'**
  String get statusSafe;

  /// Localization key for statusCaution
  ///
  /// In en, this message translates to:
  /// **'CAUTION'**
  String get statusCaution;

  /// Localization key for statusUnsafe
  ///
  /// In en, this message translates to:
  /// **'UNSAFE'**
  String get statusUnsafe;

  /// Localization key for statusReviewNeeded
  ///
  /// In en, this message translates to:
  /// **'REVIEW NEEDED'**
  String get statusReviewNeeded;

  /// Localization key for statusProcessing
  ///
  /// In en, this message translates to:
  /// **'PROCESSING'**
  String get statusProcessing;

  /// Localization key for allInspectionsFilter
  ///
  /// In en, this message translates to:
  /// **'All Inspections'**
  String get allInspectionsFilter;

  /// Localization key for noMatchingInspections
  ///
  /// In en, this message translates to:
  /// **'No matching inspections found'**
  String get noMatchingInspections;

  /// Localization key for processingInspection
  ///
  /// In en, this message translates to:
  /// **'Processing Inspection'**
  String get processingInspection;

  /// Localization key for pipelineRunning
  ///
  /// In en, this message translates to:
  /// **'AI Multi-Agent Pipeline Running'**
  String get pipelineRunning;

  /// Localization key for pipelineSubtitle
  ///
  /// In en, this message translates to:
  /// **'Our LangGraph supervisor is coordinating specialist agents across vision, telemetry, and safety standards.'**
  String get pipelineSubtitle;

  /// Localization key for pipelineFailed
  ///
  /// In en, this message translates to:
  /// **'Analysis pipeline failed on server. Please check inputs and retry.'**
  String get pipelineFailed;

  /// Localization key for backToHome
  ///
  /// In en, this message translates to:
  /// **'Back to Home'**
  String get backToHome;

  /// Localization key for stageValidation
  ///
  /// In en, this message translates to:
  /// **'Input Validation & Preprocessing'**
  String get stageValidation;

  /// Localization key for stageVision
  ///
  /// In en, this message translates to:
  /// **'4-Stage Vision Cascade (Filter, Detect, Segment)'**
  String get stageVision;

  /// Localization key for stageObd
  ///
  /// In en, this message translates to:
  /// **'OBD-II Telemetry & DTC Anomaly Detection'**
  String get stageObd;

  /// Localization key for stageRAG
  ///
  /// In en, this message translates to:
  /// **'RAG Knowledge Standards Retrieval'**
  String get stageRAG;

  /// Localization key for stageReport
  ///
  /// In en, this message translates to:
  /// **'Risk Engine & Report Generation'**
  String get stageReport;

  /// Localization key for inspectionFindingsReport
  ///
  /// In en, this message translates to:
  /// **'Inspection Findings & Report'**
  String get inspectionFindingsReport;

  /// Localization key for exportInspectionReport
  ///
  /// In en, this message translates to:
  /// **'Export Inspection Report'**
  String get exportInspectionReport;

  /// Localization key for downloadPdfReport
  ///
  /// In en, this message translates to:
  /// **'Download & Share PDF Report'**
  String get downloadPdfReport;

  /// Localization key for downloadPdfSubtitle
  ///
  /// In en, this message translates to:
  /// **'Printable document with findings, charts, and citations'**
  String get downloadPdfSubtitle;

  /// Localization key for exportJsonData
  ///
  /// In en, this message translates to:
  /// **'Export JSON Data Payload'**
  String get exportJsonData;

  /// Localization key for exportJsonSubtitle
  ///
  /// In en, this message translates to:
  /// **'Machine-readable telemetry & computer vision coordinates'**
  String get exportJsonSubtitle;

  /// Localization key for retryLoadingReport
  ///
  /// In en, this message translates to:
  /// **'Retry Loading Report'**
  String get retryLoadingReport;

  /// Localization key for exteriorVisualFindings
  ///
  /// In en, this message translates to:
  /// **'Exterior Visual Findings'**
  String get exteriorVisualFindings;

  /// Localization key for noImagesProcessed
  ///
  /// In en, this message translates to:
  /// **'No images were processed.'**
  String get noImagesProcessed;

  /// Localization key for obdTelemetryFindings
  ///
  /// In en, this message translates to:
  /// **'OBD-II Telemetry & DTC Findings'**
  String get obdTelemetryFindings;

  /// Localization key for groundedSafetyGuidance
  ///
  /// In en, this message translates to:
  /// **'Grounded Safety & Repair Guidance'**
  String get groundedSafetyGuidance;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>[
    'as',
    'bn',
    'brx',
    'doi',
    'en',
    'gu',
    'hi',
    'kn',
    'kok',
    'ks',
    'mai',
    'ml',
    'mni',
    'mr',
    'ne',
    'or',
    'pa',
    'sa',
    'sat',
    'sd',
    'ta',
    'te',
    'ur',
  ].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'as':
      return AppLocalizationsAs();
    case 'bn':
      return AppLocalizationsBn();
    case 'brx':
      return AppLocalizationsBrx();
    case 'doi':
      return AppLocalizationsDoi();
    case 'en':
      return AppLocalizationsEn();
    case 'gu':
      return AppLocalizationsGu();
    case 'hi':
      return AppLocalizationsHi();
    case 'kn':
      return AppLocalizationsKn();
    case 'kok':
      return AppLocalizationsKok();
    case 'ks':
      return AppLocalizationsKs();
    case 'mai':
      return AppLocalizationsMai();
    case 'ml':
      return AppLocalizationsMl();
    case 'mni':
      return AppLocalizationsMni();
    case 'mr':
      return AppLocalizationsMr();
    case 'ne':
      return AppLocalizationsNe();
    case 'or':
      return AppLocalizationsOr();
    case 'pa':
      return AppLocalizationsPa();
    case 'sa':
      return AppLocalizationsSa();
    case 'sat':
      return AppLocalizationsSat();
    case 'sd':
      return AppLocalizationsSd();
    case 'ta':
      return AppLocalizationsTa();
    case 'te':
      return AppLocalizationsTe();
    case 'ur':
      return AppLocalizationsUr();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
