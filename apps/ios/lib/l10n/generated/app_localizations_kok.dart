// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Konkani (`kok`).
class AppLocalizationsKok extends AppLocalizations {
  AppLocalizationsKok([String locale = 'kok']) : super(locale);

  @override
  String get appTitle => 'Vehicle Damage AI (कोंकणी)';

  @override
  String get signIn => 'साइन इन करें';

  @override
  String get createAccount => 'खाता बनाएं';

  @override
  String get welcomeBack => 'वापसी पर स्वागत है';

  @override
  String get loginSubtitle =>
      'निरीक्षण रिकॉर्ड करने, टेलीमेट्री अपलोड करने और सुरक्षा रिपोर्ट तैयार करने के लिए साइन इन करें।';

  @override
  String get registerSubtitle =>
      'वाहन सड़क-योग्यता मूल्यांकन शुरू करने के लिए निरीक्षक खाता पंजीकृत करें।';

  @override
  String get emailLabel => 'ईमेल पता';

  @override
  String get emailHint => 'inspector@example.com';

  @override
  String get passwordLabel => 'पासवर्ड';

  @override
  String get passwordHint => '••••••••••••';

  @override
  String get confirmPasswordLabel => 'पासवर्ड की पुष्टि करें';

  @override
  String get confirmPasswordHint => '••••••••••••';

  @override
  String get signInButton => 'साइन इन करें';

  @override
  String get registerButton => 'निरीक्षक खाता बनाएं';

  @override
  String get needAccount => 'खाता नहीं है? यहाँ रजिस्टर करें';

  @override
  String get alreadyHaveAccount => 'पहले से खाता है? साइन इन करें';

  @override
  String get forgotPassword => 'पासवर्ड भूल गए?';

  @override
  String get onboardingTitle => 'वाहन क्षति एवं टेलीमेट्री एआई';

  @override
  String get onboardingDesc =>
      'क्षति का पता लगाने और सड़क-योग्यता मूल्यांकन के लिए वाहन की तस्वीरें और ओबीडी-II टेलीमेट्री दर्ज करें।';

  @override
  String get getStarted => 'शुरू करें';

  @override
  String get skip => 'छोड़ें';

  @override
  String get permissionsInstruction =>
      'वाहन की तस्वीरें लेने और टेलीमेट्री लॉग अपलोड करने के लिए कैमरा और स्टोरेज अनुमति आवश्यक है।';

  @override
  String get home => 'होम';

  @override
  String get dashboard => 'डैशबोर्ड';

  @override
  String get startInspection => 'निरीक्षण शुरू करें';

  @override
  String get inspectionHistory => 'निरीक्षण इतिहास';

  @override
  String get profile => 'प्रोफ़ाइल';

  @override
  String get settings => 'सेटिंग्स';

  @override
  String get save => 'सहेजें';

  @override
  String get cancel => 'रद्द करें';

  @override
  String get back => 'पीछे';

  @override
  String get next => 'आगे';

  @override
  String get retry => 'पुनः प्रयास करें';

  @override
  String get search => 'खोजें';

  @override
  String get searchHint => 'कंपनी, मॉडल या वीआईएन से खोजें...';

  @override
  String get loading => 'लोड हो रहा है...';

  @override
  String get emptyInspections => 'कोई निरीक्षण नहीं मिला।';

  @override
  String get success => 'सफल';

  @override
  String get error => 'त्रुटि';

  @override
  String get confirm => 'पुष्टि करें';

  @override
  String get close => 'बंद करें';

  @override
  String get selectLanguage => 'Language / कोंकणी';

  @override
  String get serverSettings => 'सर्वर सेटिंग्स';

  @override
  String get backendUrl => 'बैकएंड एपीआई यूआरएल';

  @override
  String get updateUrl => 'यूआरएल अपडेट करें';

  @override
  String get urlUpdated => 'बैकएंड यूआरएल सफलतापूर्वक अपडेट किया गया';

  @override
  String get logOut => 'लॉग आउट';

  @override
  String get logOutConfirmTitle => 'लॉग आउट';

  @override
  String get logOutConfirmMessage =>
      'क्या आप इस डिवाइस से लॉग आउट करना चाहते हैं? स्थानीय प्रमाणीकरण टोकन हटा दिए जाएंगे।';

  @override
  String get delete => 'हटाएं';

  @override
  String get newInspectionTitle => 'नया निरीक्षण';

  @override
  String get vehicleDetails => 'वाहन विवरण';

  @override
  String get vehicleMake => 'कंपनी (Make)';

  @override
  String get vehicleModel => 'मॉडल';

  @override
  String get vehicleYear => 'वर्ष';

