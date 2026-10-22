// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Urdu (`ur`).
class AppLocalizationsUr extends AppLocalizations {
  AppLocalizationsUr([String locale = 'ur']) : super(locale);

  @override
  String get appTitle => 'Vehicle Damage AI (اردو)';

  @override
  String get signIn => 'سائن ان کریں';

  @override
  String get createAccount => 'اکاؤنٹ بنائیں';

  @override
  String get welcomeBack => 'خوش آمدید';

  @override
  String get loginSubtitle =>
      'Sign in to capture inspections, upload telemetry, and generate grounded safety reports.';

  @override
  String get registerSubtitle =>
      'Register an inspector account to start vehicle roadworthiness assessments.';

  @override
  String get emailLabel => 'Email Address';

  @override
  String get emailHint => 'inspector@example.com';

  @override
  String get passwordLabel => 'Password';

  @override
  String get passwordHint => '••••••••••••';

  @override
  String get confirmPasswordLabel => 'Confirm Password';

  @override
  String get confirmPasswordHint => '••••••••••••';

  @override
  String get signInButton => 'Sign In';

  @override
  String get registerButton => 'Create Inspector Account';

  @override
  String get needAccount => 'Need an account? Register here';

  @override
  String get alreadyHaveAccount => 'Already have an account? Sign In';

  @override
  String get forgotPassword => 'Forgot Password?';

  @override
  String get onboardingTitle => 'Vehicle Damage & Telemetry AI';

  @override
  String get onboardingDesc =>
      'Capture vehicle photos and OBD-II telemetry for AI-assisted damage detection and roadworthiness assessment.';

  @override
  String get getStarted => 'Get Started';

  @override
  String get skip => 'Skip';

  @override
  String get permissionsInstruction =>
      'Camera and storage permissions are required to capture vehicle photos and upload telemetry logs.';

  @override
  String get home => 'ہوم';

  @override
  String get dashboard => 'Dashboard';

  @override
  String get startInspection => 'Start Inspection';

  @override
  String get inspectionHistory => 'Inspection History';

  @override
  String get profile => 'Profile';

  @override
  String get settings => 'ترتیبات';

  @override
  String get save => 'محفوظ کریں';

  @override
  String get cancel => 'منسوخ کریں';

  @override
  String get back => 'Back';

  @override
  String get next => 'Next';

  @override
  String get retry => 'Retry';

  @override
  String get search => 'تلاش کریں';

  @override
  String get searchHint => 'Search by make, model, VIN...';

  @override
  String get loading => 'Loading...';

  @override
  String get emptyInspections => 'No inspections found.';

  @override
  String get success => 'Success';

  @override
  String get error => 'Error';

  @override
  String get confirm => 'Confirm';

  @override
  String get close => 'Close';

  @override
  String get selectLanguage => 'Language / اردو';

  @override
  String get serverSettings => 'Server Settings';

  @override
  String get backendUrl => 'Backend API Base URL';

  @override
  String get updateUrl => 'Update URL';

  @override
  String get urlUpdated => 'Backend URL updated successfully';

  @override
  String get logOut => 'لاگ آؤٹ';

  @override
  String get logOutConfirmTitle => 'Log Out';

  @override
  String get logOutConfirmMessage =>
      'Are you sure you want to log out of this device? Local authentication tokens will be removed.';

  @override
  String get delete => 'Delete';

  @override
  String get newInspectionTitle => 'New Inspection';

  @override
  String get vehicleDetails => 'Vehicle Details';

  @override
  String get vehicleMake => 'Make';

  @override
  String get vehicleModel => 'Model';

  @override
  String get vehicleYear => 'Year';

  @override
  String get vehicleMileage => 'Mileage (km / mi)';

  @override
  String get vehicleVin => 'VIN';

  @override
  String get step1Details => '1. Details';

  @override
  String get step2Photos => '2. Photos';

  @override
  String get step3Telemetry => '3. Telemetry';

  @override
  String get capturePhotos => 'Vehicle Photos';

  @override
  String get takePhoto => 'Take Photo';

  @override
  String get chooseGallery => 'Choose from Gallery';

  @override
  String get noPhotosSelected => 'No vehicle photos selected yet.';

  @override
  String get uploadTelemetry => 'OBD-II Telemetry Log';

  @override
  String get chooseCsv => 'Select CSV File';

  @override
  String get telemetryOptionalNote =>
      'Attach OBD-II telemetry CSV for powertrain and sensor diagnostics.';

  @override
  String get submitInspection => 'Start AI Assessment';

  @override
  String get submittingInspection => 'Submitting inspection...';