  @override
  String get vehicleMileage => 'माइलेज (किमी / मील)';

  @override
  String get vehicleVin => 'वीआईएन (वैकल्पिक)';

  @override
  String get step1Details => '1. विवरण';

  @override
  String get step2Photos => '2. तस्वीरें';

  @override
  String get step3Telemetry => '3. टेलीमेट्री';

  @override
  String get capturePhotos => 'वाहन की तस्वीरें';

  @override
  String get takePhoto => 'फोटो खींचें';

  @override
  String get chooseGallery => 'गैलरी से चुनें';

  @override
  String get noPhotosSelected => 'अभी तक कोई तस्वीर नहीं चुनी गई।';

  @override
  String get uploadTelemetry => 'ओबीडी-II टेलीमेट्री लॉग';

  @override
  String get chooseCsv => 'सीएसवी फ़ाइल चुनें';

  @override
  String get telemetryOptionalNote =>
      'वैकल्पिक: इंजन और सेंसर जांच के लिए ओबीडी-II टेलीमेट्री सीएसवी संलग्न करें।';

  @override
  String get submitInspection => 'एआई मूल्यांकन शुरू करें';

  @override
  String get submittingInspection => 'निरीक्षण जमा किया जा रहा है...';

  @override
  String get analysisProgressTitle => 'विश्लेषण जारी है';

  @override
  String get processingStageVision =>
      'मास्क आर-सीएनएन द्वारा बाहरी क्षति की पहचान की जा रही है...';

  @override
  String get processingStageObd =>
      'आइसोलेशन फॉरेस्ट द्वारा टेलीमेट्री पीआईडी का विश्लेषण...';

  @override
  String get processingStageRag =>
      'सत्यापित मरम्मत और सुरक्षा मानकों की पुनर्प्राप्ति...';

  @override
  String get processingStageRules =>
      'सड़क-योग्यता सुरक्षा नियमों का मूल्यांकन...';

  @override
  String get analysisCompleted => 'विश्लेषण पूरा हुआ!';

  @override
  String get viewReport => 'निरीक्षण रिपोर्ट देखें';

  @override
  String get obdTelemetryTitle => 'ओबीडी-II टेलीमेट्री एवं डायग्नोस्टिक कोड';

  @override
  String get telemetryAnalyzed => 'टेलीमेट्री विश्लेषित (आइसोलेशन फॉरेस्ट)';

  @override
  String get noTelemetryProvided =>
      'इस निरीक्षण के साथ कोई ओबीडी-II टेलीमेट्री लॉग प्रदान नहीं किया गया।';

  @override
  String get anomalyDetected => 'असामान्यता चिह्नित';

  @override
  String get flaggedSensors => 'चिह्नित टेलीमेट्री सेंसर';

  @override
  String get activeDtcs => 'सक्रिय डीटीसी कोड';

  @override
  String get yes => 'हाँ';

  @override
  String get no => 'नहीं';

  @override
  String get diagnosticTroubleCodes => 'डायग्नोस्टिक ट्रबल कोड विवरण';

  @override
  String get urgency => 'आवश्यकता स्तर';

  @override
  String get whatItMeans => 'इसका क्या अर्थ है';

  @override
  String get whatWeFound => 'जांच में क्या मिला';

  @override
  String get whatDoesThisMean => 'इस संख्या का क्या अर्थ है?';

  @override
  String get howOften => 'यह कितनी बार हुआ?';

  @override
  String get whatShouldYouDo => 'आपको क्या करना चाहिए?';

  @override
  String get symptomsAndCauses => 'लक्षण, संभावित कारण एवं तकनीकी विवरण';

  @override
  String get possibleCauses => 'संभावित कारण';

  @override
  String get possibleSymptoms => 'संभावित लक्षण';

  @override
  String get technicalDetails => 'तकनीकी विवरण';

  @override
  String get limitations => 'महत्वपूर्ण सीमाएं एवं अनिश्चितता';

  @override
  String get sourceReference => 'मानक संदर्भ स्रोत';

  @override
  String get diagnosticNotice => 'डायग्नोस्टिक सूचना';

  @override
  String get outsideMonitoringRange => 'निगरानी सीमा से बाहर';

  @override
  String get reading => 'रीडिंग';

  @override
  String get verifiedGuidance => 'सत्यापित मरम्मत एवं सुरक्षा मार्गदर्शन';

  @override
  String get canIKeepDriving => 'क्या मैं गाड़ी चलाना जारी रख सकता हूँ?';

  @override
  String get mechanicCheck => 'मैकेनिक को क्या जांचना चाहिए';

  @override
  String get whyThisMatters => 'यह क्यों महत्वपूर्ण है';