  @override
  String get analysisProgressTitle => 'Analysis in Progress';

  @override
  String get processingStageVision =>
      'Detecting exterior vehicle damage with Mask R-CNN...';

  @override
  String get processingStageObd =>
      'Analyzing telemetry PIDs with Isolation Forest...';

  @override
  String get processingStageRag =>
      'Retrieving grounded repair & safety standards...';

  @override
  String get processingStageRules =>
      'Evaluating deterministic roadworthiness rules...';

  @override
  String get analysisCompleted => 'Analysis Complete!';

  @override
  String get viewReport => 'View Inspection Report';

  @override
  String get obdTelemetryTitle => 'OBD-II Telemetry & Diagnostic Codes';

  @override
  String get telemetryAnalyzed => 'Telemetry Analyzed (Isolation Forest)';

  @override
  String get noTelemetryProvided =>
      'No OBD-II telemetry log provided with this inspection.';

  @override
  String get anomalyDetected => 'Anomaly Flagged';

  @override
  String get flaggedSensors => 'Flagged Telemetry Sensors';

  @override
  String get activeDtcs => 'Active DTC Codes';

  @override
  String get yes => 'YES';

  @override
  String get no => 'NO';

  @override
  String get diagnosticTroubleCodes => 'Diagnostic Trouble Code Explanations';

  @override
  String get urgency => 'Urgency';

  @override
  String get whatItMeans => 'What it means';

  @override
  String get whatWeFound => 'What we found';

  @override
  String get whatDoesThisMean => 'What does this number mean?';

  @override
  String get howOften => 'How often did this happen?';

  @override
  String get whatShouldYouDo => 'What should you do?';

  @override
  String get symptomsAndCauses => 'Symptoms, Causes & Technical Details';

  @override
  String get possibleCauses => 'Possible Causes';

  @override
  String get possibleSymptoms => 'Possible Symptoms';

  @override
  String get technicalDetails => 'Technical Details';

  @override
  String get limitations => 'Important Limitations';

  @override
  String get sourceReference => 'Source Reference';

  @override
  String get diagnosticNotice => 'Diagnostic Notice';

  @override
  String get outsideMonitoringRange => 'Outside Monitoring Range';

  @override
  String get reading => 'Reading';

  @override
  String get verifiedGuidance => 'Verified Repair & Safety Guidance';

  @override
  String get canIKeepDriving => 'Can I keep driving?';

  @override
  String get mechanicCheck => 'What a mechanic should check';

  @override
  String get whyThisMatters => 'Why this matters';

  @override
  String get roadworthinessStatus => 'Roadworthiness Assessment';

  @override
  String get safeStatus => 'محفوظ (SAFE)';

  @override
  String get cautionStatus => 'احتیاط (CAUTION)';

  @override
  String get unsafeStatus => 'غیر محفوظ (UNSAFE)';

  @override
  String get unavailableStatus => 'UNAVAILABLE';

  @override
  String get safeDescription =>
      'No critical safety defects detected. Vehicle appears safe for normal operation.';

  @override
  String get cautionDescription =>
      'Advisory items or non-critical anomalies detected. Professional inspection advised.';

  @override
  String get unsafeDescription =>
      'Critical hazards detected. Driving not recommended until professionally repaired.';

  @override
  String get downloadPdf => 'پی ڈی ایف رپورٹ ڈاؤن لوڈ کریں';

  @override
  String get downloadingPdf => 'Downloading PDF report...';

  @override
  String get pdfSaved => 'PDF Report saved successfully';

  @override
  String get failedDownloadPdf => 'Failed to download PDF report';

  @override
  String get shareReport => 'Share Report';

  @override
  String get damageClassScratch => 'Scratch';

  @override
  String get damageClassDent => 'Dent';

  @override
  String get damageClassBumperSmash => 'Bumper Damage';

  @override
  String get damageClassGlassCrack => 'Glass / Windshield Crack';

  @override
  String get damageClassBrokenLight => 'Broken Light';

  @override
  String get damageClassFlatTire => 'Flat / Deflated Tire';

  @override
  String get damageClassPanelCrush => 'Crushed Panel / Structural Damage';

  @override
  String get damageSeverityLow => 'Low Severity';

  @override
  String get damageSeverityMedium => 'Medium Severity';

  @override
  String get damageSeverityHigh => 'High Severity';

  @override
  String get pleaseEnterEmailAndPassword =>
      'Please enter both email and password.';

  @override
  String get errorOccurred => 'An error occurred. Please try again.';

  @override
  String get recentInspections => 'Recent Inspections';

  @override
  String get allInspections => 'All Inspections';

  @override
  String get historyTitle => 'Inspection History';

  @override
  String get settingsTitle => 'Settings & Compliance';

  @override
  String get reportTitle => 'Inspection Report';

  @override
  String get vehicleOdometer => 'Odometer';

  @override
  String get emailRequired => 'Please enter both email and password.';

  @override
  String get signOut => 'Sign Out';

  @override
  String get signOutSubtitle =>
      'End current session and clear local security tokens';

  @override
  String get logoutConfirmation =>
      'Are you sure you want to log out of this device? Local authentication tokens will be removed.';

  @override
  String get settingsAndCompliance => 'Settings & Compliance';

  @override
  String get languageSectionHeader => 'APPLICATION LANGUAGE / भाषा';

  @override
  String get languageSettingSubtitle =>
      'Select from English or any of the 22 Scheduled Languages of India. Updates the entire application immediately.';

  @override
  String get backendConnection => 'BACKEND CONNECTION';

  @override
  String get apiServerUrl => 'API Server Base URL';

  @override
  String get apiServerUrlSubtitle =>
      'Configure host for local development (e.g., http://localhost:8000 or your LAN IP)';

  @override
  String get saveEndpoint => 'Save Endpoint';

  @override
  String get backendUrlUpdated => 'Backend URL updated successfully';

  @override
  String get sessionManagement => 'SESSION MANAGEMENT';

  @override
  String get stepVehicle => 'Vehicle';

  @override
  String get stepPhotos => 'Photos';

  @override
  String get stepObd => 'OBD-II';

  @override
  String get stepReview => 'Review';

  @override
  String get submitAndAnalyze => 'Submit for Analysis';

  @override
  String get newInspection => 'New Vehicle Inspection';

  @override
  String get startNewInspection => 'Start New Inspection';

  @override
  String get aiInspectionCapabilities => 'AI Inspection Capabilities';

  @override
  String get stage1Filter => 'Stage 1 Filter';

  @override
  String get objectDetection => 'Object Detection';

  @override
  String get obdAnomaly => 'OBD Anomaly';

  @override
  String get ragStandards => 'RAG Standards';

  @override
  String get viewAll => 'View All';

  @override
  String get noInspectionsYet => 'No inspections yet';

  @override
  String get noInspectionsSubtitle =>
      'Tap \"Start New Inspection\" above to photograph a vehicle and run the AI assessment.';

  @override
  String get statusSafe => 'SAFE';

  @override
  String get statusCaution => 'CAUTION';

  @override
  String get statusUnsafe => 'UNSAFE';

  @override
  String get statusReviewNeeded => 'REVIEW NEEDED';

  @override
  String get statusProcessing => 'PROCESSING';

  @override
  String get allInspectionsFilter => 'All Inspections';

  @override
  String get noMatchingInspections => 'No matching inspections found';

  @override
  String get processingInspection => 'Processing Inspection';

  @override
  String get pipelineRunning => 'AI Multi-Agent Pipeline Running';

  @override
  String get pipelineSubtitle =>
      'Our LangGraph supervisor is coordinating specialist agents across vision, telemetry, and safety standards.';

  @override
  String get pipelineFailed =>
      'Analysis pipeline failed on server. Please check inputs and retry.';

  @override
  String get backToHome => 'Back to Home';

  @override
  String get stageValidation => 'Input Validation & Preprocessing';

  @override
  String get stageVision => '4-Stage Vision Cascade (Filter, Detect, Segment)';

  @override
  String get stageObd => 'OBD-II Telemetry & DTC Anomaly Detection';

  @override
  String get stageRAG => 'RAG Knowledge Standards Retrieval';

  @override
  String get stageReport => 'Risk Engine & Report Generation';

  @override
  String get inspectionFindingsReport => 'Inspection Findings & Report';

  @override
  String get exportInspectionReport => 'Export Inspection Report';

  @override
  String get downloadPdfReport => 'Download & Share PDF Report';

  @override
  String get downloadPdfSubtitle =>
      'Printable document with findings, charts, and citations';

  @override
  String get exportJsonData => 'Export JSON Data Payload';

  @override
  String get exportJsonSubtitle =>
      'Machine-readable telemetry & computer vision coordinates';

  @override
  String get retryLoadingReport => 'Retry Loading Report';

  @override
  String get exteriorVisualFindings => 'Exterior Visual Findings';

  @override
  String get noImagesProcessed => 'No images were processed.';

  @override
  String get obdTelemetryFindings => 'OBD-II Telemetry & DTC Findings';

  @override
  String get groundedSafetyGuidance => 'Grounded Safety & Repair Guidance';
}