  @override
  String get roadworthinessStatus => 'सड़क-योग्यता स्थिति';

  @override
  String get safeStatus => 'सुरक्षित (SAFE)';

  @override
  String get cautionStatus => 'जतनाय (CAUTION)';

  @override
  String get unsafeStatus => 'असुरक्षित (UNSAFE)';

  @override
  String get unavailableStatus => 'अनुपलब्ध (UNAVAILABLE)';

  @override
  String get safeDescription =>
      'कोई गंभीर सुरक्षा दोष नहीं मिला। सामान्य संचालन के लिए वाहन सुरक्षित प्रतीत होता है।';

  @override
  String get cautionDescription =>
      'सलाहकारी मुद्दे या गैर-महत्वपूर्ण असामान्यताएं पाई गईं। पेशेवर जांच की सलाह दी जाती है।';

  @override
  String get unsafeDescription =>
      'गंभीर खतरे पाए गए। पेशेवर रूप से मरम्मत होने तक वाहन चलाना उचित नहीं है।';

  @override
  String get downloadPdf => 'पीडीएफ रिपोर्ट डाउनलोड करें';

  @override
  String get downloadingPdf => 'पीडीएफ रिपोर्ट डाउनलोड हो रही है...';

  @override
  String get pdfSaved => 'पीडीएफ रिपोर्ट सफलतापूर्वक सहेजी गई';

  @override
  String get failedDownloadPdf => 'पीडीएफ रिपोर्ट डाउनलोड करने में विफल';

  @override
  String get shareReport => 'रिपोर्ट साझा करें';

  @override
  String get damageClassScratch => 'खरोंच (Scratch)';

  @override
  String get damageClassDent => 'डेंट (Dent)';

  @override
  String get damageClassBumperSmash => 'बम्पर क्षति (Bumper Damage)';

  @override
  String get damageClassGlassCrack => 'शीशा / विंडशील्ड दरार';

  @override
  String get damageClassBrokenLight => 'टूटी हुई लाइट';

  @override
  String get damageClassFlatTire => 'पंचर / सपाट टायर';

  @override
  String get damageClassPanelCrush => 'दबा हुआ पैनल / संरचनात्मक क्षति';

  @override
  String get damageSeverityLow => 'कम गंभीरता';

  @override
  String get damageSeverityMedium => 'मध्यम गंभीरता';

  @override
  String get damageSeverityHigh => 'उच्च गंभीरता';

  @override
  String get pleaseEnterEmailAndPassword =>
      'कृपया ईमेल और पासवर्ड दोनों दर्ज करें।';

  @override
  String get errorOccurred => 'एक त्रुटि हुई। कृपया पुनः प्रयास करें।';

  @override
  String get recentInspections => 'हाल के निरीक्षण';

  @override
  String get allInspections => 'सभी निरीक्षण';

  @override
  String get historyTitle => 'निरीक्षण इतिहास';

  @override
  String get settingsTitle => 'सेटिंग्स और अनुपालन';

  @override
  String get reportTitle => 'निरीक्षण रिपोर्ट';

  @override
  String get vehicleOdometer => 'ओडोमीटर';

  @override
  String get emailRequired => 'कृपया ईमेल और पासवर्ड दोनों दर्ज करें।';

  @override
  String get signOut => 'साइन आउट करें';

  @override
  String get signOutSubtitle =>
      'वर्तमान सत्र समाप्त करें और स्थानीय सुरक्षा टोकन हटाएं';

  @override
  String get logoutConfirmation =>
      'क्या आप वाकई इस डिवाइस से लॉग आउट करना चाहते हैं? स्थानीय प्रमाणीकरण टोकन हटा दिए जाएंगे।';

  @override
  String get settingsAndCompliance => 'सेटिंग्स और अनुपालन';

  @override
  String get languageSectionHeader => 'अनुप्रयोग भाषा / APPLICATION LANGUAGE';

  @override
  String get languageSettingSubtitle =>
      'अंग्रेजी या भारत की 22 अनुसूचित भाषाओं में से चुनें। पूरा एप्लिकेशन तुरंत अपडेट हो जाता है।';

  @override
  String get backendConnection => 'बैकएंड कनेक्शन';

  @override
  String get apiServerUrl => 'एपीआई सर्वर बेस यूआरएल';

  @override
  String get apiServerUrlSubtitle =>
      'स्थानीय विकास के लिए होस्ट कॉन्फ़िगर करें (उदा. http://localhost:8000)';

  @override
  String get saveEndpoint => 'एंडपॉइंट सहेजें';

  @override
  String get backendUrlUpdated => 'बैकएंड यूआरएल सफलतापूर्वक अपडेट किया गया';

  @override
  String get sessionManagement => 'सत्र प्रबंधन';

  @override
  String get stepVehicle => 'वाहन विवरण';

  @override
  String get stepPhotos => 'तस्वीरें';

  @override
  String get stepObd => 'ओबीडी-II';

  @override
  String get stepReview => 'समीक्षा';

  @override
  String get submitAndAnalyze => 'एआई विश्लेषण प्रारंभ करें';

  @override
  String get newInspection => 'नया वाहन निरीक्षण';

  @override
  String get startNewInspection => 'नया निरीक्षण शुरू करें';

  @override
  String get aiInspectionCapabilities => 'एआई निरीक्षण क्षमताएं';

  @override
  String get stage1Filter => 'स्टेज 1 फ़िल्टर';

  @override
  String get objectDetection => 'ऑब्जेक्ट डिटेक्शन';

  @override
  String get obdAnomaly => 'ओबीडी असामान्यता';

  @override
  String get ragStandards => 'आरएजी मानक';

  @override
  String get viewAll => 'सभी देखें';

  @override
  String get noInspectionsYet => 'अभी तक कोई निरीक्षण नहीं';

  @override
  String get noInspectionsSubtitle =>
      'वाहन की तस्वीर लेने और एआई मूल्यांकन चलाने के लिए ऊपर नया निरीक्षण शुरू करें पर टैप करें।';

  @override
  String get statusSafe => 'सुरक्षित (SAFE)';

  @override
  String get statusCaution => 'सावधानी (CAUTION)';

  @override
  String get statusUnsafe => 'असुरक्षित (UNSAFE)';

  @override
  String get statusReviewNeeded => 'समीक्षा आवश्यक';

  @override
  String get statusProcessing => 'प्रक्रिया जारी (PROCESSING)';

  @override
  String get allInspectionsFilter => 'सभी निरीक्षण';

  @override
  String get noMatchingInspections => 'कोई मेल खाने वाला निरीक्षण नहीं मिला';

  @override
  String get processingInspection => 'निरीक्षण प्रक्रियाधीन';

  @override
  String get pipelineRunning => 'एआई मल्टी-एजेंट पाइपलाइन चल रही है';

  @override
  String get pipelineSubtitle =>
      'पर्यवेक्षक दृष्टि, टेलीमेट्री और सुरक्षा मानकों के विशेषज्ञ एजेंटों का समन्वय कर रहा है।';

  @override
  String get pipelineFailed =>
      'सर्वर पर विश्लेषण पाइपलाइन विफल रही। कृपया इनपुट की जांच करें और पुनः प्रयास करें।';

  @override
  String get backToHome => 'होम पर वापस जाएं';

  @override
  String get stageValidation => 'इनपुट सत्यापन और प्रीप्रोसेसिंग';

  @override
  String get stageVision =>
      '4-चरणीय विज़न कास्केड (फ़िल्टर, पता लगाना, विभाजन)';

  @override
  String get stageObd =>
      'ओबीडी-II टेलीमेट्री और डीटीसी असामान्यता का पता लगाना';

  @override
  String get stageRAG => 'आरएजी सुरक्षा मानकों की पुनर्प्राप्ति';

  @override
  String get stageReport => 'जोखिम इंजन और रिपोर्ट निर्माण';

  @override
  String get inspectionFindingsReport => 'निरीक्षण निष्कर्ष और रिपोर्ट';

  @override
  String get exportInspectionReport => 'निरीक्षण रिपोर्ट निर्यात करें';

  @override
  String get downloadPdfReport => 'पीडीएफ रिपोर्ट डाउनलोड और साझा करें';

  @override
  String get downloadPdfSubtitle =>
      'निष्कर्ष, चार्ट और संदर्भों के साथ मुद्रण योग्य दस्तावेज़';

  @override
  String get exportJsonData => 'जेसन डेटा निर्यात करें';

  @override
  String get exportJsonSubtitle =>
      'मशीन-पठनीय टेलीमेट्री और कंप्यूटर विज़न निर्देशांक';

  @override
  String get retryLoadingReport => 'रिपोर्ट पुनः लोड करने का प्रयास करें';

  @override
  String get exteriorVisualFindings => 'बाहरी दृश्य निष्कर्ष';

  @override
  String get noImagesProcessed => 'किसी भी छवि पर प्रक्रिया नहीं की गई।';

  @override
  String get obdTelemetryFindings => 'ओबीडी-II टेलीमेट्री और डीटीसी निष्कर्ष';

  @override
  String get groundedSafetyGuidance => 'सत्यापित सुरक्षा और मरम्मत मार्गदर्शन';
}
