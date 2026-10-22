/// Multilingual diagnostic translation helper for OBD-II findings, DTCs,
/// telemetry PIDs, vehicle roadworthiness risk, and RAG repair guidance.
///
/// Ensures dynamic content displayed on the Inspection Report screen updates
/// in the user's selected language (Hindi, Tamil, Telugu, Kannada, Bengali,
/// Gujarati, Marathi, Punjabi, Malayalam, Odia, etc.) while preserving
/// technical code identifiers (P0300, P0128, etc.).
library;

class DiagnosticLocalization {
  DiagnosticLocalization._();

  // ---------------------------------------------------------------------------
  // 1. Language Normalization Helper
  // ---------------------------------------------------------------------------
  static String _norm(String langCode) {
    return langCode.toLowerCase().split('-')[0].split('_')[0];
  }

  // ---------------------------------------------------------------------------
  // 2. Risk Banner & Executive Summary Labels
  // ---------------------------------------------------------------------------
  static String getRiskBannerTitle(String riskClass, bool isInconclusive, String langCode) {
    final lang = _norm(langCode);
    final rc = riskClass.toLowerCase();

    if (rc == 'unsafe') {
      switch (lang) {
        case 'hi': return 'असुरक्षित — गंभीर जोखिमों का पता चला';
        case 'ta': return 'பாதுகாப்பற்றது — முக்கியமான அபாயங்கள் கண்டறியப்பட்டுள்ளன';
        case 'te': return 'అసురక్షితం — తీవ్రమైన ప్రమాదాలు గుర్తించబడ్డాయి';
        case 'kn': return 'ಅಸುರಕ್ಷಿತ — ಗಂಭೀರ ಅಪಾಯಗಳು ಕಂಡುಬಂದಿವೆ';
        case 'bn': return 'অনিরাপদ — গুরুতর ঝুঁকি সনাক্ত করা হয়েছে';
        case 'gu': return 'અસુરક્ષિત — ગંભીર જોખમો જણાયા';
        case 'mr': return 'असुरक्षित — गंभीर धोके आढळले';
        case 'pa': return 'ਅਸੁਰੱਖਿਅਤ — ਗੰਭੀਰ ਖਤਰੇ ਪਾਏ ਗਏ';
        case 'ml': return 'അസുരക്ഷിതം — ഗുരുതരമായ അപകടസാധ്യതകൾ കണ്ടെത്തി';
        case 'or': return 'ଅସୁରକ୍ଷିତ — ଗୁରୁତର ବିପଦ ଚିହ୍ନଟ ହୋଇଛି';
        default: return 'UNSAFE — CRITICAL RISKS DETECTED';
      }
    } else if (rc == 'caution') {
      switch (lang) {
        case 'hi': return 'सावधानी — सलाहकारी समस्याएं देखी गईं';
        case 'ta': return 'எச்சரிக்கை — ஆலோசனைக் குறைபாடுகள் காணப்படுகின்றன';
        case 'te': return 'హెచ్చరిక — సలహా సమస్యలు గమనించబడ్డాయి';
        case 'kn': return 'ಎಚ್ಚರಿಕೆ — ಸಲಹಾ ಸಮಸ್ಯೆಗಳು ಕಂಡುಬಂದಿವೆ';
        case 'bn': return 'সতর্কতা — পরামর্শমূলক সমস্যা দেখা গেছে';
        case 'gu': return 'સાવધાની — સલાહકાર સમસ્યાઓ જોવા મળી';
        case 'mr': return 'सावधान — सल्लागार समस्या आढळल्या';
        case 'pa': return 'ਸਾਵਧਾਨੀ — ਸਲਾਹਕਾਰ ਮੁੱਦੇ ਦੇਖੇ ਗਏ';
        case 'ml': return 'ജാഗ്രത — ഉപദേശപരമായ പ്രശ്നങ്ങൾ നിരീക്ഷിച്ചു';
        case 'or': return 'ସତର୍କତା — ପରାମର୍ଶଦାତା ସମସ୍ୟା ଦେଖାଯାଇଛି';
        default: return 'CAUTION — ADVISORY ISSUES OBSERVED';
      }
    } else if (rc == 'unavailable' || isInconclusive) {
      switch (lang) {
        case 'hi': return 'निर्धारित करने में असमर्थ — मैन्युअल समीक्षा आवश्यक';
        case 'ta': return 'தீர்மானிக்க முடியவில்லை — நேரடி ஆய்வு தேவை';
        case 'te': return 'నిర్ణయించలేకపోయాము — మాన్యువల్ సమీక్ష అవసరం';
        case 'kn': return 'ನಿರ್ಧರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ — ಹಸ್ತಚಾಲಿತ ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ';
        case 'bn': return 'নির্ধারণ করতে অক্ষম — ম্যানুয়াল পর্যালোচনা প্রয়োজন';
        case 'gu': return 'નક્કી કરવામાં અસમર્થ — મેન્યુઅલ સમીક્ષા જરૂરી';
        case 'mr': return 'निश्चित करण्यात अक्षम — मॅन्युअल पुनरावलोकन आवश्यक';
        case 'pa': return 'ਨਿਰਧਾਰਤ ਕਰਨ ਵਿੱਚ ਅਸਮਰੱਥ — ਮੈਨੂਅਲ ਸਮੀਖਿਆ ਲੋੜੀਂਦੀ ਹੈ';
        case 'ml': return 'തീരുമാനിക്കാൻ കഴിഞ്ഞില്ല — പരിശോധന ആവശ്യമാണ്';
        case 'or': return 'ନିର୍ଣ୍ଣୟ କରିବାକୁ ଅସମର୍ଥ — ମାନୁଆଲ୍ ସମୀକ୍ଷା ଆବଶ୍ୟକ';
        default: return 'UNABLE TO DETERMINE — MANUAL REVIEW REQUIRED';
      }
    } else {
      switch (lang) {
        case 'hi': return 'सामान्य परिस्थितियों के लिए सुरक्षित';
        case 'ta': return 'வழக்கமான பயன்பாட்டிற்கு பாதுகாப்பானது';
        case 'te': return 'సాధారణ పరిస్థితులకు సురక్షితం';
        case 'kn': return 'ಸಾಮಾನ್ಯ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ಸುರಕ್ಷಿತ';
        case 'bn': return 'স্বাভাবিক পরিস্থিতির জন্য নিরাপদ';
        case 'gu': return 'સામાન્ય પરિસ્થિતિઓ માટે સુરક્ષિત';
        case 'mr': return 'सामान्य परिस्थितीसाठी सुरक्षित';
        case 'pa': return 'ਆਮ ਸਥਿਤੀਆਂ ਲਈ ਸੁਰੱਖਿਅਤ';
        case 'ml': return 'സാധാരണ അവസ്ഥകൾക്ക് സുരക്ഷിതം';
        case 'or': return 'ସାଧାରଣ ପରିସ୍ଥିତି ପାଇଁ ସୁରକ୍ଷିତ';
        default: return 'SAFE FOR TYPICAL CONDITIONS';
      }
    }
  }

  static String getProfessionalInspectionBadge(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'पेशेवर योग्य निरीक्षण की सिफारिश की जाती है';
      case 'ta': return 'தகுதிவாய்ந்த நிபுணர் ஆய்வு பரிந்துரைக்கப்படுகிறது';
      case 'te': return 'వృత్తిపరమైన అర్హత గల తనిఖీ సిఫార్సు చేయబడింది';
      case 'kn': return 'ವೃತ್ತಿಪರ ಅರ್ಹ ತಪಾಸಣೆ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ';
      case 'bn': return 'পেশাদার যোগ্য পরিদর্শনের পরামর্শ দেওয়া হচ্ছে';
      case 'gu': return 'વ્યવસાયિક લાયકાત ધરાવતી તપાસની ભલામણ કરવામાં આવે છે';
      case 'mr': return 'व्यावसायिक पात्र तपासणीची शिफारस केली आहे';
      case 'pa': return 'ਪੇਸ਼ੇਵਰ ਯੋਗਤਾ ਪ੍ਰਾਪਤ ਨਿਰੀਖਣ ਦੀ ਸਿਫਾਰਸ਼ ਕੀਤੀ ਜਾਂਦੀ ਹੈ';
      case 'ml': return 'പ്രൊഫഷണൽ യോഗ്യതയുള്ള പരിശോധന ശുപാർശ ചെയ്യുന്നു';
      case 'or': return 'ବୃତ୍ତିଗତ ଯୋଗ୍ୟ ଯାଞ୍ଚ ପାଇଁ ପରାମର୍ଶ ଦିଆଯାଇଛି';
      default: return 'Professional qualified inspection recommended';
    }
  }

  static String getRiskSummary(String riskClass, String originalSummary, String langCode) {
    final lang = _norm(langCode);
    final rc = riskClass.toLowerCase();

    if (lang == 'en') return originalSummary;

    // Check for high-level risk patterns from rules engine
    if (rc == 'unsafe') {
      switch (lang) {
        case 'hi':
          return 'वाहन असुरक्षित श्रेणी में वर्गीकृत। महत्वपूर्ण ड्राइविंग या यांत्रिक खतरे पाए गए। गंभीर बाहरी क्षति या डीटीसी कोड (जैसे P0300 मिसफायर) की तत्काल पेशेवर मरम्मत आवश्यक है।';
        case 'ta':
          return 'வாகனம் பாதுகாப்பற்றதாக வகைப்படுத்தப்பட்டுள்ளது. குறிப்பிடத்தக்க ஓட்டுநர் அல்லது இயந்திர அபாயங்கள் கண்டறியப்பட்டுள்ளன. தீவிர சேதங்கள் அல்லது DTC குறியீடுகளுக்கு உடனடி பழுதுபார்ப்பு தேவை.';
        case 'te':
          return 'వాహనం అసురక్షితంగా వర్గీకరించబడింది. తీవ్రమైన డ్రైవింగ్ లేదా మెకానికల్ ప్రమాదాలు గుర్తించబడ్డాయి. తీవ్రమైన నష్టం లేదా DTC కోడ్‌లకు తక్షణ మరమ్మతు అవసరం.';
        case 'kn':
          return 'ವಾಹನ ಅಸುರಕ್ಷಿತ ಎಂದು ವರ್ಗೀಕರಿಸಲಾಗಿದೆ. ಗಂಭೀರ ಚಾಲನೆ ಅಥವಾ ಯಾಂತ್ರಿಕ ಅಪಾಯಗಳು ಕಂಡುಬಂದಿವೆ. ತಕ್ಷಣದ ದುರಸ್ತಿ ಅಗತ್ಯವಿದೆ.';
        case 'bn':
          return 'যানবাহন অনিরাপদ হিসেবে শ্রেণীবদ্ধ। উল্লেখযোগ্য ড্রাইভিং বা যান্ত্রিক ঝুঁকি সনাক্ত হয়েছে। অবিলম্বে মেরামত প্রয়োজন।';
        case 'gu':
          return 'વાહન અસુરક્ષિત તરીકે વર્ગીકૃત. નોંધપાત્ર ડ્રાઇવિંગ અથવા યાંત્રિક જોખમો જણાયા. તાત્કાલિક સમારકામ જરૂરી છે.';
        case 'mr':
          return 'वाहन असुरक्षित म्हणून वर्गीकृत. लक्षणीय ड्रायव्हिंग किंवा यांत्रिक धोके आढळले. त्वरित दुरुस्ती आवश्यक आहे.';
        case 'pa':
          return 'ਵਾਹਨ ਨੂੰ ਅਸੁਰੱਖਿਅਤ ਵਜੋਂ ਸ਼੍ਰੇਣੀਬੱਧ ਕੀਤਾ ਗਿਆ। ਮਹੱਤਵਪੂਰਨ ਡਰਾਈਵਿੰਗ ਜਾਂ ਮਕੈਨੀਕਲ ਖਤਰੇ ਪਾਏ ਗਏ। ਤੁਰੰਤ ਮੁਰੰਮਤ ਲੋੜੀਂਦੀ ਹੈ।';
        case 'ml':
          return 'വാഹനം അസുരക്ഷിതമായി തരംതിരിച്ചിരിക്കുന്നു. കാര്യമായ ഡ്രൈവിംഗ് അല്ലെങ്കിൽ മെക്കാനിക്കൽ അപകടങ്ങൾ കണ്ടെത്തി. അടിയന്തിര അറ്റകുറ്റപ്പണി ആവശ്യമാണ്.';
        case 'or':
          return 'ଯାନଟି ଅସୁରକ୍ଷିତ ଭାବେ ବର୍ଗୀକୃତ। ଉଲ୍ଲେଖନୀୟ ଡ୍ରାଇଭିଂ କିମ୍ବା ଯାନ୍ତ୍ରିକ ବିପଦ ଚିହ୍ନଟ ହୋଇଛି। ତୁରନ୍ତ ମରାମତି ଆବଶ୍ୟକ।';
        default:
          return originalSummary;
      }
    } else if (rc == 'caution') {
      switch (lang) {
        case 'hi':
          return 'वाहन सावधानी श्रेणी में वर्गीकृत। मध्यम क्षति या टेलीमेट्री असामान्यताएं देखी गईं। आगे नुकसान से बचने के लिए पेशेवर निरीक्षण कराएं।';
        case 'ta':
          return 'வாகனம் எச்சரிக்கை பிரிவில் வைக்கப்பட்டுள்ளது. மிதமான சேதம் அல்லது சென்சார் முரண்பாடுகள் காணப்படுகின்றன. நிபுணர் ஆய்வு பரிந்துரைக்கப்படுகிறது.';
        case 'te':
          return 'వాహనం హెచ్చరిక విభాగంలో ఉంది. మోస్తరు నష్టం లేదా సెన్సార్ సమస్యలు గమనించబడ్డాయి. నిపుణుల తనిఖీ సిఫార్సు చేయబడింది.';
        default:
          return originalSummary;
      }
    } else if (rc == 'safe') {
      switch (lang) {
        case 'hi':
          return 'वाहन सामान्य परिस्थितियों के लिए सुरक्षित है। कोई उच्च जोखिम वाला संरचनात्मक दोष या गंभीर इंजन खराबी नहीं मिली।';
        case 'ta':
          return 'வாகனம் சாதாரண பயன்பாட்டிற்கு பாதுகாப்பானது. கடுமையான சேதங்கள் எதுவும் இல்லை.';
        case 'te':
          return 'వాహనం సాధారణ పరిస్థితులలో సురక్షితం. ఎటువంటి ప్రమాదకర లోపాలు లేవు.';
        default:
          return originalSummary;
      }
    }
    return originalSummary;
  }

  static String getDamageDetectedLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'क्षति का पता चला';
      case 'ta': return 'சேதம் கண்டறியப்பட்டது';
      case 'te': return 'నష్టం గుర్తించబడింది';
      case 'kn': return 'ಹಾನಿ ಪತ್ತೆಯಾಗಿದೆ';
      case 'bn': return 'ক্ষতি সনাক্ত হয়েছে';
      case 'gu': return 'નુકસાન જણાયું';
      case 'mr': return 'नुकसान आढळले';
      case 'pa': return 'ਨੁਕਸਾਨ ਪਾਇਆ ਗਿਆ';
      case 'ml': return 'കേടുപാടുകൾ കണ്ടെത്തി';
      case 'or': return 'କ୍ଷତି ଚିହ୍ନଟ ହୋଇଛି';
      default: return 'Damage Detected';
    }
  }

  static String getSeverityLevelLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'गंभीरता का स्तर';
      case 'ta': return 'தீவிரத்தன்மை நிலை';
      case 'te': return 'తీవ్రత స్థాయి';
      case 'kn': return 'ತೀವ್ರತೆಯ ಮಟ್ಟ';
      case 'bn': return 'তীব্রতার মাত্রা';
      case 'gu': return 'તીવ્રતા સ્તર';
      case 'mr': return 'तीव्रता पातळी';
      case 'pa': return 'ਗੰਭੀਰਤਾ ਪੱਧਰ';
      case 'ml': return 'തീവ്രത നില';
      case 'or': return 'ଗୁରୁତର ସ୍ତର';
      default: return 'Severity Level';
    }
  }

  static String getSeverityScoreLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'गंभीरता स्कोर';
      case 'ta': return 'தீவிரத்தன்மை மதிப்பெண்';
      case 'te': return 'తీవ్రత స్కోరు';
      case 'kn': return 'ತೀವ್ರತೆ ಸ್ಕೋರ್';
      case 'bn': return 'তীব্রতা স্কোর';
      case 'gu': return 'તીવ્રતા સ્કોર';
      case 'mr': return 'तीव्रता गुण';
      case 'pa': return 'ਗੰਭੀਰਤਾ ਸਕੋਰ';
      case 'ml': return 'തീവ്രത സ്കോർ';
      case 'or': return 'ଗୁରୁତର ସ୍କୋର';
      default: return 'Severity Score';
    }
  }

  static String getBooleanLabel(String raw, String langCode) {
    final lang = _norm(langCode);
    final upper = raw.toUpperCase().trim();
    if (upper == 'YES') {
      switch (lang) {
        case 'hi': return 'हाँ';
        case 'ta': return 'ஆம்';
        case 'te': return 'అవును';
        case 'kn': return 'ಹೌದು';
        case 'bn': return 'হ্যাঁ';
        case 'gu': return 'હા';
        case 'mr': return 'होय';
        case 'pa': return 'ਹਾਂ';
        case 'ml': return 'അതെ';
        case 'or': return 'ହଁ';
        default: return 'YES';
      }
    } else if (upper == 'NO') {
      switch (lang) {
        case 'hi': return 'नहीं';
        case 'ta': return 'இல்லை';
        case 'te': return 'కాదు';
        case 'kn': return 'ಇಲ್ಲ';
        case 'bn': return 'না';
        case 'gu': return 'ના';
        case 'mr': return 'नाही';
        case 'pa': return 'ਨਹੀਂ';
        case 'ml': return 'ഇല്ല';
        case 'or': return 'ନା';
        default: return 'NO';
      }
    } else if (upper == 'UNKNOWN') {
      switch (lang) {
        case 'hi': return 'अज्ञात';
        case 'ta': return 'தெரியவில்லை';
        case 'te': return 'తెలియదు';
        case 'kn': return 'ತಿಳಿದಿಲ್ಲ';
        case 'bn': return 'অজানা';
        case 'gu': return 'અજ્ઞાત';
        case 'mr': return 'अज्ञात';
        case 'pa': return 'ਅਣਜਾਣ';
        case 'ml': return 'അജ്ഞാതം';
        case 'or': return 'ଅଜ୍ଞାତ';
        default: return 'UNKNOWN';
      }
    }
    return raw;
  }

  static String getSeverityValue(String level, String langCode) {
    final lang = _norm(langCode);
    final upper = level.toUpperCase().trim();
    if (upper == 'LOW') {
      switch (lang) {
        case 'hi': return 'कम (LOW)';
        case 'ta': return 'குறைவு (LOW)';
        case 'te': return 'తక్కువ (LOW)';
        case 'kn': return 'ಕಡಿಮೆ (LOW)';
        case 'bn': return 'কম (LOW)';
        case 'gu': return 'ઓછું (LOW)';
        case 'mr': return 'कमी (LOW)';
        case 'pa': return 'ਘੱਟ (LOW)';
        case 'ml': return 'കുറഞ്ഞത് (LOW)';
        case 'or': return 'କମ (LOW)';
        default: return 'LOW';
      }
    } else if (upper == 'MEDIUM') {
      switch (lang) {
        case 'hi': return 'मध्यम (MEDIUM)';
        case 'ta': return 'நடுத்தரம் (MEDIUM)';
        case 'te': return 'మధ్యస్థం (MEDIUM)';
        case 'kn': return 'ಮಧ್ಯಮ (MEDIUM)';
        case 'bn': return 'মাঝারি (MEDIUM)';
        case 'gu': return 'મધ્યમ (MEDIUM)';
        case 'mr': return 'मध्यम (MEDIUM)';
        case 'pa': return 'ਦਰਮਿਆਨਾ (MEDIUM)';
        case 'ml': return 'ഇടത്തരം (MEDIUM)';
        case 'or': return 'ମଧ୍ୟମ (MEDIUM)';
        default: return 'MEDIUM';
      }
    } else if (upper == 'HIGH') {
      switch (lang) {
        case 'hi': return 'उच्च (HIGH)';
        case 'ta': return 'அதிகம் (HIGH)';
        case 'te': return 'ఎక్కువ (HIGH)';
        case 'kn': return 'ಹೆಚ್ಚು (HIGH)';
        case 'bn': return 'উচ্চ (HIGH)';
        case 'gu': return 'વધારે (HIGH)';
        case 'mr': return 'उच्च (HIGH)';
        case 'pa': return 'ਉੱਚ (HIGH)';
        case 'ml': return 'ഉയർന്നത് (HIGH)';
        case 'or': return 'ଉଚ୍ଚ (HIGH)';
        default: return 'HIGH';
      }
    } else if (upper == 'N/A' || upper == 'UNAVAILABLE') {
      return 'N/A';
    }
    return level;
  }

  static String getInconclusiveBannerText(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'निर्धारित करने में असमर्थ — मैन्युअल समीक्षा आवश्यक।';
      case 'ta': return 'தீர்மானிக்க முடியவில்லை — நேரடி ஆய்வு தேவை.';
      case 'te': return 'నిర్ణయించలేకపోయాము — మాన్యువల్ సమీక్ష అవసరం.';
      case 'kn': return 'ನಿರ್ಧರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ — ಹಸ್ತಚಾಲಿತ ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ.';
      case 'bn': return 'নির্ধারণ করতে অক্ষম — ম্যানুয়াল পর্যালোচনা প্রয়োজন।';
      case 'gu': return 'નક્કી કરવામાં અસમર્થ — મેન્યુઅલ સમીક્ષા જરૂરી.';
      case 'mr': return 'निश्चित करण्यात अक्षम — मॅन्युअल पुनरावलोकन आवश्यक.';
      case 'pa': return 'ਨਿਰਧਾਰਤ ਕਰਨ ਵਿੱਚ ਅਸਮਰੱਥ — ਮੈਨੂਅਲ ਸਮੀਖਿਆ ਲੋੜੀਂਦੀ ਹੈ।';
      case 'ml': return 'തീരുമാനിക്കാൻ കഴിഞ്ഞില്ല — പരിശോധന ആവശ്യമാണ്.';
      case 'or': return 'ନିର୍ଣ୍ଣୟ କରିବାକୁ ଅସମର୍ଥ — ମାନୁଆଲ୍ ସମୀକ୍ଷା ଆବଶ୍ୟକ।';
      default: return 'Unable to determine — manual review required.';
    }
  }

  // ---------------------------------------------------------------------------
  // 3. OBD-II Section Labels
  // ---------------------------------------------------------------------------
  static String getTelemetryStatusLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'टेलीमेट्री स्थिति';
      case 'ta': return 'டெலிமெட்ரி நிலை';
      case 'te': return 'టెలిమెట్రీ స్థితి';
      case 'kn': return 'ಟೆಲಿಮೆಟ್ರಿ ಸ್ಥಿತಿ';
      case 'bn': return 'টেলিমেট্রি অবস্থা';
      case 'gu': return 'ટેલિમેટ્રી સ્થિતિ';
      case 'mr': return 'टेलिमेट्री स्थिती';
      case 'pa': return 'ਟੈਲੀਮੈਟਰੀ ਸਥਿਤੀ';
      case 'ml': return 'ടെലിമെട്രി നില';
      case 'or': return 'ଟେଲିମେଟ୍ରି ସ୍ଥିତି';
      default: return 'Telemetry Status';
    }
  }

  static String getTelemetryStatusBadge(bool hasAnomalies, String langCode) {
    final lang = _norm(langCode);
    if (hasAnomalies) {
      switch (lang) {
        case 'hi': return 'असामान्यताओं का पता चला';
        case 'ta': return 'முரண்பாடுகள் கண்டறியப்பட்டன';
        case 'te': return 'సమస్యలు గుర్తించబడ్డాయి';
        case 'kn': return 'ವ್ಯತ್ಯಾಸಗಳು ಕಂಡುಬಂದಿವೆ';
        case 'bn': return 'অসঙ্গতি সনাক্ত করা হয়েছে';
        case 'gu': return 'વિસંગતતાઓ જણાઈ';
        case 'mr': return 'विसंगती आढळल्या';
        case 'pa': return 'ਵਿਸੰਗਤੀਆਂ ਪਾਈਆਂ ਗਈਆਂ';
        case 'ml': return 'അപാകതകൾ കണ്ടെത്തി';
        case 'or': return 'ଅସ୍ୱାଭାବିକତା ଚିହ୍ନଟ ହୋଇଛି';
        default: return 'ANOMALIES DETECTED';
      }
    } else {
      switch (lang) {
        case 'hi': return 'सामान्य रीडिंग';
        case 'ta': return 'வழக்கமான அளவீடுகள்';
        case 'te': return 'సాధారణ రీడింగ్‌లు';
        case 'kn': return 'ಸಾಮಾನ್ಯ ರೀಡಿಂಗ್‌ಗಳು';
        case 'bn': return 'স্বাভাবিক রিডিং';
        case 'gu': return 'સામાન્ય રીડિંગ્સ';
        case 'mr': return 'सामान्य वाचन';
        case 'pa': return 'ਆਮ ਰੀਡਿੰਗਾਂ';
        case 'ml': return 'സാധാരണ റീഡിംഗുകൾ';
        case 'or': return 'ସାଧାରଣ ରିଡିଂ';
        default: return 'NORMAL READINGS';
      }
    }
  }

  static String getActiveDtcsHeader(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सक्रिय डायग्नोस्टिक ट्रबल कोड (DTCs):';
      case 'ta': return 'செயலில் உள்ள பிழைக் குறியீடுகள் (DTCs):';
      case 'te': return 'యాక్టివ్ డయాగ్నస్టిక్ ట్రబుల్ కోడ్‌లు (DTCs):';
      case 'kn': return 'ಸಕ್ರಿಯ ಡಯಾಗ್ನೋಸ್ಟಿಕ್ ಟ್ರಬಲ್ ಕೋಡ್‌ಗಳು (DTCs):';
      case 'bn': return 'সক্রিয় ডায়াগনস্টিক ট্রাবল কোড (DTCs):';
      case 'gu': return 'સક્રિય ડાયગ્નોસ્ટિક ટ્રબલ કોડ્સ (DTCs):';
      case 'mr': return 'सक्रिय डायग्नोस्टिक ट्रबल कोड (DTCs):';
      case 'pa': return 'ਕਿਰਿਆਸ਼ੀਲ ਡਾਇਗਨੌਸਟਿਕ ਟਰਬਲ ਕੋਡ (DTCs):';
      case 'ml': return 'സജീവ ഡയഗ്നോസ്റ്റിക് ട്രബിൾ കോഡുകൾ (DTCs):';
      case 'or': return 'ସକ୍ରିୟ ଡାଇଗ୍ନୋଷ୍ଟିକ୍ ଟ୍ରବଲ୍ କୋଡ୍ (DTCs):';
      default: return 'Active Diagnostic Trouble Codes (DTCs):';
    }
  }

  static String getFlaggedSensorsHeader(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'चिह्नित टेलीमेट्री सेंसर:';
      case 'ta': return 'குறிக்கப்பட்ட டெலிமெட்ரி சென்சார்கள்:';
      case 'te': return 'ఫ్లాగ్ చేయబడిన టెలిమెట్రీ సెన్సార్లు:';
      case 'kn': return 'ಗುರುತಿಸಲಾದ ಟೆಲಿಮೆಟ್ರಿ ಸಂವೇದಕಗಳು:';
      case 'bn': return 'চিহ্নিত টেলিমেট্রি সেন্সর:';
      case 'gu': return 'ચિહ્નિત ટેલિમેટ્રી સેન્સર્સ:';
      case 'mr': return 'चिन्हांकित टेलिमेट्री सेन्सर्स:';
      case 'pa': return 'ਨਿਸ਼ਾਨਬੱਧ ਟੈਲੀਮੈਟਰੀ ਸੈਂਸਰ:';
      case 'ml': return 'ഫ്ലാഗ് ചെയ്ത ടെലിമെട്രി സെൻസറുകൾ:';
      case 'or': return 'ଚିହ୍ନିତ ଟେଲିମେଟ୍ରି ସେନ୍ସର:';
      default: return 'Flagged Telemetry Sensors:';
    }
  }

  static String getUrgencyLabel(String urgencyLabel, String langCode) {
    final lang = _norm(langCode);
    final lower = urgencyLabel.toLowerCase();

    if (lower.contains('stop')) {
      switch (lang) {
        case 'hi': return 'सुरक्षित रूप से रुकें';
        case 'ta': return 'பாதுகாப்பாக நிறுத்துங்கள்';
        case 'te': return 'సురక్షితంగా ఆపండి';
        case 'kn': return 'ಸುರಕ್ಷಿತವಾಗಿ ನಿಲ್ಲಿಸಿ';
        case 'bn': return 'নিরাপদে থামুন';
        case 'gu': return 'સલામત રીતે રોકો';
        case 'mr': return 'सुरक्षितपणे थांबा';
        case 'pa': return 'ਸੁਰੱਖਿਅਤ ਢੰਗ ਨਾਲ ਰੁਕੋ';
        case 'ml': return 'സുരക്ഷിതമായി നിർത്തുക';
        case 'or': return 'ସୁରକ୍ଷିତ ଭାବେ ଅଟକନ୍ତୁ';
        default: return 'Stop Safely';
      }
    } else if (lower.contains('prompt')) {
      switch (lang) {
        case 'hi': return 'शीघ्र ध्यान दें';
        case 'ta': return 'உடனடி கவனம் தேவை';
        case 'te': return 'వెంటనే శ్రద్ధ వహించండి';
        case 'kn': return 'ತ್ವರಿತ ಗಮನ ಅಗತ್ಯ';
        case 'bn': return 'দ্রুত মনোযোগ দিন';
        case 'gu': return 'તાત્કાલિક ધ્યાન આપો';
        case 'mr': return 'त्वरित लक्ष द्या';
        case 'pa': return 'ਤੁਰੰਤ ਧਿਆਨ ਦਿਓ';
        case 'ml': return 'ഉടൻ ശ്രദ്ധിക്കുക';
        case 'or': return 'ତୁରନ୍ତ ଧ୍ୟାନ ଦିଅନ୍ତୁ';
        default: return 'Prompt Attention';
      }
    } else if (lower.contains('schedule') || lower.contains('check')) {
      switch (lang) {
        case 'hi': return 'जांच का समय तय करें';
        case 'ta': return 'பரிசோதனைக்கு திட்டமிடுங்கள்';
        case 'te': return 'తనిఖీని షెడ్యూల్ చేయండి';
        case 'kn': return 'ತಪಾಸಣೆಯನ್ನು ನಿಗದಿಪಡಿಸಿ';
        case 'bn': return 'একটি পরীক্ষা নির্ধারণ করুন';
        case 'gu': return 'તપાસ સુનિશ્ચિત કરો';
        case 'mr': return 'तपासणीचे नियोजन करा';
        case 'pa': return 'ਜਾਂਚ ਨਿਰਧਾਰਤ ਕਰੋ';
        case 'ml': return 'പരിശോധന ഷെഡ്യൂൾ ചെയ്യുക';
        case 'or': return 'ଯାଞ୍ଚ ନିର୍ଦ୍ଧାରଣ କରନ୍ତୁ';
        default: return 'Schedule a Check';
      }
    }
    return urgencyLabel;
  }

  // ---------------------------------------------------------------------------
  // 4. Action & Detail Headers
  // ---------------------------------------------------------------------------
  static String getWhatYouShouldDoLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'आपको क्या करना चाहिए: ';
      case 'ta': return 'நீங்கள் என்ன செய்ய வேண்டும்: ';
      case 'te': return 'మీరు ఏమి చేయాలి: ';
      case 'kn': return 'ನೀವು ಏನು ಮಾಡಬೇಕು: ';
      case 'bn': return 'আপনার কি করা উচিত: ';
      case 'gu': return 'તમારે શું કરવું જોઈએ: ';
      case 'mr': return 'तुम्ही काय करावे: ';
      case 'pa': return 'ਤੁਹਾਨੂੰ ਕੀ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ: ';
      case 'ml': return 'നിങ്ങൾ എന്തുചെയ്യണം: ';
      case 'or': return 'ଆପଣ କ’ଣ କରିବା ଉଚିତ୍: ';
      default: return 'What you should do: ';
    }
  }

  static String getWhatWeFoundLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'हमें क्या मिला: ';
      case 'ta': return 'நாங்கள் கண்டறிந்தது: ';
      case 'te': return 'మేము కనుగొన్నది: ';
      case 'kn': return 'ನಾವು ಕಂಡುಕೊಂಡದ್ದು: ';
      case 'bn': return 'আমরা যা পেয়েছি: ';
      case 'gu': return 'અમને શું મળ્યું: ';
      case 'mr': return 'आम्हाला काय आढळले: ';
      case 'pa': return 'ਸਾਨੂੰ ਕੀ ਮਿਲਿਆ: ';
      case 'ml': return 'ഞങ്ങൾ കണ്ടെത്തിയത്: ';
      case 'or': return 'ଆମେ କ’ଣ ପାଇଲୁ: ';
      default: return 'What we found: ';
    }
  }

  static String getWhyThisMattersLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'यह क्यों महत्वपूर्ण है: ';
      case 'ta': return 'இது ஏன் முக்கியமானது: ';
      case 'te': return 'ఇది ఎందుకు ముఖ్యం: ';
      case 'kn': return 'ಇದು ಏಕೆ ಮುಖ್ಯ: ';
      case 'bn': return 'এটি কেন গুরুত্বপূর্ণ: ';
      case 'gu': return 'આ શા માટે મહત્વપૂર્ણ છે: ';
      case 'mr': return 'हे का महत्त्वाचे आहे: ';
      case 'pa': return 'ਇਹ ਕਿਉਂ ਮਹੱਤਵਪੂਰਨ ਹੈ: ';
      case 'ml': return 'ഇത് എന്തുകൊണ്ട് പ്രധാനമാണ്: ';
      case 'or': return 'ଏହା କାହିଁକି ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ: ';
      default: return 'Why this matters: ';
    }
  }

  static String getCanIKeepDrivingLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'क्या मैं गाड़ी चलाना जारी रख सकता हूँ?: ';
      case 'ta': return 'நான் தொடர்ந்து வண்டியை ஓட்டலாமா?: ';
      case 'te': return 'నేను డ్రైవింగ్ కొనసాగించవచ్చా?: ';
      case 'kn': return 'ನಾನು ವಾಹನ ಚಾಲನೆ ಮುಂದುವರಿಸಬಹುದೇ?: ';
      case 'bn': return 'আমি কি গাড়ি চালানো চালিয়ে যেতে পারি?: ';
      case 'gu': return 'શું હું ડ્રાઇવિંગ ચાલુ રાખી શકું?: ';
      case 'mr': return 'मी वाहन चालवणे सुरू ठेवू शकतो का?: ';
      case 'pa': return 'ਕੀ ਮੈਂ ਗੱਡੀ ਚਲਾਉਣਾ ਜਾਰੀ ਰੱਖ ਸਕਦਾ ਹਾਂ?: ';
      case 'ml': return 'എനിക്ക് ഡ്രൈവിംഗ് തുടരാൻ കഴിയുമോ?: ';
      case 'or': return 'ମୁଁ ଗାଡ଼ି ଚଳାଇବା ଜାରି ରଖିପାରିବି କି?: ';
      default: return 'Can I keep driving?: ';
    }
  }

  static String getMechanicChecklistTitle(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मैकेनिक चेकलिस्ट और तकनीकी विवरण';
      case 'ta': return 'மெக்கானிக் சரிபார்ப்புப் பட்டியல் மற்றும் தொழில்நுட்ப விவரங்கள்';
      case 'te': return 'మెకానిక్ చెక్‌లిస్ట్ & సాంకేతిక వివరాలు';
      case 'kn': return 'ಮೆಕ್ಯಾನಿಕ್ ಪರಿಶೀಲನಾಪಟ್ಟಿ ಮತ್ತು ತಾಂತ್ರಿಕ ವಿವರಗಳು';
      case 'bn': return 'মেকানিক চেকলিস্ট এবং প্রযুক্তিগত বিবরণ';
      case 'gu': return 'મિકેનિક ચેકલિસ્ટ અને ટેકનિકલ વિગતો';
      case 'mr': return 'मेकॅनिक चेकलिस्ट आणि तांत्रिक तपशील';
      case 'pa': return 'ਮਕੈਨਿਕ ਚੈੱਕਲਿਸਟ ਅਤੇ ਤਕਨੀਕੀ ਵੇਰਵੇ';
      case 'ml': return 'മെക്കാനിക് ചെക്ക്‌ലിസ്റ്റും സാങ്കേതിക വിവരങ്ങളും';
      case 'or': return 'ମେକାନିକ୍ ଯାଞ୍ଚ ତାଲିକା ଏବଂ ବୈଷୟିକ ବିବରଣୀ';
      default: return 'Mechanic Checklist & Technical Details';
    }
  }

  static String getWhatMechanicMayCheckLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मैकेनिक क्या जांच सकता है:';
      case 'ta': return 'மெக்கானிக் எதைச் சரிபார்க்கலாம்:';
      case 'te': return 'మెకానిక్ ఏమి తనిఖీ చేయవచ్చు:';
      case 'kn': return 'ಮೆಕ್ಯಾನಿಕ್ ಏನನ್ನು ಪರಿಶೀಲಿಸಬಹುದು:';
      case 'bn': return 'মেকানিক যা পরীক্ষা করতে পারে:';
      case 'gu': return 'મિકેનિક શું તપાસી શકે છે:';
      case 'mr': return 'मेकॅनिक काय तपासू शकतो:';
      case 'pa': return 'ਮਕੈਨਿਕ ਕੀ ਜਾਂਚ ਸਕਦਾ ਹੈ:';
      case 'ml': return 'മെക്കാനിക് എന്താണ് പരിശോധിക്കേണ്ടത്:';
      case 'or': return 'ମେକାନିକ୍ କ’ଣ ଯାଞ୍ଚ କରିପାରିବେ:';
      default: return 'What the mechanic may check:';
    }
  }

  static String getTechnicalDetailsLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'तकनीकी विवरण: ';
      case 'ta': return 'தொழில்நுட்ப விவரங்கள்: ';
      case 'te': return 'సాంకేతిక వివరాలు: ';
      case 'kn': return 'ತಾಂತ್ರಿಕ ವಿವರಗಳು: ';
      case 'bn': return 'প্রযুক্তিগত বিবরণ: ';
      case 'gu': return 'ટેકનિકલ વિગતો: ';
      case 'mr': return 'तांत्रिक तपशील: ';
      case 'pa': return 'ਤਕਨੀਕੀ ਵੇਰਵੇ: ';
      case 'ml': return 'സാങ്കേതിക വിവരങ്ങൾ: ';
      case 'or': return 'ବୈଷୟିକ ବିବରଣୀ: ';
      default: return 'Technical details: ';
    }
  }

  static String getCitationLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'संदर्भ / उद्धरण: ';
      case 'ta': return 'மேற்கோள்: ';
      case 'te': return 'ఆధారం: ';
      case 'kn': return 'ಉಲ್ಲೇಖ: ';
      case 'bn': return 'উদ্ধৃতি: ';
      case 'gu': return 'સંદર્ભ: ';
      case 'mr': return 'संदर्भ: ';
      case 'pa': return 'ਹਵਾਲਾ: ';
      case 'ml': return 'റഫറൻസ്: ';
      case 'or': return 'ସନ୍ଦର୍ଭ: ';
      default: return 'Citation: ';
    }
  }

  static String getSymptomsCausesTitle(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'लक्षण, कारण और तकनीकी विवरण';
      case 'ta': return 'அறிகுறிகள், காரணங்கள் மற்றும் தொழில்நுட்ப விவரங்கள்';
      case 'te': return 'లక్షణాలు, కారణాలు & సాంకేతిక వివరాలు';
      case 'kn': return 'ರೋಗಲಕ್ಷಣಗಳು, ಕಾರಣಗಳು ಮತ್ತು ತಾಂತ್ರಿಕ ವಿವರಗಳು';
      case 'bn': return 'লক্ষণ, কারণ এবং প্রযুক্তিগত বিবরণ';
      case 'gu': return 'લક્ષણો, કારણો અને તકનીકી વિગતો';
      case 'mr': return 'लक्षणे, कारणे आणि तांत्रिक तपशील';
      case 'pa': return 'ਲੱਛਣ, ਕਾਰਨ ਅਤੇ ਤਕਨੀਕੀ ਵੇਰਵੇ';
      case 'ml': return 'ലക്ഷണങ്ങൾ, കാരണങ്ങൾ, സാങ്കേതിക വിവരങ്ങൾ';
      case 'or': return 'ଲକ୍ଷଣ, କାରଣ ଏବଂ ବୈଷୟିକ ବିବରଣୀ';
      default: return 'Symptoms, Causes & Technical Details';
    }
  }

  static String getWhatYouMightNoticeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'आप क्या नोटिस कर सकते हैं (हो भी सकता है या नहीं भी):';
      case 'ta': return 'நீங்கள் கவனிக்கக்கூடியவை (ஏற்படலாம் அல்லது ஏற்படாமலும் இருக்கலாம்):';
      case 'te': return 'మీరు గమనించే విషయాలు (జరగవచ్చు లేదా జరగకపోవచ్చు):';
      case 'kn': return 'ನೀವು ಗಮನಿಸಬಹುದಾದ ಅಂಶಗಳು (ಸಂಭವಿಸಬಹುದು ಅಥವಾ ಇಲ್ಲದಿರಬಹುದು):';
      case 'bn': return 'আপনি যা লক্ষ্য করতে পারেন (ঘটতে পারে বা নাও পারে):';
      case 'gu': return 'તમે શું નોંધી શકો છો (થઈ શકે છે અથવા ન પણ થઈ શકે):';
      case 'mr': return 'तुमच्या लक्षात येणाऱ्या गोष्टी (होऊ शकते किंवा नाही):';
      case 'pa': return 'ਤੁਸੀਂ ਕੀ ਦੇਖ ਸਕਦੇ ਹੋ (ਹੋ ਵੀ ਸਕਦਾ ਹੈ ਜਾਂ ਨਹੀਂ ਵੀ):';
      case 'ml': return 'നിങ്ങൾ ശ്രദ്ധിച്ചേക്കാവുന്ന ലക്ഷണങ്ങൾ:';
      case 'or': return 'ଆପଣ କ’ଣ ଲକ୍ଷ୍ୟ କରିପାରନ୍ତି (ଘଟିପାରେ କିମ୍ବା ନ ହୋଇପାରେ):';
      default: return 'What you might notice (may or may not occur):';
    }
  }

  static String getPossibleCausesLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'संभावित कारण / जांच के क्षेत्र:';
      case 'ta': return 'சாத்தியமான காரணங்கள் / சரிபார்க்க வேண்டிய பகுதிகள்:';
      case 'te': return 'సాధ్యమయ్యే కారణాలు / తనిఖీ చేయవలసిన ప్రాంతాలు:';
      case 'kn': return 'ಸಂಭಾವ್ಯ ಕಾರಣಗಳು / ಪರಿಶೀಲಿಸಬೇಕಾದ ಪ್ರದೇಶಗಳು:';
      case 'bn': return 'সম্ভাব্য কারণ / পরীক্ষা করার ক্ষেত্র:';
      case 'gu': return 'સંભવિત કારણો / તપાસવાના ક્ષેત્રો:';
      case 'mr': return 'संभाव्य कारणे / तपासण्याची क्षेत्रे:';
      case 'pa': return 'ਸੰਭਾਵੀ ਕਾਰਨ / ਜਾਂਚ ਕਰਨ ਵਾਲੇ ਖੇਤਰ:';
      case 'ml': return 'സാധ്യമായ കാരണങ്ങൾ / പരിശോധിക്കേണ്ട മേഖലകൾ:';
      case 'or': return 'ସମ୍ଭାବ୍ୟ କାରଣ / ଯାଞ୍ଚ କରିବା କ୍ଷେତ୍ର:';
      default: return 'Possible causes / areas to check:';
    }
  }

  static String getNoticeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सूचना: ';
      case 'ta': return 'அறிவிப்பு: ';
      case 'te': return 'గమనిక: ';
      case 'kn': return 'ಸೂಚನೆ: ';
      case 'bn': return 'বিজ্ঞপ্তি: ';
      case 'gu': return 'સૂચના: ';
      case 'mr': return 'सूचना: ';
      case 'pa': return 'ਸੂਚਨਾ: ';
      case 'ml': return 'അറിയിപ്പ്: ';
      case 'or': return 'ସୂଚନା: ';
      default: return 'Notice: ';
    }
  }

  static String getStandardDefinitionLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मानक परिभाषा: ';
      case 'ta': return 'நிலையான வரையறை: ';
      case 'te': return 'ప్రామాణిక నిర్వచనం: ';
      case 'kn': return 'ಪ್ರಮಾಣಿತ ವ್ಯಾಖ್ಯಾನ: ';
      case 'bn': return 'মানক সংজ্ঞা: ';
      case 'gu': return 'પ્રમાણભૂત વ્યાખ્યા: ';
      case 'mr': return 'मानक व्याख्या: ';
      case 'pa': return 'ਮਿਆਰੀ ਪਰਿਭਾਸ਼ਾ: ';
      case 'ml': return 'സ്റ്റാൻഡേർഡ് നിർവചനം: ';
      case 'or': return 'ମାନକ ସଂଜ୍ଞା: ';
      default: return 'Standard definition: ';
    }
  }

  static String getVerifiedSourceLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सत्यापित स्रोत: ';
      case 'ta': return 'சரிபார்க்கப்பட்ட ஆதாரம்: ';
      case 'te': return 'ధృవీకరించబడిన మూలం: ';
      case 'kn': return 'ದೃಢೀಕರಿಸಿದ ಮೂಲ: ';
      case 'bn': return 'যাচাইকৃত উৎস: ';
      case 'gu': return 'ચકાસાયેલ સ્ત્રોત: ';
      case 'mr': return 'सत्यापित स्रोत: ';
      case 'pa': return 'ਪ੍ਰਮਾਣਿਤ ਸਰੋਤ: ';
      case 'ml': return 'പരിശോധിച്ച ഉറവിടം: ';
      case 'or': return 'ପ୍ରମାଣିତ ଉତ୍ସ: ';
      default: return 'Verified Source: ';
    }
  }

  static String getNoObdTelemetryText(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'इस निरीक्षण के साथ कोई OBD-II टेलीमेट्री लॉग अपलोड नहीं किया गया था। पावरट्रेन और इलेक्ट्रॉनिक सबसिस्टम के स्वास्थ्य का मूल्यांकन नहीं किया गया था।';
      case 'ta': return 'இந்த ஆய்வில் OBD-II டெலிமெட்ரி பதிவு பதிவேற்றப்படவில்லை. எஞ்சின் மற்றும் மின்னணு பாகங்களின் நிலை மதிப்பீடு செய்யப்படவில்லை.';
      case 'te': return 'ఈ తనిఖీతో OBD-II టెలిమెట్రీ లాగ్ అప్‌లోడ్ చేయబడలేదు. ఇంజిన్ మరియు ఎలక్ట్రానిక్ వ్యవస్థల స్థితి మూల్యాంకనం చేయబడలేదు.';
      case 'kn': return 'ಈ ತಪಾಸಣೆಯೊಂದಿಗೆ ಯಾವುದೇ OBD-II ಟೆಲಿಮೆಟ್ರಿ ಲಾಗ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಲಾಗಿಲ್ಲ.';
      case 'bn': return 'এই পরিদর্শনের সাথে কোন OBD-II টেলিমেট্রি লগ আপলোড করা হয়নি।';
      case 'gu': return 'આ તપાસ સાથે કોઈ OBD-II ટેલિમેટ્રી લોગ અપલોડ કરવામાં આવ્યો ન હતો.';
      case 'mr': return 'या तपासणीसह कोणताही OBD-II टेलिमेट्री लॉग अपलोड केलेला नाही.';
      case 'pa': return 'ਇਸ ਨਿਰੀਖਣ ਨਾਲ ਕੋਈ OBD-II ਟੈਲੀਮੈਟਰੀ ਲੌਗ ਅੱਪਲੋਡ ਨਹੀਂ ਕੀਤਾ ਗਿਆ ਸੀ।';
      case 'ml': return 'ഈ പരിശോധനയോടൊപ്പം OBD-II ടെലിമെട്രി ലോഗ് അപ്‌ലോഡ് ചെയ്തിട്ടില്ല.';
      case 'or': return 'ଏହି ଯାଞ୍ଚ ସହିତ କୌଣସି OBD-II ଟେଲିମେଟ୍ରି ଲଗ୍ ଅପଲୋଡ୍ ହୋଇନାହିଁ।';
      default: return 'No OBD-II telemetry log was uploaded with this inspection. Powertrain and electronic subsystem health was not evaluated.';
    }
  }

  static String getNoGuidanceText(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'कॉन्फ़िगर किए गए ज्ञानकोष में कोई सत्यापित मरम्मत मार्गदर्शन नहीं मिला।';
      case 'ta': return 'வழங்கப்பட்ட தரவுத்தளத்தில் சரிபார்க்கப்பட்ட பழுதுபார்ப்பு வழிகாட்டுதல் எதுவும் கிடைக்கவில்லை.';
      case 'te': return 'నాలెడ్జ్ బేస్‌లో ధృవీకరించబడిన మరమ్మతు మార్గదర్శకత్వం కనుగొనబడలేదు.';
      case 'kn': return 'ಯಾವುದೇ ದೃಢೀಕರಿಸಿದ ದುರಸ್ತಿ ಮಾರ್ಗದರ್ಶನ ಕಂಡುಬಂದಿಲ್ಲ.';
      case 'bn': return 'কোন যাচাইকৃত মেরামত নির্দেশিকা পাওয়া যায়নি।';
      case 'gu': return 'કોઈ ચકાસાયેલ સમારકામ માર્ગદર્શન મળ્યું નથી.';
      case 'mr': return 'कोणतेही सत्यापित दुरुस्ती मार्गदर्शन आढळले नाही.';
      case 'pa': return 'ਕੋਈ ਪ੍ਰਮਾਣਿਤ ਮੁਰੰਮਤ ਮਾਰਗਦਰਸ਼ਨ ਨਹੀਂ ਮਿਲਿਆ।';
      case 'ml': return 'സ്ഥിരീകരിച്ച റിപ്പയർ മാർഗ്ഗനിർദ്ദേശങ്ങളൊന്നും കണ്ടെത്തിയില്ല.';
      case 'or': return 'କୌଣସି ପ୍ରମାଣିତ ମରାମତି ମାର୍ଗଦର୍ଶିକା ମିଳିଲା ନାହିଁ।';
      default: return 'No verified repair guidance was found in the configured knowledge base.';
    }
  }

  static String getReadingLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'रीडिंग: ';
      case 'ta': return 'அளவீடு: ';
      case 'te': return 'రీడింగ్: ';
      case 'kn': return 'ರೀಡಿಂಗ್: ';
      case 'bn': return 'রিডিং: ';
      case 'gu': return 'રીડિંગ: ';
      case 'mr': return 'वाचन: ';
      case 'pa': return 'ਰੀਡਿੰਗ: ';
      case 'ml': return 'റീഡിംഗ്: ';
      case 'or': return 'ରିଡିଂ: ';
      default: return 'Reading: ';
    }
  }

  static String getOutsideMonitoringRangeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'निगरानी सीमा से बाहर';
      case 'ta': return 'கண்காணிப்பு வரம்பிற்கு வெளியே';
      case 'te': return 'పర్యవేక్షణ పరిధి వెలుపల';
      case 'kn': return 'ಮೇಲ್ವಿಚಾರಣಾ ವ್ಯಾಪ್ತಿಯ ಹೊರಗೆ';
      case 'bn': return 'পর্যবেক্ষণ সীমার বাইরে';
      case 'gu': return 'નિરીક્ષણ શ્રેણીની બહાર';
      case 'mr': return 'निरीक्षण मर्यादेबाहेर';
      case 'pa': return 'ਨਿਗਰਾਨੀ ਸੀਮਾ ਤੋਂ ਬਾਹਰ';
      case 'ml': return 'നിരീക്ഷണ പരിധിക്ക് പുറത്ത്';
      case 'or': return 'ନିରୀକ୍ଷଣ ପରିସର ବାହାରେ';
      default: return 'Outside Monitoring Range';
    }
  }

  static String getWhatDoesThisNumberMeanLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'इस संख्या का क्या अर्थ है?';
      case 'ta': return 'இந்த எண்ணின் பொருள் என்ன?';
      case 'te': return 'ఈ సంఖ్య అర్థం ఏమిటి?';
      case 'kn': return 'ಈ ಸಂಖ್ಯೆಯ ಅರ್ಥವೇನು?';
      case 'bn': return 'এই সংখ্যার অর্থ কি?';
      case 'gu': return 'આ સંખ્યાનો અર્થ શું છે?';
      case 'mr': return 'या संख्येचा अर्थ काय आहे?';
      case 'pa': return 'ਇਸ ਨੰਬਰ ਦਾ ਕੀ ਅਰਥ ਹੈ?';
      case 'ml': return 'ഈ സംഖ്യയുടെ അർത്ഥമെന്താണ്?';
      case 'or': return 'ଏହି ସଂଖ୍ୟାର ଅର୍ଥ କ’ଣ?';
      default: return 'What does this number mean?';
    }
  }

  static String getHowOftenDidThisHappenLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'यह कितनी बार हुआ?';
      case 'ta': return 'இது எத்தனை முறை நடந்தது?';
      case 'te': return 'ఇది ఎంత తరచుగా జరిగింది?';
      case 'kn': return 'ಇದು ಎಷ್ಟು ಬಾರಿ ಸಂಭವಿಸಿತು?';
      case 'bn': return 'এটি কত ঘনঘন ঘটেছে?';
      case 'gu': return 'આ કેટલી વાર બન્યું?';
      case 'mr': return 'हे किती वेळा घडले?';
      case 'pa': return 'ਇਹ ਕਿੰਨੀ ਵਾਰ ਹੋਇਆ?';
      case 'ml': return 'ഇത് എത്ര തവണ സംഭവിച്ചു?';
      case 'or': return 'ଏହା କେତେ ଥର ଘଟିଲା?';
      default: return 'How often did this happen?';
    }
  }

  static String getPidPossibleCausesTitle(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'संभावित कारण, सीमाएं और तकनीकी संदर्भ';
      case 'ta': return 'சாத்தியமான காரணங்கள், வரம்புகள் மற்றும் குறிப்புகள்';
      case 'te': return 'సాధ్యమయ్యే కారణాలు, పరిమితులు & సాంకేతిక సూచన';
      case 'kn': return 'ಸಂಭಾವ್ಯ ಕಾರಣಗಳು, ಮಿತಿಗಳು ಮತ್ತು ತಾಂತ್ರಿಕ ಉಲ್ಲೇಖ';
      case 'bn': return 'সম্ভাব্য কারণ, সীমাবদ্ধতা এবং প্রযুক্তিগত রেফারেন্স';
      case 'gu': return 'સંભવિત કારણો, મર્યાદાઓ અને તકનીકી સંદર્ભ';
      case 'mr': return 'संभाव्य कारणे, मर्यादा आणि तांत्रिक संदर्भ';
      case 'pa': return 'ਸੰਭਾਵੀ ਕਾਰਨ, ਸੀਮਾਵਾਂ ਅਤੇ ਤਕਨੀਕੀ ਹਵਾਲਾ';
      case 'ml': return 'സാധ്യമായ കാരണങ്ങൾ, പരിധികൾ, സാങ്കേതിക വിവരങ്ങൾ';
      case 'or': return 'ସମ୍ଭାବ୍ୟ କାରଣ, ସୀମାବଦ୍ଧତା ଏବଂ ବୈଷୟିକ ଉଲ୍ଲେଖ';
      default: return 'Possible Causes, Limitations & Technical Reference';
    }
  }

  static String getPossibleReasonsInvestigateLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'जांच के संभावित कारण (संभावनाएं, कोई पुष्ट निदान नहीं):';
      case 'ta': return 'ஆராய்வதற்கான சாத்தியமான காரணங்கள் (சாத்தியக்கூறுகள், உறுதிப்படுத்தப்பட்ட நோயறிதல் அல்ல):';
      case 'te': return 'పరిశోధించవలసిన సంభావ్య కారణాలు (అవకాశాలు, నిర్ధారిత రోగ నిర్ధారణ కాదు):';
      case 'kn': return 'ತನಿಖೆ ಮಾಡಬೇಕಾದ ಸಂಭವನೀಯ ಕಾರಣಗಳು (ಸಾಧ್ಯತೆಗಳು, ದೃಢಪಡಿಸಿದ ರೋಗನಿರ್ಣಯವಲ್ಲ):';
      case 'bn': return 'তদন্তের সম্ভাব্য কারণ (সম্ভাবনা, নিশ্চিত রোগ নির্ণয় নয়):';
      case 'gu': return 'તપાસવાના સંભવિત કારણો (શક્યતાઓ, પુષ્ટિ થયેલ નિદાન નથી):';
      case 'mr': return 'तपासणीची संभाव्य कारणे (शक्यता, पुष्टी झालेले निदान नाही):';
      case 'pa': return 'ਜਾਂਚ ਦੇ ਸੰਭਾਵੀ ਕਾਰਨ (ਸੰਭਾਵਨਾਵਾਂ, ਕੋਈ ਪੁਸ਼ਟੀ ਕੀਤੀ ਜਾਂਚ ਨਹੀਂ):';
      case 'ml': return 'അന്വേഷിക്കേണ്ട സാധ്യമായ കാരണങ്ങൾ (സാധ്യതകൾ, സ്ഥിരീകരിച്ച രോഗനിർണയമല്ല):';
      case 'or': return 'ତଦନ୍ତ ପାଇଁ ସମ୍ଭାବ୍ୟ କାରଣ (ସମ୍ଭାବନା, ନିଶ୍ଚିତ ନିଦାନ ନୁହେଁ):';
      default: return 'Possible reasons to investigate (Possibilities, not confirmed diagnosis):';
    }
  }

  static String getImportantNoticePrefix(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'महत्वपूर्ण सूचना: ';
      case 'ta': return 'முக்கிய அறிவிப்பு: ';
      case 'te': return 'ముఖ్యమైన గమనిక: ';
      case 'kn': return 'ಪ್ರಮುಖ ಸೂಚನೆ: ';
      case 'bn': return 'গুরুত্বপূর্ণ বিজ্ঞপ্তি: ';
      case 'gu': return 'મહત્વપૂર્ણ સૂચના: ';
      case 'mr': return 'महत्त्वाची सूचना: ';
      case 'pa': return 'ਮਹੱਤਵਪੂਰਨ ਸੂਚਨਾ: ';
      case 'ml': return 'പ്രധാന അറിയിപ്പ്: ';
      case 'or': return 'ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ସୂଚନା: ';
      default: return 'Important: ';
    }
  }

  static String getConfiguredMonitoringRangeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'कॉन्फ़िगर की गई निगरानी सीमा: ';
      case 'ta': return 'கட்டமைக்கப்பட்ட கண்காணிப்பு வரம்பு: ';
      case 'te': return 'కాన్ఫిగర్ చేయబడిన పర్యవేక్షణ పరిధి: ';
      case 'kn': return 'ಕಾನ್ಫಿಗರ್ ಮಾಡಲಾದ ಮೇಲ್ವಿಚಾರಣಾ ಶ್ರೇಣಿ: ';
      case 'bn': return 'কনফিগার করা পর্যবেক্ষণ পরিসীমা: ';
      case 'gu': return 'રૂપરેખાંકિત નિરીક્ષણ શ્રેણી: ';
      case 'mr': return 'कॉन्फिगर केलेली निरीक्षण श्रेणी: ';
      case 'pa': return 'ਸੰਰਚਿਤ ਨਿਗਰਾਨੀ ਸੀਮਾ: ';
      case 'ml': return 'കോൺഫിഗർ ചെയ്ത നിരീക്ഷണ പരിധി: ';
      case 'or': return 'କନଫିଗର ହୋଇଥିବା ନିରୀକ୍ଷଣ ପରିସର: ';
      default: return 'Configured Monitoring Range: ';
    }
  }

  static String getTechnicalContextLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'तकनीकी संदर्भ: ';
      case 'ta': return 'தொழில்நுட்ப சூழல்: ';
      case 'te': return 'సాంకేతిక సందర్భం: ';
      case 'kn': return 'ತಾಂತ್ರಿಕ ಸಂದರ್ಭ: ';
      case 'bn': return 'প্রযুক্তিগত প্রসঙ্গ: ';
      case 'gu': return 'તકનીકી સંદર્ભ: ';
      case 'mr': return 'तांत्रिक संदर्भ: ';
      case 'pa': return 'ਤਕਨੀਕੀ ਪ੍ਰਸੰਗ: ';
      case 'ml': return 'സാങ്കേതിക പശ്ചാത്തലം: ';
      case 'or': return 'ବୈଷୟିକ ପ୍ରସଙ୍ଗ: ';
      default: return 'Technical Context: ';
    }
  }

  static String getStandardReferenceLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मानक संदर्भ: ';
      case 'ta': return 'நிலையான குறிப்பு: ';
      case 'te': return 'ప్రామాణిక సూచన: ';
      case 'kn': return 'ಪ್ರಮಾಣಿತ ಉಲ್ಲೇಖ: ';
      case 'bn': return 'মানক রেফারেন্স: ';
      case 'gu': return 'માનક સંદર્ભ: ';
      case 'mr': return 'मानक संदर्भ: ';
      case 'pa': return 'ਮਿਆਰੀ ਹਵਾਲਾ: ';
      case 'ml': return 'സ്റ്റാൻഡേർഡ് റഫറൻസ്: ';
      case 'or': return 'ମାନକ ସନ୍ଦର୍ଭ: ';
      default: return 'Standard Reference: ';
    }
  }

  // ---------------------------------------------------------------------------
  // 5. DTC Translations Map
  // ---------------------------------------------------------------------------
  static final Map<String, Map<String, Map<String, dynamic>>> _dtcTranslations = {
    'hi': {
      'P0128': {
        'title': 'इंजन अपेक्षित तापमान तक नहीं पहुँच रहा है',
        'what_it_means': 'आपका इंजन वाहन कंप्यूटर द्वारा निर्धारित सामान्य तापमान तक गर्म नहीं हो पा रहा है। थर्मोस्टेट या तापमान सेंसर की खराबी इसका एक संभावित कारण हो सकती है।',
        'what_you_should_do': 'इंजन कूलिंग सिस्टम की जांच करवाएं। यदि अधिक गर्म होने या कूलेंट चेतावनी दिखे, तो सुरक्षित रूप से रुकें और निर्माता के निर्देशों का पालन करें।',
      },
      'P0133': {
        'title': 'ऑक्सीजन सेंसर धीमी प्रतिक्रिया दे रहा है',
        'what_it_means': 'ईंधन और उत्सर्जन को नियंत्रित करने वाला सेंसर सामान्य से धीमी गति से प्रतिक्रिया दे रहा है। सेंसर या इंजन से जुड़ी कोई अन्य समस्या इसका कारण हो सकती है।',
        'what_you_should_do': 'पार्ट्स बदलने से पहले पेशेवर डायग्नोस्टिक जांच करवाएं।',
      },
      'P0171': {
        'title': 'इंजन मिश्रण में ईंधन बहुत कम (Lean) है',
        'what_it_means': 'इंजन कंप्यूटर हवा की मात्रा अधिक या ईंधन की मात्रा अपर्याप्त पा रहा है।',
        'what_you_should_do': 'इंटेक सिस्टम में वैक्यूम लीक और मास एयर फ्लो (MAF) सेंसर की जांच करवाएं।',
      },
      'P0300': {
        'title': 'अनियमित / एकाधिक सिलेंडर मिसफायर का पता चला',
        'what_it_means': 'इंजन कंप्यूटर ने पाया है कि एक या अधिक सिलेंडरों में ईंधन ठीक से नहीं जल रहा है।',
        'what_you_should_do': 'यदि इंजन चेतावनी लाइट चमक रही है या गाड़ी कांप रही है, तो तुरंत सुरक्षित स्थान पर रुकें। स्पार्क प्लग और इग्निशन कॉइल की तत्काल जांच करवाएं।',
      },
      'P0401': {
        'title': 'ईजीआर (EGR) गैस प्रवाह अपर्याप्त है',
        'what_it_means': 'एग्जॉस्ट गैस रीसर्कुलेशन सिस्टम में प्रवाह अपेक्षित से कम है। वाल्व या ट्यूब में रुकावट इसका कारण हो सकती है।',
        'what_you_should_do': 'पार्ट्स बदलने से पहले ईजीआर वाल्व और ट्यूबों में कार्बन जमाव की जांच करवाएं।',
      },
      'P0420': {
        'title': 'कैटेलिटिक कन्वर्टर दक्षता स्तर से नीचे कार्य कर रहा है',
        'what_it_means': 'कैटेलिटिक कन्वर्टर उत्सर्जन गैसों को पूरी तरह से साफ नहीं कर पा रहा है।',
        'what_you_should_do': 'कन्वर्टर बदलने से पहले संपूर्ण एग्जॉस्ट और ऑक्सीजन सेंसर की जांच करवाएं।',
      },
      'P0442': {
        'title': 'ईवीएपी (EVAP) सिस्टम में छोटा वाष्प रिसाव',
        'what_it_means': 'ईंधन वाष्पीकरण नियंत्रण प्रणाली में एक छोटा रिसाव मिला है।',
        'what_you_should_do': 'जांचें कि फ्यूल कैप ठीक से कसी हुई है या नहीं। यदि चेतावनी बनी रहे तो जांच करवाएं।',
      },
      'P0455': {
        'title': 'ईवीएपी (EVAP) सिस्टम में बड़ा वाष्प रिसाव / ढीला कैप',
        'what_it_means': 'ईंधन वाष्प नियंत्रण प्रणाली में बड़ा रिसाव या खुला फ्यूल कैप पाया गया है।',
        'what_you_should_do': 'जांचें कि फ्यूल टैंक कैप ढीली या गायब तो नहीं है। यदि कैप सही है तो सर्विस करवाएं।',
      },
    },
    'ta': {
      'P0128': {
        'title': 'என்ஜின் நிர்ணயிக்கப்பட்ட வெப்பநிலையை எட்டவில்லை',
        'what_it_means': 'வாகன கணினி எதிர்பார்க்கும் வெப்பநிலையை என்ஜின் எட்டவில்லை. தெர்மோஸ்டாட் அல்லது வெப்பநிலை சென்சார் பிரச்சனை காரணமாக இருக்கலாம்.',
        'what_you_should_do': 'குளிரூட்டும் அமைப்பை சரிபார்க்கவும். அதிக வெப்ப எச்சரிக்கை வந்தால் வாகனத்தை பாதுகாப்பாக நிறுத்துங்கள்.',
      },
      'P0133': {
        'title': 'ஆக்ஸிஜன் சென்சார் தாமதமாக பதிலளிக்கிறது',
        'what_it_means': 'எரிபொருள் மற்றும் புகையைக் கட்டுப்படுத்தும் சென்சார் எதிர்பார்த்ததை விட தாமதமாக பதிலளிக்கிறது. சென்சார் அல்லது என்ஜின் பிரச்சனை காரணமாக இருக்கலாம்.',
        'what_you_should_do': 'உதிரிபாகங்களை மாற்றுவதற்கு முன் கணினி பரிசோதனை செய்து உறுதிப்படுத்தவும்.',
      },
      'P0171': {
        'title': 'என்ஜின் எரிபொருள் கலவை மிகவும் குறைவு (Lean)',
        'what_it_means': 'என்ஜினில் காற்று அதிகமாகவும் எரிபொருள் குறைவாகவும் உள்ளதாக கணினி கண்டறிந்துள்ளது.',
        'what_you_should_do': 'காற்று கசிவு மற்றும் எரிபொருள் அழுத்தத்தை பரிசோதிக்கவும்.',
      },
      'P0300': {
        'title': 'என்ஜின் சிலிண்டர் மிஸ்பயர் கண்டறியப்பட்டது',
        'what_it_means': 'என்ஜினின் ஒன்றுக்கும் மேற்பட்ட சிலிண்டர்களில் எரிபொருள் சரியாக எரியவில்லை.',
        'what_you_should_do': 'என்ஜின் விளக்கு மின்னினால் உடனடியாக வாகனத்தை பாதுகாப்பாக நிறுத்துங்கள். ஸ்பார்க் பிளக்குகளை உடனே பரிசோதிக்கவும்.',
      },
      'P0401': {
        'title': 'EGR வாயு மறுசுழற்சி ஓட்டம் போதுமானதாக இல்லை',
        'what_it_means': 'புகை மறுசுழற்சி அமைப்பில் ஓட்டம் குறைவாக உள்ளது. வால்வில் அடைப்பு ஏற்பட்டிருக்கலாம்.',
        'what_you_should_do': 'பாகங்களை மாற்றுவதற்கு முன் EGR வால்வில் உள்ள அடைப்பை சரிபார்க்கவும்.',
      },
      'P0420': {
        'title': 'கேடலிடிக் கன்வெர்ட்டர் செயல்திறன் குறைவு',
        'what_it_means': 'புகையை சுத்திகரிக்கும் கன்வெர்ட்டர் எதிர்பார்த்த அளவிற்கு செயல்படவில்லை.',
        'what_you_should_do': 'கன்வெர்ட்டரை மாற்றுவதற்கு முன் முழுமையான பரிசோதனை மேற்கொள்ளவும்.',
      },
    },
    'te': {
      'P0128': {
        'title': 'ఇంజిన్ అవసరమైన ఉష్ణోగ్రతను చేరుకోవడం లేదు',
        'what_it_means': 'వాహన కంప్యూటర్ ఊహించిన సాధారణ ఉష్ణోగ్రతకు ఇంజిన్ వేడెక్కడం లేదు. థర్మోస్టాట్ సమస్య కావచ్చు.',
        'what_you_should_do': 'ఇంజిన్ కూలింగ్ సిస్టమ్‌ను మెకానిక్‌తో తనిఖీ చేయించండి.',
      },
      'P0133': {
        'title': 'ఆక్సిజన్ సెన్సార్ ఆలస్యంగా స్పందిస్తోంది',
        'what_it_means': 'ఇంధనం మరియు ఉద్గారాలను నిర్వహించే సెన్సార్ సాధారణం కంటే నెమ్మదిగా స్పందిస్తోంది.',
        'what_you_should_do': 'భాగాలను మార్చడానికి ముందు కంప్యూటర్ తనిఖీని ఏర్పాటు చేయండి.',
      },
      'P0171': {
        'title': 'ఇంధన మిశ్రమం చాలా తక్కువగా ఉంది (Lean)',
        'what_it_means': 'ఇంజిన్‌లో గాలి ఎక్కువగా మరియు ఇంధనం తక్కువగా ఉన్నట్లు గుర్తించబడింది.',
        'what_you_should_do': 'ఇన్‌టేక్ సిస్టమ్‌లో గాలి లీక్‌లను పరిశీలించండి.',
      },
      'P0300': {
        'title': 'సిలిండర్ మిస్‌ఫైర్ గుర్తించబడింది',
        'what_it_means': 'ఒకటి కంటే ఎక్కువ సిలిండర్లలో ఇంధనం సరిగ్గా మండటం లేదు.',
        'what_you_should_do': 'ఇంజిన్ లైట్ మెరుస్తుంటే సురక్షితంగా ఆపండి. స్పార్క్ ప్లగ్‌లను తనిఖీ చేయించండి.',
      },
      'P0401': {
        'title': 'EGR వాయు ప్రవాహం సరిపోవడం లేదు',
        'what_it_means': 'ఎగ్జాస్ట్ గ్యాస్ రీసర్క్యులేషన్ సిస్టమ్‌లో ప్రవాహం తక్కువగా ఉంది. వాల్వ్ సమస్య కావచ్చు.',
        'what_you_should_do': 'EGR వాల్వ్ మరియు ట్యూబ్‌లను శుభ్రం చేయించండి.',
      },
      'P0420': {
        'title': 'కెటలిటిక్ కన్వర్టర్ సామర్థ్యం తక్కువగా ఉంది',
        'what_it_means': 'కెటలిటిక్ కన్వర్టర్ ఉద్గారాలను సరిగ్గా శుభ్రపరచడం లేదు.',
        'what_you_should_do': 'కన్వర్టర్ మార్చే ముందు ఎగ్జాస్ట్ తనిఖీ చేయించండి.',
      },
    },
  };

  // ---------------------------------------------------------------------------
  // 6. Guidance Passages Map
  // ---------------------------------------------------------------------------
  static final Map<String, Map<String, Map<String, dynamic>>> _guidanceTranslations = {
    'hi': {
      'P0300': {
        'title': 'सिलेंडर मिसफायर सुरक्षा एवं मरम्मत मार्गदर्शन (DTC P0300)',
        'what_we_found': 'इंजन कंप्यूटर ने पाया है कि एक या अधिक सिलेंडरों में ईंधन सही तरीके से नहीं जल रहा है।',
        'why_this_matters': 'बार-बार मिसफायर होने से बिना जला ईंधन साइलेंसर में जाता है, जिससे पिकअप गिरता है, वाहन कांपता है और कैटेलिटिक कन्वर्टर अत्यधिक गर्म होकर खराब हो सकता है।',
        'what_you_should_do_now': 'यदि इंजन चेतावनी लाइट चमक रही है या गाड़ी जोर से कांप रही है, तो तुरंत सुरक्षित स्थान पर रुकें और इंजन बंद करें। भारी त्वरण से बचें और तत्काल जांच करवाएं।',
        'can_i_keep_driving': 'अनावश्यक ड्राइविंग से बचें; तुरंत मैकेनिक को दिखाएं।',
        'technical_details': 'SAE J2012 के अनुसार P0300 तब दर्ज होता है जब क्रैंकशाफ्ट घूर्णन अनियमितता कई सिलेंडरों में मिसफायर दर्शाती है। बिना जला ईंधन कैटेलिटिक कन्वर्टर को अत्यधिक गर्म कर सकता है।',
        'mechanic_checks': [
          'स्पार्क प्लग और इग्निशन कॉइल की स्थिति',
          'ईंधन दबाव और फ्यूल इंजेक्टर',
          'एयर इंटेक और वैक्यूम पाइप में रिसाव',
          'इंजन कंप्रेशन और टाइमिंग'
        ],
      },
      'P0128': {
        'title': 'इंजन तापमान अपेक्षित स्तर से कम (DTC P0128)',
        'what_we_found': 'इंजन सामान्य ऑपरेटिंग तापमान तक पहुँचने में आवश्यकता से अधिक समय ले रहा है।',
        'why_this_matters': 'कम तापमान पर चलने से माइलेज कम होती है, केबिन हीटर ठंडा रहता है और प्रदूषण बढ़ सकता है।',
        'what_you_should_do_now': 'कूलिंग सिस्टम का थर्मोस्टेट और तापमान सेंसर चेक करवाएं।',
        'can_i_keep_driving': 'शीघ्र मैकेनिक से अपॉइंटमेंट लें।',
        'technical_details': 'SAE J2012 के अनुसार P0128 तब सेट होता है जब इंजन कूलेंट निर्धारित समय के भीतर आवश्यक तापमान तक नहीं पहुँचता।',
        'mechanic_checks': [
          'थर्मोस्टेट (जांचें कि खुला तो नहीं अटक गया)',
          'कूलेंट तापमान सेंसर का प्रतिरोध',
          'कूलेंट स्तर और पंखे का संचालन'
        ],
      },
      'P0401': {
        'title': 'ईजीआर गैस प्रवाह अपर्याप्त (DTC P0401)',
        'what_we_found': 'इंजन में एग्जॉस्ट गैस लौटाने वाले सिस्टम में प्रवाह सामान्य से कम पाया गया है। रुकावट या वाल्व की खराबी इसका कारण हो सकती है।',
        'why_this_matters': 'ईजीआर सिस्टम इंजन के दहन तापमान को नियंत्रित करता है और उत्सर्जन कम करता है; कम प्रवाह से अधिक लोड पर खटखटाने की आवाज (pinging) और प्रदूषण बढ़ सकता है।',
        'what_you_should_do_now': 'पार्ट्स बदलने से पहले ईजीआर सिस्टम की जांच करवाएं।',
        'can_i_keep_driving': 'शीघ्र मैकेनिक से अपॉइंटमेंट लें।',
        'technical_details': 'SAE J2012 के अनुसार P0401 तब सेट होता है जब ईसीएम परीक्षण के दौरान ईजीआर प्रवाह दर आवश्यक सीमा से कम पाई जाती है।',
        'mechanic_checks': [
          'ईजीआर वाल्व में कार्बन जमाव',
          'ईजीआर प्रेशर सेंसर (DPFE)',
          'ईजीआर पाइप की सफाई'
        ],
      },
      'P0171': {
        'title': 'कम ईंधन मिश्रण मार्गदर्शन (DTC P0171)',
        'what_we_found': 'सिलेंडर बैंक 1 में हवा की मात्रा अधिक या ईंधन की मात्रा अपर्याप्त पाई गई है।',
        'why_this_matters': 'लीन मिक्सचर से गाड़ी झटके ले सकती है, गति धीमी हो सकती है और इंजन का तापमान बढ़ सकता है।',
        'what_you_should_do_now': 'इंटेक वैक्यूम लीक और एयर फिल्टर सेंसर की जांच करवाएं।',
        'can_i_keep_driving': 'अनावश्यक ड्राइविंग से बचें; जल्द निरीक्षण करवाएं।',
        'technical_details': 'SAE J2012 के अनुसार P0171 तब सक्रिय होता है जब ईंधन ट्रिम मान स्वीकार्य अनुकूलन सीमा से अधिक हो जाते हैं।',
        'mechanic_checks': [
          'इंटेक बूट और वैक्यूम होज़',
          'मास एयर फ्लो सेंसर',
          'फ्यूल पंप दबाव और फिल्टर'
        ],
      },
    },
    'ta': {
      'P0300': {
        'title': 'என்ஜின் சிலிண்டர் மிஸ்பயர் பாதுகாப்பு வழிகாட்டுதல் (DTC P0300)',
        'what_we_found': 'என்ஜினின் ஒன்று அல்லது அதற்கு மேற்பட்ட சிலிண்டர்களில் எரிபொருள் சரியாக எரியவில்லை என்று கண்டறியப்பட்டுள்ளது.',
        'why_this_matters': 'தொடர்ச்சியான மிஸ்பயரினால் எரியாத எரிபொருள் வெளியேறி, புகை சுத்திகரிப்பான் சேதமடையக்கூடும் மற்றும் என்ஜின் அதிரும்.',
        'what_you_should_do_now': 'என்ஜின் எச்சரிக்கை விளக்கு மின்னினால் உடனடியாக பாதுகாப்பான இடத்தில் வண்டியை நிறுத்தி என்ஜினை அணையுங்கள். தாமதிக்காமல் மெக்கானிக்கை அணுகவும்.',
        'can_i_keep_driving': 'தேவையற்ற பயணங்களைத் தவிர்க்கவும்; உடனடியாக மெக்கானிக்கிடம் செல்லவும்.',
        'technical_details': 'SAE J2012 வரையறையின்படி P0300 கிராங்க்ஷாஃப்ட் சீரற்ற சுழற்சியைக் குறிக்கிறது.',
        'mechanic_checks': [
          'ஸ்பார்க் பிளக் மற்றும் இக்னிஷன் காயில்கள்',
          'எரிபொருள் அழுத்தம் மற்றும் இன்ஜெக்டர்கள்',
          'காற்று குழாய் கசிவுகள்',
          'என்ஜின் டைமிங் மற்றும் அழுத்தம்'
        ],
      },
      'P0128': {
        'title': 'என்ஜின் வெப்பநிலை குறைவாக உள்ளது (DTC P0128)',
        'what_we_found': 'என்ஜின் இயக்க வெப்பநிலையை எட்ட அதிக நேரம் எடுத்துக்கொள்கிறது.',
        'why_this_matters': 'குறைந்த வெப்பநிலையில் ஓட்டுவதால் மைலேஜ் குறையும் மற்றும் புகை அளவு அதிகரிக்கும்.',
        'what_you_should_do_now': 'தெர்மோஸ்டாட் மற்றும் வெப்பநிலை சென்சாரைச் சரிபார்க்கவும்.',
        'can_i_keep_driving': 'விரைவில் மெக்கானிக்கிடம் செல்லவும்.',
        'technical_details': 'SAE J2012 வரையறை: குறிப்பிட்ட நேரத்தில் கூலண்ட் வெப்பநிலை எட்டப்படவில்லை.',
        'mechanic_checks': [
          'தெர்மோஸ்டாட் செயல்பாடு',
          'சென்சார் மின்தடை அளவு',
          'கூலண்ட் அளவு'
        ],
      },
      'P0401': {
        'title': 'EGR வாயு மறுசுழற்சி ஓட்டம் போதுமானதாக இல்லை (DTC P0401)',
        'what_we_found': 'என்ஜினின் EGR அமைப்பில் புகை மறுசுழற்சி ஓட்டம் குறைவாக உள்ளது. அடைப்பு அல்லது வால்வு பிரச்சனை இருக்கலாம்.',
        'why_this_matters': 'இது என்ஜின் வெப்பநிலையைக் கட்டுப்படுத்தும்; ஓட்டம் குறைந்தால் சத்தம் மற்றும் மாசு அதிகரிக்கும்.',
        'what_you_should_do_now': 'பாகங்களை மாற்றுவதற்கு முன் கரியடைப்பை சரிபார்க்கவும்.',
        'can_i_keep_driving': 'விரைவில் மெக்கானிக்கிடம் செல்லவும்.',
        'technical_details': 'SAE J2012 வரையறை: EGR ஓட்டத்தின் அளவு அனுமதிக்கப்பட்ட அளவை விட குறைவு.',
        'mechanic_checks': [
          'EGR வால்வில் உள்ள கரியடைப்பு',
          'EGR பிரஷர் சென்சார்',
          'EGR குழாய் சுத்தம்'
        ],
      },
    },
    'te': {
      'P0300': {
        'title': 'ఇంజిన్ సిలిండర్ మిస్‌ఫైర్ మార్గదర్శకత్వం (DTC P0300)',
        'what_we_found': 'ఒకటి లేదా అంతకంటే ఎక్కువ సిలిండర్లలో ఇంధనం సరిగ్గా మండటం లేదని కంప్యూటర్ గుర్తించింది.',
        'why_this_matters': 'మండని ఇంధనం ఎగ్జాస్ట్‌లోకి ప్రవేశించి కన్వర్టర్‌ను పాడు చేస్తుంది మరియు ఇంజిన్ వణుకుతుంది.',
        'what_you_should_do_now': 'ఇంజిన్ లైట్ మెరుస్తుంటే వెంటనే సురక్షిత ప్రదేశంలో ఆపండి. నిపుణులతో తనిఖీ చేయించండి.',
        'can_i_keep_driving': 'అనవసరంగా డ్రైవ్ చేయకండి; త్వరగా రిపేర్ చేయించండి.',
        'technical_details': 'SAE J2012 ప్రకారం P0300 క్రాంక్‌షాఫ్ట్ అసమానతను సూచిస్తుంది.',
        'mechanic_checks': [
          'స్పార్క్ ప్లగ్‌లు & ఇగ్నిషన్ కాయిల్స్',
          'ఇంధన పీడనం & ఇంజెక్టర్లు',
          'గాలి లీకులు & వాక్యూమ్ లైన్లు',
          'సిలిండర్ కంప్రెషన్'
        ],
      },
      'P0128': {
        'title': 'ఇంజిన్ ఉష్ణోగ్రత తక్కువగా ఉంది (DTC P0128)',
        'what_we_found': 'ఇంజిన్ సాధారణ ఉష్ణోగ్రతకు చేరుకోవడానికి ఎక్కువ సమయం తీసుకుంటోంది.',
        'why_this_matters': 'తక్కువ ఉష్ణోగ్రత వల్ల మైలేజ్ తగ్గుతుంది మరియు కాలుష్యం పెరుగుతుంది.',
        'what_you_should_do_now': 'కూలింగ్ సిస్టమ్ థర్మోస్టాట్‌ను తనిఖీ చేయించండి.',
        'can_i_keep_driving': 'త్వరలో మెకానిక్‌ను సంప్రదించండి.',
        'technical_details': 'SAE J2012 ప్రకారం కూలెంట్ సరైన సమయంలో వేడెక్కలేదు.',
        'mechanic_checks': [
          'థర్మోస్టాట్ ఆపరేషన్',
          'కూలెంట్ ఉష్ణోగ్రత సెన్సార్',
          'కూలెంట్ స్థాయి'
        ],
      },
      'P0401': {
        'title': 'EGR వాయు ప్రవాహం సరిపోవడం లేదు (DTC P0401)',
        'what_we_found': 'ఎగ్జాస్ట్ గ్యాస్ రీసర్క్యులేషన్ సిస్టమ్‌లో ప్రవాహం తక్కువగా ఉంది.',
        'why_this_matters': 'ఇది ఇంజిన్ దహన ఉష్ణోగ్రతను నియంత్రిస్తుంది; తక్కువ ప్రవాహం వల్ల కాలుష్యం పెరుగుతుంది.',
        'what_you_should_do_now': 'EGR సిస్టమ్‌ను మెకానిక్‌తో తనిఖీ చేయించండి.',
        'can_i_keep_driving': 'త్వరలో మెకానిక్‌ను సంప్రదించండి.',
        'technical_details': 'SAE J2012 ప్రకారం EGR ప్రవాహం అవసరమైన స్థాయి కంటే తక్కువ.',
        'mechanic_checks': [
          'EGR వాల్వ్ కార్బన్ డిపాజిట్లు',
          'EGR ప్రెషర్ సెన్సార్',
          'ట్యూబ్ క్లీనింగ్'
        ],
      },
    },
  };

  // ---------------------------------------------------------------------------
  // 6b. Centralized Telemetry PID Multilingual Translations Map
  // ---------------------------------------------------------------------------
  static final Map<String, Map<String, Map<String, String>>> _pidTranslations = {
    'hi': {
      'FUEL_TRIM_SHORT': {
        'title': 'इंजन ईंधन समायोजन निगरानी सीमा से बाहर',
        'what_we_found': 'वाहन का इंजन कंप्यूटर दहन संतुलन बनाए रखने के लिए ईंधन की आपूर्ति में अपेक्षित से बड़ा बदलाव कर रहा है।',
        'value_meaning': 'पॉजिटिव फ्यूल ट्रिम का अर्थ है कि हवा अधिक होने पर अतिरिक्त ईंधन दिया जा रहा है। नेगेटिव ट्रिम का अर्थ है ईंधन कम किया जा रहा है।',
        'what_you_should_do': 'यदि इंजन असामान्य आवाज कर रहा है, पिकअप गिर गया है या माइलेज कम हो गई है, तो पेशेवर डायग्नोस्टिक जांच करवाएं।',
        'technical_details': 'शॉर्ट-टर्म फ्यूल ट्रिम (STFT) ऑक्सीजन सेंसर सिग्नल के आधार पर वास्तविक समय का सुधार दर्शाता है।',
        'range_source': 'SAE J1979 क्लोज्ड-लूप मानक के आधार पर कॉन्फ़िगर की गई सीमा [-15.0, 15.0] %।',
      },
      'FUEL_TRIM_SHORT_B2': {
        'title': 'इंजन ईंधन समायोजन (बैंक 2) निगरानी सीमा से बाहर',
        'what_we_found': 'सिलेंडर बैंक 2 में ईंधन समायोजन अपेक्षित निगरानी सीमा से बाहर दर्ज किया गया।',
        'value_meaning': 'बैंक 2 में हवा या ईंधन का असंतुलन बना हुआ है।',
        'what_you_should_do': 'बैंक 2 से जुड़े वैक्यूम पाइप और इंजेक्टरों की जांच करवाएं।',
        'technical_details': 'सिलेंडर बैंक 2 के लिए शॉर्ट-टर्म ईंधन समायोजन (STFT B2)।',
        'range_source': 'SAE J1979 बैंक 2 क्लोज्ड-लूप मानक सीमा [-15.0, 15.0] %।',
      },
      'FUEL_TRIM_LONG': {
        'title': 'लॉन्ग-टर्म इंजन ईंधन समायोजन सीमा से बाहर',
        'what_we_found': 'वाहन कंप्यूटर ने समय के साथ एक स्थायी ईंधन सुधार लागू किया है, जो निरंतर असंतुलन दर्शाता है।',
        'value_meaning': 'लॉन्ग-टर्म ट्रिम स्थायी रिसाव, ईंधन प्रवाह रुकावट या सेंसर अशुद्धि की ओर संकेत करता है।',
        'what_you_should_do': 'गैरेज में वैक्यूम लीक और फ्यूल पंप दबाव की व्यापक जांच करवाएं।',
        'technical_details': 'लॉन्ग-टर्म फ्यूल ट्रिम (LTFT) निरंतर ऑपरेटिंग विसंगतियों को संतुलित करने के लिए सीखा गया मान है।',
        'range_source': 'SAE J1979 मानक क्लोज्ड-लूप सीमा [-15.0, 15.0] %।',
      },
      'COOLANT_TEMP': {
        'title': 'इंजन कूलेंट तापमान सामान्य सीमा से बाहर',
        'what_we_found': 'इंजन कूलेंट तापमान रीडिंग एप्लिकेशन की कॉन्फ़िगर की गई सामान्य सीमा से बाहर दर्ज की गई।',
        'value_meaning': '105°C से अधिक तापमान ओवरहीटिंग का जोखिम दर्शाता है। वार्म-अप के बाद 75°C से कम तापमान थर्मोस्टेट खुला अटकने का संकेत देता है।',
        'what_you_should_do': 'यदि तापमान बहुत अधिक है, तो सुरक्षित स्थान पर रुकें। इंजन ठंडा होने पर ही कूलेंट स्तर और पंखे की जांच करें।',
        'technical_details': 'इंजन कूलेंट टेम्परेचर (ECT) सेंसर इंजन ऑपरेटिंग तापमान की सटीक निगरानी करता है।',
        'range_source': 'यात्री वाहनों की सामान्य ऑपरेटिंग सीमा [75.0, 105.0] °C।',
      },
      'ENGINE_RPM': {
        'title': 'इंजन गति (RPM) अपेक्षित सीमा से बाहर',
        'what_we_found': 'इंजन आरपीएम रीडिंग सामान्य ड्राइविंग एवं निष्क्रिय सीमा से बाहर दर्ज की गई।',
        'value_meaning': 'अत्यधिक उच्च RPM से इंजन पर दबाव बढ़ता है; अत्यधिक कम या अस्थिर RPM से इंजन बंद हो सकता है।',
        'what_you_should_do': 'आइडल एयर कंट्रोल, थ्रॉटल बॉडी और स्पार्क प्लग की जांच करवाएं।',
        'technical_details': 'क्रैंकशाफ्ट पोजिशन सेंसर (CKP) द्वारा प्रति मिनट घूर्णन गति (RPM) की निगरानी की जाती है।',
        'range_source': 'कॉन्फ़िगर की गई निगरानी सीमा [500, 6500] RPM।',
      },
      'VEHICLE_SPEED': {
        'title': 'वाहन गति सेंसर रीडिंग में विसंगति',
        'what_we_found': 'वाहन गति सेंसर रीडिंग सामान्य सीमा से बाहर या असंगत दर्ज की गई।',
        'value_meaning': 'पहिया गति या ट्रांसमिशन आउटपुट सेंसर में संभावित अंतर।',
        'what_you_should_do': 'एबीएस सेंसर और स्पीडोमीटर केबल/सेंसर की जांच करवाएं।',
        'technical_details': 'व्हीकल स्पीड सेंसर (VSS) ट्रांसमिशन या एबीएस मॉड्यूल से गति डेटा देता है।',
        'range_source': 'मानक सड़क गति निगरानी सीमा [0, 200] km/h।',
      },
      'INTAKE_PRESSURE': {
        'title': 'इंटेक मैनिफोल्ड दबाव सामान्य सीमा से बाहर',
        'what_we_found': 'इंजन मैनिफोल्ड निरपेक्ष दबाव (MAP) सामान्य सीमा से बाहर पाया गया।',
        'value_meaning': 'इंजन वैक्यूम में रिसाव, रुकावट या थ्रॉटल खराबी का संकेत हो सकता है।',
        'what_you_should_do': 'इंटेक होज़, गैसकेट और वैक्यूम लाइनों का निरीक्षण करवाएं।',
        'technical_details': 'मैनिफोल्ड एब्सोल्यूट प्रेशर (MAP) सेंसर इंजन लोड और वैक्यूम का आकलन करता है।',
        'range_source': 'मानक इनटेक मैनिफोल्ड प्रेशर सीमा [15, 105] kPa।',
      },
      'MAF': {
        'title': 'मास एयर फ्लो (MAF) सेंसर रीडिंग सीमा से बाहर',
        'what_we_found': 'इंजन में प्रवेश करने वाली हवा की मात्रा सामान्य सीमा से विचलित पाई गई।',
        'value_meaning': 'गंदा सेंसर या इंटेक में अनधिकृत हवा का प्रवेश इसका कारण हो सकता है।',
        'what_you_should_do': 'विशेष क्लीनर से एमएएफ सेंसर साफ करवाएं और एयर फिल्टर बदलें।',
        'technical_details': 'मास एयर फ्लो (MAF) सेंसर आने वाली वायु के द्रव्यमान को मापता है।',
        'range_source': 'मानक एयरफ्लो निगरानी सीमा [1.0, 250.0] g/s।',
      },
    },
    'ta': {
      'FUEL_TRIM_SHORT': {
        'title': 'என்ஜின் எரிபொருள் சரிசெய்தல் வரம்பிற்கு வெளியே உள்ளது',
        'what_we_found': 'என்ஜின் எரிபொருள் அளவை சரிசெய்ய கணினி பெரிய மாற்றங்களைச் செய்து வருகிறது.',
        'value_meaning': 'நேர்மறை (+) ட்ரிம் என்பது காற்று அதிகமாக இருப்பதால் கூடுதல் எரிபொருள் சேர்க்கப்படுவதைக் குறிக்கிறது. எதிர்மறை (-) ட்ரிம் என்பது எரிபொருள் குறைக்கப்படுவதைக் குறிக்கிறது.',
        'what_you_should_do': 'என்ஜின் அதிர்வு இருந்தால் அல்லது மைலேஜ் குறைந்தால் முழுமையான கணினி பரிசோதனை செய்யுங்கள்.',
        'technical_details': 'குறுகிய கால எரிபொருள் ட்ரிம் (STFT) ஆக்சிஜன் சென்சார் தகவல்களின் அடிப்படையில் செயல்படுகிறது.',
        'range_source': 'SAE J1979 நிலையான கண்காணிப்பு வரம்பு [-15.0, 15.0] %.',
      },
      'COOLANT_TEMP': {
        'title': 'என்ஜின் குளிரூட்டி வெப்பநிலை வழக்கத்திற்கு மாறானது',
        'what_we_found': 'என்ஜின் கூலண்ட் வெப்பநிலை நிர்ணயிக்கப்பட்ட சாதாரண வரம்பிற்கு வெளியே உள்ளது.',
        'value_meaning': '105°C-க்கு மேல் இருப்பது அதிக வெப்பம் (overheating) அபாயத்தைக் குறிக்கும். 75°C-க்கு கீழ் இருப்பது என்ஜின் சரியாக சூடாகவில்லை என்பதைக் குறிக்கும்.',
        'what_you_should_do': 'வெப்பநிலை அதிகமாக இருந்தால் பாதுகாப்பாக வாகனத்தை நிறுத்தி குளிரூட்டி அளவை சரிபார்க்கவும்.',
        'technical_details': 'என்ஜின் குளிரூட்டி வெப்பநிலை (ECT) சென்சார் என்ஜின் சூட்டை கண்காணிக்கிறது.',
        'range_source': 'வழக்கமான பயணிகள் வாகன வரம்பு [75.0, 105.0] °C.',
      },
      'ENGINE_RPM': {
        'title': 'என்ஜின் வேகம் (RPM) வரம்பிற்கு வெளியே உள்ளது',
        'what_we_found': 'என்ஜின் சுழற்சி வேகம் எதிர்பார்க்கப்படும் நிலையை விட மாறுபட்டுள்ளது.',
        'value_meaning': 'அதிகப்படியான RPM என்ஜினை சேதப்படுத்தும்; மிகக் குறைந்த RPM வண்டியை அணைக்கக்கூடும்.',
        'what_you_should_do': 'த்ராட்டில் பாடி மற்றும் ஸ்பார்க் பிளக்குகளை சரிபார்க்கவும்.',
        'technical_details': 'கிரான்க்ஷாஃப்ட் சென்சார் என்ஜின் சுழற்சியை நிமிடத்திற்கு (RPM) அளவிடுகிறது.',
        'range_source': 'கண்காணிப்பு வரம்பு [500, 6500] RPM.',
      },
      'MAF': {
        'title': 'காற்று ஓட்ட சென்சார் (MAF) வரம்பிற்கு வெளியே உள்ளது',
        'what_we_found': 'என்ஜினுக்குள் செல்லும் காற்றின் அளவு நிர்ணயிக்கப்பட்ட வரம்பை விட வேறுபடுகிறது.',
        'value_meaning': 'அழுக்கான சென்சார் அல்லது குழாய் கசிவு காரணமாக இருக்கலாம்.',
        'what_you_should_do': 'சென்சாரைச் சுத்தம் செய்து ஏர் ஃபில்டரை மாற்றவும்.',
        'technical_details': 'Mass Air Flow (MAF) சென்சார் காற்று எடையை அளவிடுகிறது.',
        'range_source': 'தரநிலைக் கண்காணிப்பு வரம்பு [1.0, 250.0] g/s.',
      },
    },
    'te': {
      'FUEL_TRIM_SHORT': {
        'title': 'ఇంజిన్ ఇంధన సర్దుబాటు పర్యవేక్షణ పరిధి వెలుపల ఉంది',
        'what_we_found': 'ఇంజిన్ దహన ప్రక్రియను స్థిరీకరించడానికి కంప్యూటర్ ఊహించిన దానికంటే పెద్ద సర్దుబాట్లను చేస్తోంది.',
        'value_meaning': 'పాజిటివ్ ట్రిమ్ (+) అంటే అదనపు గాలి వల్ల ఎక్కువ ఇంధనం ఇవ్వబడుతోంది. నెగటివ్ ట్రిమ్ (-) అంటే ఇంధనం తగ్గించబడుతోంది.',
        'what_you_should_do': 'వాహనం అసాధారణంగా నడుస్తున్నా లేదా మైలేజీ తగ్గినా డయాగ్నస్టిక్ తనిఖీని ఏర్పాటు చేయండి.',
        'technical_details': 'షార్ట్-టర్మ్ ఫ్యూయల్ ట్రిమ్ (STFT) ఆక్సిజన్ సెన్సార్ ఫీడ్‌బ్యాక్ ఆధారంగా పనిచేస్తుంది.',
        'range_source': 'SAE J1979 పర్యవేక్షణ పరిధి [-15.0, 15.0] %.',
      },
      'COOLANT_TEMP': {
        'title': 'ఇంజిన్ కూలెంట్ ఉష్ణోగ్రత సాధారణ పరిధి వెలుపల ఉంది',
        'what_we_found': 'ఇంజిన్ కూలెంట్ ఉష్ణోగ్రత రీడింగ్ సాధారణ పరిధికి వెలుపల నమోదైంది.',
        'value_meaning': '105°C కంటే ఎక్కువైతే ఓవర్‌హీటింగ్ ప్రమాదం. 75°C కంటే తక్కువైతే ఇంజిన్ సరిగ్గా వేడెక్కలేదని అర్థం.',
        'what_you_should_do': 'ఉష్ణోగ్రత ఎక్కువగా ఉంటే సురక్షితంగా ఆపి కూలెంట్ స్థాయిని తనిఖీ చేయండి.',
        'technical_details': 'ఇంజిన్ కూలెంట్ టెంపరేచర్ (ECT) సెన్సార్ ఉష్ణోగ్రతను పర్యవేక్షిస్తుంది.',
        'range_source': 'సాధారణ ప్యాసింజర్ వాహన పరిధి [75.0, 105.0] °C.',
      },
      'ENGINE_RPM': {
        'title': 'ఇంజిన్ వేగం (RPM) సాధారణ పరిధి వెలుపల ఉంది',
        'what_we_found': 'ఇంజిన్ భ్రమణ వేగం పర్యవేక్షణ సరిహద్దుల వెలుపల నమోదైంది.',
        'value_meaning': 'అధిక RPM వల్ల ఇంజిన్ ఒత్తిడి పెరుగుతుంది; తక్కువ RPM వల్ల వాహనం ఆగిపోవచ్చు.',
        'what_you_should_do': 'థ్రోటల్ బాడీ మరియు స్పార్క్ ప్లగ్‌లను పరిశీలించండి.',
        'technical_details': 'క్రాంక్‌షాఫ్ట్ సెన్సార్ నిమిషానికి ఇంజిన్ భ్రమణాలను లెక్కిస్తుంది.',
        'range_source': 'పర్యవేక్షణ పరిధి [500, 6500] RPM.',
      },
    },
    'kn': {
      'FUEL_TRIM_SHORT': {
        'title': 'ಎಂಜಿನ್ ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಮೇಲ್ವಿಚಾರಣಾ ವ್ಯಾಪ್ತಿಯ ಹೊರಗಿದೆ',
        'what_we_found': 'ಸರಿಯಾದ ದಹನವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಲು ವಾಹನದ ಕಂಪ್ಯೂಟರ್ ಇಂಧನದ ಪ್ರಮಾಣದಲ್ಲಿ ನಿರೀಕ್ಷೆಗಿಂತ ದೊಡ್ಡ ಹೊಂದಾಣಿಕೆಗಳನ್ನು ಮಾಡುತ್ತಿದೆ.',
        'value_meaning': 'ಧನಾತ್ಮಕ ಟ್ರಿಮ್ (+) ಎಂದರೆ ಹೆಚ್ಚುವರಿ ಗಾಳಿ ಇರುವುದರಿಂದ ಹೆಚ್ಚು ಇಂಧನ ನೀಡಲಾಗುತ್ತಿದೆ. ಋಣಾತ್ಮಕ ಟ್ರಿಮ್ (-) ಎಂದರೆ ಇಂಧನ ಕಡಿಮೆ ಮಾಡಲಾಗುತ್ತಿದೆ.',
        'what_you_should_do': 'ವಾಹನದಲ್ಲಿ ನಡುಕ ಅಥವಾ ಮೈಲೇಜ್ ಕುಸಿತ ಕಂಡುಬಂದರೆ ಗ್ಯಾರೇಜ್‌ನಲ್ಲಿ ತಪಾಸಣೆ ನಡೆಸಿ.',
        'technical_details': 'ಶಾರ್ಟ್-ಟರ್ಮ್ ಇಂಧನ ಟ್ರಿಮ್ (STFT) ತಕ್ಷಣದ ಆಕ್ಸಿಜನ್ ಸಂವೇದಕ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ಪ್ರತಿನಿಧಿಸುತ್ತದೆ.',
        'range_source': 'SAE J1979 ಮಾನಿಟರಿಂಗ್ ಶ್ರೇಣಿ [-15.0, 15.0] %.',
      },
      'COOLANT_TEMP': {
        'title': 'ಎಂಜಿನ್ ಕೂಲೆಂಟ್ ತಾಪಮಾನ ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯ ಹೊರಗಿದೆ',
        'what_we_found': 'ಎಂಜಿನ್ ಕೂಲೆಂಟ್ ತಾಪಮಾನವು ನಿಗದಿತ ಸುರಕ್ಷಿತ ಮಿತಿಗಿಂತ ಹೊರಗಿದೆ.',
        'value_meaning': '105°C ಕ್ಕಿಂತ ಹೆಚ್ಚು ತಾಪಮಾನವು ಅತಿಯಾದ ಬಿಸಿಯಾಗುವ ಅಪಾಯವನ್ನು ಸೂಚಿಸುತ್ತದೆ.',
        'what_you_should_do': 'ತಾಪಮಾನ ಹೆಚ್ಚಿದ್ದರೆ ತಕ್ಷಣ ವಾಹನವನ್ನು ನಿಲ್ಲಿಸಿ ಕೂಲೆಂಟ್ ಮಟ್ಟವನ್ನು ಪರೀಕ್ಷಿಸಿ.',
        'technical_details': 'ಕೂಲೆಂಟ್ ತಾಪಮಾನ ಸಂವೇದಕವು (ECT) ಎಂಜಿನ್ ಶಾಖವನ್ನು ಅಳೆಯುತ್ತದೆ.',
        'range_source': 'ಸಾಮಾನ್ಯ ಆಪರೇಟಿಂಗ್ ಶ್ರೇಣಿ [75.0, 105.0] °C.',
      },
    },
    'bn': {
      'FUEL_TRIM_SHORT': {
        'title': 'ইঞ্জিন ফুয়েল সমন্বয় পর্যবেক্ষণ সীমার বাইরে',
        'what_we_found': 'ইঞ্জিনের সঠিক দহন বজায় রাখতে কম্পিউটার প্রত্যাশার চেয়ে বেশি জ্বালানি সামঞ্জস্য করছে।',
        'value_meaning': 'পজিটিভ ফুয়েল ট্রিম মানে অতিরিক্ত বাতাসের জন্য বেশি জ্বালানি যোগ হচ্ছে। নেগেটিভ ট্রিম মানে জ্বালানি কমানো হচ্ছে।',
        'what_you_should_do': 'ইঞ্জিনে কম্পন থাকলে বা মাইলেজ কমে গেলে দ্রুত মেকানিক দিয়ে পরীক্ষা করান।',
        'technical_details': 'শর্ট-টার্ম ফুয়েল ট্রিম (STFT) তাৎক্ষণিক অক্সিজেন সেন্সর ফিডব্যাক নির্দেশ করে।',
        'range_source': 'SAE J1979 স্ট্যান্ডার্ড পর্যবেক্ষণ পরিসীমা [-15.0, 15.0] %।',
      },
      'COOLANT_TEMP': {
        'title': 'ইঞ্জিন কুল্যান্ট তাপমাত্রা স্বাভাবিক সীমার বাইরে',
        'what_we_found': 'ইঞ্জিন কুল্যান্ট তাপমাত্রা পর্যবেক্ষণ সীমার বাইরে রেকর্ড করা হয়েছে।',
        'value_meaning': '১০৫°C-এর বেশি তাপমাত্রা ইঞ্জিন অতিরিক্ত গরম হওয়ার ঝুঁকি নির্দেশ করে।',
        'what_you_should_do': 'তাপমাত্রা বেশি হলে নিরাপদ স্থানে থামুন এবং কুল্যান্ট পরীক্ষা করুন।',
        'technical_details': 'ইঞ্জিন কুল্যান্ট টেম্পারেচার (ECT) সেন্সর ইঞ্জিনের তাপমাত্রা ট্র্যাক করে।',
        'range_source': 'স্বাভাবিক অপারেটিং সীমা [75.0, 105.0] °C।',
      },
    },
    'mr': {
      'FUEL_TRIM_SHORT': {
        'title': 'इंजिन इंधन समायोजन मर्यादा ओलांडली',
        'what_we_found': 'इंजिन योग्य ज्वलन राखण्यासाठी आवश्यकतेपेक्षा जास्त इंधन बदल करत आहे.',
        'value_meaning': 'पॉझिटिव्ह ट्रिम म्हणजे जादा हवेमुळे इंधन वाढवले जात आहे. निगेटिव्ह ट्रिम म्हणजे इंधन कमी केले जात आहे.',
        'what_you_should_do': 'इंजिनमध्ये कंपन असल्यास किंवा मायलेज कमी झाल्यास गॅरेजमध्ये तपासणी करा.',
        'technical_details': 'शॉर्ट-टर्म फ्युएल ट्रिम (STFT) ऑक्सिजन सेन्सरवर आधारित रीअल-टाइम बदल दर्शवते.',
        'range_source': 'SAE J1979 निरीक्षण श्रेणी [-15.0, 15.0] %.',
      },
      'COOLANT_TEMP': {
        'title': 'इंजिन कूलंट तापमान सामान्य मर्यादेबाहेर',
        'what_we_found': 'कूलंट तापमान कॉन्फिगर केलेल्या मर्यादेबाहेर नोंदवले गेले.',
        'value_meaning': '१०५°C पेक्षा जास्त तापमान ओव्हरहाटिंगचा धोका दर्शवते.',
        'what_you_should_do': 'तापमान जास्त असल्यास सुरक्षितपणे थांबा आणि कूलंट पातळी तपासा.',
        'technical_details': 'इंजिन कूलंट तापमान (ECT) सेन्सर इंजिन उष्णतेचे निरीक्षण करतो.',
        'range_source': 'सामान्य कार्य श्रेणी [75.0, 105.0] °C.',
      },
    },
    'gu': {
      'FUEL_TRIM_SHORT': {
        'title': 'એન્જિન ઇંધણ ગોઠવણ સામાન્ય શ્રેણી બહાર છે',
        'what_we_found': 'યોગ્ય દહન જાળવવા માટે એન્જિન કમ્પ્યુટર ઇંધણ પુરવઠામાં અપેક્ષિત કરતાં મોટો ફેરફાર કરી રહ્યું છે.',
        'value_meaning': 'પોઝિટિવ ટ્રિમ એટલે હવા વધુ હોવાથી વધારે ઇંધણ ઉમેરાય છે. નેગેટિવ ટ્રિમ એટલે ઇંધણ ઘટાડાય છે.',
        'what_you_should_do': 'જો એન્જિનમાં ધ્રુજારી હોય અથવા એવરેજ ઘટી હોય તો ગેરેજમાં તપાસ કરાવો.',
        'technical_details': 'શોર્ટ-ટર્મ ફ્યુઅલ ટ્રીમ (STFT) તાત્કાલિક ઓક્સિજન સેન્સર ફીડબેક દર્શાવે છે.',
        'range_source': 'SAE J1979 મોનિટરિંગ શ્રેણી [-15.0, 15.0] %.',
      },
      'COOLANT_TEMP': {
        'title': 'એન્જિન કુલન્ટ તાપમાન સામાન્ય મર્યાદા બહાર',
        'what_we_found': 'કુલન્ટ તાપમાન રીડિંગ સામાન્ય શ્રેણી બહાર નોંધાયું.',
        'value_meaning': '૧૦૫°C થી વધુ તાપમાન ઓવરહિટીંગનું જોખમ દર્શાવે છે.',
        'what_you_should_do': 'તાપમાન વધારે હોય તો સલામત સ્થળે કાર રોકીને કુલન્ટ ચેક કરો.',
        'technical_details': 'એન્જિન કુલન્ટ ટેમ્પરેચર (ECT) સેન્સર ઓપરેટિંગ તાપમાન માપે છે.',
        'range_source': 'સામાન્ય ઓપરેટિંગ શ્રેણી [75.0, 105.0] °C.',
      },
    },
  };

  // ---------------------------------------------------------------------------
  // 7. Public Translation Methods for Dynamic Report Data
  // ---------------------------------------------------------------------------

  static String getDtcTitle(String code, String fallback, String langCode) {
    final lang = _norm(langCode);
    final match = _dtcTranslations[lang]?[code.toUpperCase()];
    if (match != null && match['title'] != null) {
      return match['title'] as String;
    }
    return fallback;
  }

  static String getDtcWhatItMeans(String code, String fallback, String langCode) {
    final lang = _norm(langCode);
    final match = _dtcTranslations[lang]?[code.toUpperCase()];
    if (match != null && match['what_it_means'] != null) {
      return match['what_it_means'] as String;
    }
    return fallback;
  }

  static String getDtcWhatYouShouldDo(String code, String fallback, String langCode) {
    final lang = _norm(langCode);
    final match = _dtcTranslations[lang]?[code.toUpperCase()];
    if (match != null && match['what_you_should_do'] != null) {
      return match['what_you_should_do'] as String;
    }
    return fallback;
  }

  static String getDtcNotice(String symptom, String langCode) {
    final lang = _norm(langCode);
    final s = symptom.toLowerCase();
    if (lang == 'hi') {
      if (s.contains('misfire') || s.contains('rough idle') || s.contains('idling')) return 'इंजन मिसफायर, वाहन का कांपना या झटके लेना';
      if (s.contains('check engine') || s.contains('mil') || s.contains('illuminated') || s.contains('flashing')) return 'चेक इंजन लाइट का जलना या चमकना';
      if (s.contains('hesitation') || s.contains('acceleration') || s.contains('stumble')) return 'त्वरण (acceleration) के समय पिकअप में रुकावट';
      if (s.contains('reduced fuel') || s.contains('mileage') || s.contains('economy')) return 'माइलेज में भारी गिरावट या अधिक ईंधन खपत';
      if (s.contains('cooler') || s.contains('cold') || s.contains('temperature')) return 'इंजन का सामान्य से अधिक ठंडा चलना';
      if (s.contains('cabin heat') || s.contains('heater')) return 'केबिन हीटर से पर्याप्त गर्म हवा न मिलना';
      if (s.contains('pinging') || s.contains('knocking') || s.contains('knock')) return 'लोड पड़ने पर इंजन में खटखटाहट की आवाज (pinging)';
      if (s.contains('odor') || s.contains('smell') || s.contains('fuel smell')) return 'वाहन या एग्जॉस्ट के पास पेट्रोल/डीजल की तेज गंध';
      if (s.contains('sluggish') || s.contains('loss of power') || s.contains('power')) return 'गाड़ी की सुस्त चाल और इंजन की शक्ति में कमी';
      if (s.contains('rotten egg') || s.contains('sulfur')) return 'साइलेंसर से सड़े अंडे या सल्फर जैसी गंध';
      if (s.contains('transmission') || s.contains('shifting') || s.contains('slip')) return 'गियर बदलने में झटका या गियर स्लिप होना';
    } else if (lang == 'ta') {
      if (s.contains('misfire') || s.contains('idling')) return 'என்ஜின் மிஸ்பயர் அல்லது வண்டி அதிர்தல்';
      if (s.contains('check engine') || s.contains('mil')) return 'என்ஜின் எச்சரிக்கை விளக்கு எரிதல்';
      if (s.contains('reduced fuel') || s.contains('mileage')) return 'மைலேஜ் குறைதல் அல்லது அதிக எரிபொருள் செலவு';
      if (s.contains('acceleration')) return 'வேகமெடுக்கும் போது இழுத்தல் அல்லது தாமதம்';
      if (s.contains('sluggish') || s.contains('power')) return 'என்ஜின் இழுவை சக்தி குறைதல்';
      if (s.contains('smell') || s.contains('odor')) return 'எரிபொருள் அல்லது புகை வாசனை';
    } else if (lang == 'te') {
      if (s.contains('misfire') || s.contains('idling')) return 'ఇంజిన్ మిస్‌ఫైర్ లేదా ఇంజిన్ వణుకు';
      if (s.contains('check engine') || s.contains('mil')) return 'చెక్ ఇంజిన్ లైట్ వెలగడం';
      if (s.contains('reduced fuel') || s.contains('mileage')) return 'మైలేజ్ తగ్గడం లేదా ఇంధన వినియోగం పెరగడం';
      if (s.contains('acceleration')) return 'వేగం పెంచేటప్పుడు తడబాటు';
      if (s.contains('sluggish') || s.contains('power')) return 'ఇంజిన్ శక్తి తగ్గడం';
    } else if (lang == 'kn') {
      if (s.contains('misfire') || s.contains('idling')) return 'ಎಂಜಿನ್ ಮಿಸ್‌ಫೈರ್ ಅಥವಾ ನಡುಕ';
      if (s.contains('check engine')) return 'ಚೆಕ್ ಎಂಜಿನ್ ಲೈಟ್ ಉರಿಯುವುದು';
      if (s.contains('mileage')) return 'ಮೈಲೇಜ್ ಇಳಿಕೆ';
    } else if (lang == 'bn') {
      if (s.contains('misfire') || s.contains('idling')) return 'ইঞ্জিন মিসফায়ার বা অতিরিক্ত কম্পন';
      if (s.contains('check engine')) return 'চেক ইঞ্জিন লাইট জ্বলা';
      if (s.contains('mileage')) return 'মাইলেজ কমে যাওয়া';
    }
    return symptom;
  }

  static String getDtcWhyItMatters(String code, String fallback, String langCode) {
    final lang = _norm(langCode);
    final c = code.toUpperCase();
    if (lang == 'hi') {
      if (c == 'P0300') return 'अनियमित मिसफायर से बिना जला ईंधन एग्जॉस्ट में जाता है, जिससे प्रदूषण बढ़ता है और महंगा कैटेलिटिक कन्वर्टर अत्यधिक गर्म होकर पिघल सकता है।';
      if (c == 'P0128') return 'कम तापमान पर लगातार चलने से इंजन में कार्बन जमाव बढ़ता है, ईंधन की अत्यधिक खपत होती है और केबिन में हीटर ठीक से काम नहीं करता।';
      if (c == 'P0401') return 'ईजीआर प्रवाह रुकने से दहन तापमान अत्यधिक बढ़ जाता है, जिससे इंजन खटखटाता है और नाइट्रोजन ऑक्साइड उत्सर्जन बढ़ता है।';
      if (c == 'P0171') return 'अत्यधिक लीन मिश्रण से इंजन के पुर्जे अत्यधिक गर्म हो सकते हैं, वाल्व जल सकते हैं और त्वरण के समय गाड़ी झटके ले सकती है।';
      if (c == 'P0420') return 'कैटेलिटिक कन्वर्टर की कम दक्षता के कारण हानिकारक उत्सर्जन वातावरण में फैलते हैं और वाहन प्रदूषण मानकों में विफल हो सकता है।';
      if (c == 'P0217') return 'इंजन ओवरहीटिंग से हेड गैसकेट फट सकता है, सिलेंडर हेड मुड़ सकता है और इंजन पूरी तरह सीज हो सकता है।';
      if (c == 'P0133') return 'धीमी प्रतिक्रिया वाला ऑक्सीजन सेंसर ईसीएम को गलत डेटा भेजता है, जिससे ईंधन मिश्रण बिगड़ता है।';
      if (c == 'P0455') return 'ईंधन वाष्प का वातावरण में रिसाव होने से ईंधन की बर्बादी होती है और आग का खतरा बन सकता है।';
      if (c == 'P0700') return 'ट्रांसमिशन कंप्यूटर की खराबी से गियर लॉक हो सकते हैं और ट्रांसमिशन क्लच जल सकता है।';
    } else if (lang == 'ta') {
      if (c == 'P0300') return 'தொடர் மிஸ்பயரினால் எரியாத எரிபொருள் சைலன்சரில் சென்று புகை சுத்திகரிப்பானை (catalytic converter) அழித்துவிடும்.';
      if (c == 'P0128') return 'என்ஜின் குளிராக இயங்குவதால் அதிக எரிபொருள் செலவாகும் மற்றும் என்ஜின் ஆயுள் குறையும்.';
      if (c == 'P0401') return 'EGR குறைபாட்டினால் என்ஜின் அதிக வெப்பமடைந்து சத்தம் அதிகரிக்கும்.';
      if (c == 'P0171') return 'எரிபொருள் கலவை குறைவினால் என்ஜின் சூடாகி செயல்திறன் குறையும்.';
    } else if (lang == 'te') {
      if (c == 'P0300') return 'మండని ఇంధనం ఎగ్జాస్ట్‌లోకి ప్రవేశించి కెటలిటిక్ కన్వర్టర్‌ను పాడు చేస్తుంది మరియు ఇంజిన్ దెబ్బతింటుంది.';
      if (c == 'P0128') return 'తక్కువ ఉష్ణోగ్రత వద్ద నడవడం వల్ల మైలేజ్ తగ్గి కాలుష్యం పెరుగుతుంది.';
      if (c == 'P0401') return 'EGR ప్రవాహం తగ్గడం వల్ల ఇంజిన్ వేడెక్కి శబ్దం చేస్తుంది.';
    }
    return fallback;
  }

  static String getDtcCause(String cause, String langCode) {
    final lang = _norm(langCode);
    final c = cause.toLowerCase();
    if (lang == 'hi') {
      if (c.contains('spark plug') || c.contains('ignition coil')) return 'खराब या घिसे हुए स्पार्क प्लग अथवा इग्निशन कॉइल';
      if (c.contains('vacuum leak') || c.contains('vacuum hose')) return 'इंटेक मैनिफोल्ड वैक्यूम लीक या कटी-फटी वैक्यूम पाइपें';
      if (c.contains('maf') || c.contains('mass air')) return 'दूषित या खराब मास एयर फ्लो (MAF) सेंसर';
      if (c.contains('injector')) return 'जाम, लीक या अवरुद्ध फ्यूल इंजेक्टर';
      if (c.contains('fuel pump') || c.contains('fuel pressure')) return 'कमजोर फ्यूल पंप, कम ईंधन दबाव या चोक फ्यूल फिल्टर';
      if (c.contains('thermostat')) return 'थर्मोस्टेट का खुला या बंद अटक जाना';
      if (c.contains('coolant temperature') || c.contains('ect sensor')) return 'खराब इंजन कूलेंट टेम्परेचर (ECT) सेंसर';
      if (c.contains('egr valve') || c.contains('carbon buildup')) return 'ईजीआर वाल्व अथवा पाइपों में अत्यधिक कार्बन जमाव';
      if (c.contains('catalytic converter')) return 'क्षतिग्रस्त या आंतरिक रूप से टूटा हुआ कैटेलिटिक कन्वर्टर';
      if (c.contains('oxygen sensor') || c.contains('o2 sensor')) return 'खराब या अशुद्ध रीडिंग देने वाला ऑक्सीजन सेंसर';
      if (c.contains('fuel cap') || c.contains('gas cap')) return 'ढीली, कटी या गायब फ्यूल टैंक कैप';
      if (c.contains('purge valve') || c.contains('evap')) return 'ईवीएपी (EVAP) कैनिस्टर पर्ज वाल्व का खुला अटकना';
      if (c.contains('transmission fluid')) return 'ट्रांसमिशन ऑयल का कम स्तर अथवा दूषित ऑयल';
    } else if (lang == 'ta') {
      if (c.contains('spark plug') || c.contains('ignition coil')) return 'ஸ்பார்க் பிளக் அல்லது காயில் பழுது';
      if (c.contains('vacuum leak')) return 'காற்று குழாய் கசிவுகள்';
      if (c.contains('injector')) return 'எரிபொருள் இன்ஜெக்டர் அடைப்பு';
      if (c.contains('thermostat')) return 'தெர்மோஸ்டாட் கோளாறு';
      if (c.contains('egr')) return 'EGR வால்வில் கரியடைப்பு';
    } else if (lang == 'te') {
      if (c.contains('spark plug') || c.contains('ignition coil')) return 'స్పార్క్ ప్లగ్ లేదా కాయిల్ లోపం';
      if (c.contains('vacuum leak')) return 'వాక్యూమ్ లీకులు';
      if (c.contains('injector')) return 'ఇంధన ఇంజెక్టర్ల సమస్య';
      if (c.contains('thermostat')) return 'థర్మోస్టాట్ సమస్య';
    }
    return cause;
  }

  static String getDtcLimitation(String limitation, String langCode) {
    final lang = _norm(langCode);
    final l = limitation.toLowerCase();
    if (lang == 'hi') {
      if (l.contains('alone does not prove') || l.contains('specific failed part') || l.contains('physical testing')) {
        return 'यह डीटीसी कोड केवल सर्किट या सबसिस्टम की असामान्य स्थिति दर्शाता है, किसी निश्चित पुर्जे की खराबी नहीं। पुर्जे बदलने से पहले पेशेवर मैकेनिक द्वारा भौतिक जांच आवश्यक है।';
      }
    } else if (lang == 'ta') {
      return 'இந்தக் குறியீடு கணினியின் நிலையை மட்டுமே குறிக்கிறது. உதிரிபாகங்களை மாற்றுவதற்கு முன் நேரடி மெக்கானிக் ஆய்வு அவசியம்.';
    } else if (lang == 'te') {
      return 'ఈ కోడ్ నిర్దిష్ట భాగం వైఫల్యాన్ని నిరూపించదు. భాగాలను మార్చడానికి ముందు భౌతిక పరీక్ష అవసరం.';
    }
    return limitation;
  }

  static String getDtcDescription(String code, String fallback, String langCode) {
    final lang = _norm(langCode);
    final c = code.toUpperCase();
    if (lang == 'hi') {
      if (c == 'P0300') return 'अनियमित / एकाधिक सिलेंडर मिसफायर का पता चला';
      if (c == 'P0128') return 'कूलेंट तापमान थर्मोस्टेट विनियमन सीमा से नीचे';
      if (c == 'P0401') return 'एग्जॉस्ट गैस रीसर्कुलेशन (EGR) प्रवाह अपर्याप्त';
      if (c == 'P0171') return 'सिस्टम में अत्यधिक लीन मिश्रण (बैंक 1)';
      if (c == 'P0420') return 'कैटेलिटिक कन्वर्टर प्रणाली दक्षता सीमा से कम (बैंक 1)';
      if (c == 'P0217') return 'इंजन कूलेंट अत्यधिक गर्म होने की स्थिति';
      if (c == 'P0133') return 'ऑक्सीजन सेंसर सर्किट धीमी प्रतिक्रिया (बैंक 1, सेंसर 1)';
      if (c == 'P0455') return 'ईवीएपी (EVAP) नियंत्रण प्रणाली में बड़ा वाष्प रिसाव';
      if (c == 'P0700') return 'ट्रांसमिशन नियंत्रण प्रणाली खराबी अनुरोध';
    } else if (lang == 'ta') {
      if (c == 'P0300') return 'பல சிலிண்டர் மிஸ்பயர் கண்டறியப்பட்டது';
      if (c == 'P0128') return 'என்ஜின் வெப்பநிலை போதுமானதாக இல்லை';
      if (c == 'P0401') return 'EGR வாயு மறுசுழற்சி ஓட்டம் குறைவு';
      if (c == 'P0171') return 'எரிபொருள் கலவை மிகவும் குறைவு';
    } else if (lang == 'te') {
      if (c == 'P0300') return 'సిలిండర్ మిస్‌ఫైర్ గుర్తించబడింది';
      if (c == 'P0128') return 'ఇంజిన్ ఉష్ణోగ్రత తక్కువగా ఉంది';
      if (c == 'P0401') return 'EGR ప్రవాహం సరిపోవడం లేదు';
    }
    return fallback;
  }

  // ---------------------------------------------------------------------------
  // 8. PID Multilingual Public Helper Methods
  // ---------------------------------------------------------------------------

  static String getPidTitle(String pidName, String fallback, String langCode) {
    final lang = _norm(langCode);
    final key = pidName.toUpperCase().trim();
    final match = _pidTranslations[lang]?[key];
    if (match != null && match['title'] != null) {
      return match['title']!;
    }
    // Fallback translation for common variations
    if (key.contains('FUEL_TRIM')) {
      switch (lang) {
        case 'hi': return 'इंजन ईंधन समायोजन निगरानी सीमा से बाहर';
        case 'ta': return 'என்ஜின் எரிபொருள் சரிசெய்தல் வரம்பிற்கு வெளியே';
        case 'te': return 'ఇంజిన్ ఇంధన సర్దుబాటు పర్యవేక్షణ పరిధి వెలుపల';
        case 'kn': return 'ಇಂಧನ ಹೊಂದಾಣಿಕೆ ಮಿತಿಮೀರಿದೆ';
        case 'bn': return 'ফুয়েল সমন্বয় সীমার বাইরে';
        case 'mr': return 'इंधन समायोजन मर्यादेबाहेर';
        case 'gu': return 'ઇંધણ ગોઠવણ સામાન્ય શ્રેણી બહાર';
      }
    }
    if (key.contains('COOLANT')) {
      switch (lang) {
        case 'hi': return 'इंजन कूलेंट तापमान सामान्य सीमा से बाहर';
        case 'ta': return 'என்ஜின் கூலண்ட் வெப்பநிலை வழக்கத்திற்கு மாறானது';
        case 'te': return 'ఇంజిన్ కూలెంట్ ఉష్ణోగ్రత సాధారణ పరిధి వెలుపల';
      }
    }
    if (key.contains('RPM')) {
      switch (lang) {
        case 'hi': return 'इंजन गति (RPM) अपेक्षित सीमा से बाहर';
        case 'ta': return 'என்ஜின் வேகம் (RPM) வரம்பிற்கு வெளியே';
        case 'te': return 'ఇంజిన్ వేగం (RPM) సాధారణ పరిధి వెలుపల';
      }
    }
    return fallback;
  }

  static String getPidWhatWeFound(String pidName, String fallback, String langCode) {
    final lang = _norm(langCode);
    final key = pidName.toUpperCase().trim();
    final match = _pidTranslations[lang]?[key];
    if (match != null && match['what_we_found'] != null) {
      return match['what_we_found']!;
    }
    final lower = fallback.toLowerCase();
    if (lower.contains('fuel supplied') || lower.contains('fuel adjustment') || key.contains('FUEL_TRIM')) {
      switch (lang) {
        case 'hi': return 'वाहन का इंजन कंप्यूटर दहन संतुलन बनाए रखने के लिए ईंधन की आपूर्ति में अपेक्षित से बड़ा बदलाव कर रहा है।';
        case 'ta': return 'என்ஜின் எரிபொருள் அளவை சரிசெய்ய கணினி பெரிய மாற்றங்களைச் செய்து வருகிறது.';
        case 'te': return 'ఇంజిన్ దహన ప్రక్రియను స్థిరీకరించడానికి కంప్యూటర్ పెద్ద సర్దుబాట్లను చేస్తోంది.';
        case 'kn': return 'ಸರಿಯಾದ ದಹನವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಲು ಇಂಧನದ ಪ್ರಮಾಣದಲ್ಲಿ ದೊಡ್ಡ ಹೊಂದಾಣಿಕೆಗಳನ್ನು ಮಾಡುತ್ತಿದೆ.';
        case 'bn': return 'ইঞ্জিনের সঠিক দহন বজায় রাখতে প্রত্যাশার চেয়ে বেশি জ্বালানি সামঞ্জস্য করা হচ্ছে।';
        case 'mr': return 'इंजिन योग्य ज्वलन राखण्यासाठी आवश्यकतेपेक्षा जास्त इंधन बदल करत आहे.';
        case 'gu': return 'યોગ્ય દહન જાળવવા માટે ઇંધણ પુરવઠામાં અપેક્ષિત કરતાં મોટો ફેરફાર થઈ રહ્યો છે.';
      }
    }
    if (lower.contains('coolant') || key.contains('COOLANT')) {
      switch (lang) {
        case 'hi': return 'इंजन कूलेंट तापमान रीडिंग एप्लिकेशन की कॉन्फ़िगर की गई सामान्य सीमा से बाहर दर्ज की गई।';
        case 'ta': return 'என்ஜின் கூலண்ட் வெப்பநிலை நிர்ணயிக்கப்பட்ட சாதாரண வரம்பிற்கு வெளியே உள்ளது.';
        case 'te': return 'ఇంజిన్ కూలెంట్ ఉష్ణోగ్రత రీడింగ్ సాధారణ పరిధికి వెలుపల నమోదైంది.';
      }
    }
    if (lower.contains('speed') || key.contains('SPEED') || key.contains('RPM')) {
      switch (lang) {
        case 'hi': return 'सेंसर रीडिंग कॉन्फ़िगर की गई सामान्य परिचालन सीमा से बाहर दर्ज की गई।';
        case 'ta': return 'சென்சார் அளவீடு வழக்கமான வரம்பிற்கு வெளியே உள்ளது.';
        case 'te': return 'సెన్సార్ రీడింగ్ సాధారణ పరిధి వెలుపల నమోదైంది.';
      }
    }
    return fallback;
  }

  static String getPidValueMeaning(String pidName, String fallback, String langCode) {
    final lang = _norm(langCode);
    final key = pidName.toUpperCase().trim();
    final match = _pidTranslations[lang]?[key];
    if (match != null && match['value_meaning'] != null) {
      return match['value_meaning']!;
    }
    if (fallback.toLowerCase().contains('positive fuel trim') || key.contains('FUEL_TRIM')) {
      switch (lang) {
        case 'hi': return 'पॉजिटिव फ्यूल ट्रिम (+) का अर्थ है कि हवा अधिक होने पर अतिरिक्त ईंधन दिया जा रहा है (लीन मिश्रण)। नेगेटिव ट्रिम (-) का अर्थ है कि अधिक ईंधन होने पर आपूर्ति घटाई जा रही है (रिच मिश्रण)।';
        case 'ta': return 'நேர்மறை (+) ட்ரிம் என்பது காற்று அதிகமாக இருப்பதால் கூடுதல் எரிபொருள் சேர்க்கப்படுவதைக் குறிக்கிறது. எதிர்மறை (-) ட்ரிம் என்பது எரிபொருள் குறைக்கப்படுவதைக் குறிக்கிறது.';
        case 'te': return 'పాజిటివ్ ట్రిమ్ (+) అంటే అదనపు గాలి వల్ల ఎక్కువ ఇంధనం ఇవ్వబడుతోంది. నెగటివ్ ట్రిమ్ (-) అంటే ఇంధనం తగ్గించబడుతోంది.';
        case 'kn': return 'ಧನಾತ್ಮಕ ಟ್ರಿಮ್ ಎಂದರೆ ಹೆಚ್ಚುವರಿ ಇಂಧನ ನೀಡಲಾಗುತ್ತಿದೆ. ಋಣಾತ್ಮಕ ಟ್ರಿಮ್ ಎಂದರೆ ಇಂಧನ ಕಡಿಮೆ ಮಾಡಲಾಗುತ್ತಿದೆ.';
      }
    }
    return fallback;
  }

  static String getPidSampleExplanation(String pidName, String fallback, num? pctOutside, String langCode) {
    final lang = _norm(langCode);
    final pct = pctOutside ?? 100;
    switch (lang) {
      case 'hi': return 'रिकॉर्ड किए गए नमूनों में से $pct% नमूने एप्लिकेशन की कॉन्फ़िगर की गई सामान्य सीमा से बाहर पाए गए।';
      case 'ta': return 'பதிவு செய்யப்பட்ட அளவீடுகளில் $pct% அளவீடுகள் நிர்ணயிக்கப்பட்ட வரம்பிற்கு வெளியே இருந்தன.';
      case 'te': return 'నమోదైన నమూనాలలో $pct% నమూనాలు అప్లికేషన్ కాన్ఫిగర్ చేసిన పరిధి వెలుపల ఉన్నాయి.';
      case 'kn': return 'ದಾಖಲಿಸಲಾದ ಮಾದರಿಗಳಲ್ಲಿ ಶೇ. $pct ರಷ್ಟು ಮಾದರಿಗಳು ಸಾಮಾನ್ಯ ಮಿತಿಯ ಹೊರಗಿದ್ದವು.';
      case 'bn': return 'রেকর্ড করা নমুনার $pct% অ্যাপ্লিকেশন দ্বারা কনফিগার করা সীমার বাইরে ছিল।';
      case 'mr': return 'नोंदवलेल्या नमुन्यांपैकी $pct% नमुने कॉन्फिगर केलेल्या मर्यादेबाहेर आढळले.';
      case 'gu': return 'રેકોર્ડ કરેલા નમૂનાઓમાંથી $pct% નમૂનાઓ સામાન્ય મર્યાદા બહાર હતા.';
      default: return '$pct% of recorded samples were outside the application\'s configured range.';
    }
  }

  static String getPidCrossFindingNotice(String? crossNotice, String langCode) {
    if (crossNotice == null || crossNotice.isEmpty) return '';
    final lang = _norm(langCode);
    final lower = crossNotice.toLowerCase();
    if (lower.contains('p0171') || lower.contains('positive fuel trim') || lower.contains('vacuum leak')) {
      switch (lang) {
        case 'hi': return 'डायग्नोस्टिक क्रॉस-फाइंडिंग सूचना: डीटीसी P0171 और पॉजिटिव फ्यूल ट्रिम दोनों का एक साथ मिलना इंटेक वैक्यूम लीक या ईंधन आपूर्ति अवरोध की प्रबल संभावना दर्शाता है।';
        case 'ta': return 'கண்டறிதல் அறிவிப்பு: DTC P0171 மற்றும் அதிக எரிபொருள் பயன்பாடு இரண்டும் ஒன்றாக இருப்பது காற்று கசிவு அல்லது எரிபொருள் தடை இருப்பதைக் காட்டுகிறது.';
        case 'te': return 'డయాగ్నస్టిక్ గమనిక: DTC P0171 మరియు పాజిటివ్ ఫ్యూయల్ ట్రిమ్ రెండూ కలిసి ఉండటం వాక్యూమ్ లీక్ లేదా ఇంధన ప్రవాహ అడ్డంకిని సూచిస్తుంది.';
        case 'kn': return 'DTC P0171 ಮತ್ತು ಇಂಧನ ವ್ಯತ್ಯಾಸ ಒಟ್ಟಿಗೆ ಕಂಡುಬರುವುದು ಗಾಳಿ ಸೋರಿಕೆ ಅಥವಾ ಇಂಧನ ಪೂರೈಕೆಯ ಸಮಸ್ಯೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.';
        case 'bn': return 'DTC P0171 এবং পজিটিভ ফুয়েল ট্রিম একসাথে থাকা ভ্যাকুয়াম লিক বা জ্বালানি সরবরাহের বাধার ইঙ্গিত দেয়।';
      }
    }
    return crossNotice;
  }

  static String getPidWhatYouShouldDo(String pidName, String fallback, String langCode) {
    final lang = _norm(langCode);
    final key = pidName.toUpperCase().trim();
    final match = _pidTranslations[lang]?[key];
    if (match != null && match['what_you_should_do'] != null) {
      return match['what_you_should_do']!;
    }
    switch (lang) {
      case 'hi': return 'यदि यह वाहन की वास्तविक रीडिंग है, तो डायग्नोस्टिक जांच करवाएं, विशेष रूप से यदि इंजन असामान्य आवाज कर रहा हो या चेतावनी लाइट जल रही हो।';
      case 'ta': return 'வாகனம் வழக்கத்திற்கு மாறாக இயங்கினால் அல்லது என்ஜின் விளக்கு எரிந்தால் உடனடியாக மெக்கானிக்கிடம் பரிசோதிக்கவும்.';
      case 'te': return 'ఇంజిన్ అసాధారణంగా నడుస్తున్నా లేదా వార్నింగ్ లైట్ వెలుగుతున్నా మెకానిక్‌తో తనిఖీ చేయించండి.';
      case 'kn': return 'ಎಂಜಿನ್ ಅಸಹಜ ಶಬ್ದ ಮಾಡುತ್ತಿದ್ದರೆ ಅಥವಾ ಎಚ್ಚರಿಕೆ ದೀಪ ಉರಿಯುತ್ತಿದ್ದರೆ ತಪಾಸಣೆ ನಡೆಸಿ.';
      case 'bn': return 'ইঞ্জিন অস্বাভাবিকভাবে চললে বা সতর্কতা বাতি জ্বললে দ্রুত পরীক্ষা করান।';
      default: return fallback;
    }
  }

  static String getPidCause(String cause, String langCode) {
    return getDtcCause(cause, langCode);
  }

  static String getPidLimitation(String limitation, String langCode) {
    final lang = _norm(langCode);
    final l = limitation.toLowerCase();
    if (lang == 'hi') {
      if (l.contains('alone does not prove') || l.contains('safe to drive')) {
        return 'यह रीडिंग अकेले यह साबित नहीं करती कि कोई पुर्जा खराब है या वाहन चलाना सुरक्षित है या नहीं।';
      }
      if (l.contains('operating context') || l.contains('idle vs load')) {
        return 'इस रीडिंग का मूल्यांकन वाहन की परिचालन स्थिति (निष्क्रिय बनाम लोड, क्लोज्ड-लूप) के संदर्भ में किया जाना चाहिए।';
      }
      if (l.contains('single fuel-trim') || l.contains('specific faulty sensor')) {
        return 'एकल सेंसर रीडिंग किसी विशिष्ट खराब सेंसर, इंजेक्टर या यांत्रिक हिस्से की निश्चित पहचान नहीं कर सकती।';
      }
    } else if (lang == 'ta') {
      return 'இந்த அளவீடு மட்டுமே ஒரு பாகம் பழுதடைந்துவிட்டது என்பதை நிரூபிக்காது. நேரடி மெக்கானிக் ஆய்வு அவசியம்.';
    } else if (lang == 'te') {
      return 'ఈ రీడింగ్ మాత్రమే ఒక భాగం లోపభూయిష్టంగా ఉందని నిరూపించదు. పూర్తి మెకానిక్ తనిఖీ అవసరం.';
    }
    return limitation;
  }

  static String getPidRangeSource(String rangeSource, String langCode) {
    final lang = _norm(langCode);
    if (lang == 'hi') {
      return rangeSource
          .replaceAll('Application configured monitoring range', 'एप्लिकेशन कॉन्फ़िगर की गई निगरानी सीमा')
          .replaceAll('based on SAE J1979 / OBD-II standard closed-loop trim bounds', 'SAE J1979 / OBD-II मानक क्लोज्ड-लूप सीमा पर आधारित')
          .replaceAll('Not a vehicle-specific OEM specification.', 'यह वाहन-विशिष्ट OEM विनिर्देश नहीं है।')
          .replaceAll('based on typical modern passenger vehicle closed-loop operating window.', 'आधुनिक यात्री वाहनों की मानक क्लोज्ड-लूप ऑपरेटिंग विंडो पर आधारित।');
    } else if (lang == 'ta') {
      return rangeSource
          .replaceAll('Application configured monitoring range', 'கட்டமைக்கப்பட்ட கண்காணிப்பு வரம்பு')
          .replaceAll('Not a vehicle-specific OEM specification.', 'வாகன பிரத்யேக OEM விவரக்குறிப்பு அல்ல.');
    }
    return rangeSource;
  }

  static String getPidTechnicalDetails(String techDetails, String langCode) {
    final lang = _norm(langCode);
    final lower = techDetails.toLowerCase();
    if (lang == 'hi') {
      if (lower.contains('short-term fuel trim') || lower.contains('stft')) {
        return 'शॉर्ट-टर्म फ्यूल ट्रिम (STFT) ऑक्सीजन सेंसर सिग्नल के आधार पर ईसीएम (ECM) द्वारा किए गए तात्कालिक क्लोज्ड-लूप सुधारात्मक समायोजन का प्रतिनिधित्व करता है।';
      }
      if (lower.contains('long-term fuel trim') || lower.contains('ltft')) {
        return 'लॉन्ग-टर्म फ्यूल ट्रिम (LTFT) निरंतर ऑपरेटिंग विसंगतियों को संतुलित करने के लिए सीखा गया मान है।';
      }
      if (lower.contains('coolant temperature') || lower.contains('ntc')) {
        return 'इंजन कूलेंट टेम्परेचर (ECT) सेंसर एनटीसी थर्मिस्टर के माध्यम से इंजन के ऑपरेटिंग तापमान की निगरानी करता है।';
      }
    }
    return techDetails;
  }

  // ---------------------------------------------------------------------------
  // 9. Guidance Passages Public Translation Methods (Visual Damage & OBD DTCs)
  // ---------------------------------------------------------------------------

  static String getGuidanceTitle(String keyOrDtc, String fallback, String langCode) {
    final lang = _norm(langCode);
    final upper = '$keyOrDtc $fallback'.toUpperCase();

    // 1. Visual damage guidance
    if (upper.contains('HEADLIGHT') || upper.contains('TAILLIGHT') || upper.contains('HEADLAMP') || upper.contains('LIGHT')) {
      switch (lang) {
        case 'hi': return 'हेडलाइट / टेललाइट क्षति सुरक्षा मार्गदर्शन';
        case 'ta': return 'முகப்பு / பின்புற விளக்கு சேதம் பாதுகாப்பு வழிகாட்டுதல்';
        case 'te': return 'హెడ్‌లైట్ / టెయిల్‌లైట్ దెబ్బతిన్న భద్రతా మార్గదర్శకత్వం';
        case 'kn': return 'ಹೆಡ್‌ಲೈಟ್ / ಟೈಲ್‌ಲೈಟ್ ಹಾನಿ ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'হেডলাইট / পেছনের লাইট ক্ষতি সুরক্ষা নির্দেশিকা';
        case 'mr': return 'हेडलाइट / टेललाइट नुकसान सुरक्षा मार्गदर्शन';
        case 'gu': return 'હેડલાઇટ / ટેલલાઇટ નુકસાન સુરક્ષા માર્ગદર્શન';
        case 'pa': return 'ਹੈੱਡਲਾਈਟ / ਟੇਲਲਾਈਟ ਨੁਕਸਾਨ ਸੁਰੱਖਿਆ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'ഹെഡ്‌ലൈറ്റ് / ടെയിൽലൈറ്റ് കേടുപാടുകൾ സുരക്ഷാ നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ହେଡଲାଇଟ୍ / ଟେଲଲାଇଟ୍ କ୍ଷତି ସୁରକ୍ଷା ମାର୍ଗଦର୍ଶିକା';
      }
    }
    if (upper.contains('WINDSHIELD') || upper.contains('GLASS')) {
      switch (lang) {
        case 'hi': return 'विंडशील्ड दरार / कांच क्षति सुरक्षा मार्गदर्शन';
        case 'ta': return 'விண்ட்ஷீல்டு விரிசல் / கண்ணாடி சேதம் பாதுகாப்பு வழிகாட்டுதல்';
        case 'te': return 'విండ్‌షీల్డ్ పగులు / గ్లాస్ దెబ్బతిన్న భద్రతా మార్గదర్శకత్వం';
        case 'kn': return 'ವಿಂಡ್‌ಶೀಲ್ಡ್ ಬಿರುಕು / ಗಾಜು ಹಾನಿ ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'উইন্ডশীল্ড ফাটল / কাঁচের ক্ষতি সুরক্ষা নির্দেশিকা';
        case 'mr': return 'विंडशील्ड क्रॅक / काच नुकसान सुरक्षा मार्गदर्शन';
        case 'gu': return 'વિન્ડશિલ્ડ તિરાડ સુરક્ષા માર્ગદર્શન';
        case 'pa': return 'ਵਿੰਡਸ਼ੀਲਡ ਤਰੇੜ ਸੁਰੱਖਿਆ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'വിൻഡ്ഷീൽഡ് വിള്ളൽ സുരക്ഷാ നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ୱିଣ୍ଡଶିଲ୍ଡ ଫାଟ ସୁରକ୍ଷା ମାର୍ଗଦର୍ଶିକା';
      }
    }
    if (upper.contains('BUMPER')) {
      switch (lang) {
        case 'hi': return 'बम्पर असेंबली क्षति सुरक्षा मार्गदर्शन';
        case 'ta': return 'பம்பர் பகுதி சேதம் பாதுகாப்பு வழிகாட்டுதல்';
        case 'te': return 'బంపర్ అసెంబ్లీ దెబ్బతిన్న భద్రతా మార్గదర్శకత్వం';
        case 'kn': return 'ಬಂಪರ್ ಜೋಡಣೆ ಹಾನಿ ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'বাম্পার সমাবেশ ক্ষতি সুরক্ষা নির্দেশিকা';
        case 'mr': return 'बंपर असेंब्ली नुकसान सुरक्षा मार्गदर्शन';
        case 'gu': return 'બમ્પર એસેમ્બલી નુકસાન સુરક્ષા માર્ગદર્શન';
        case 'pa': return 'ਬੰਪਰ ਅਸੈਂਬਲੀ ਨੁਕਸਾਨ ਸੁਰੱਖਿਆ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'ബമ്പർ കേടുപാടുകൾ സുരക്ഷാ നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ବମ୍ପର କ୍ଷତି ସୁରକ୍ଷା ମାର୍ଗଦର୍ଶିକା';
      }
    }
    if (upper.contains('TIRE') || upper.contains('TYRE') || upper.contains('DEFLAT')) {
      switch (lang) {
        case 'hi': return 'टायर क्षति / हवा का रिसाव सुरक्षा मार्गदर्शन';
        case 'ta': return 'டயர் சேதம் அல்லது காற்று குறைவு பாதுகாப்பு வழிகாட்டுதல்';
        case 'te': return 'టైర్ దెబ్బతింది లేదా గాలి తగ్గిన భద్రతా మార్గదర్శకత్వం';
        case 'kn': return 'ಟೈರ್ ಹಾನಿ / ಗಾಳಿ ಕೊರತೆ ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'টায়ার ক্ষতি বা ডিফ্লেশন সুরক্ষা নির্দেশিকা';
        case 'mr': return 'टायर नुकसान / पंक्चर सुरक्षा मार्गदर्शन';
        case 'gu': return 'ટાયર નુકસાન સુરક્ષા માર્ગદર્શન';
        case 'pa': return 'ਟਾਇਰ ਦਾ ਨੁਕਸਾਨ ਸੁਰੱਖਿਆ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'ടയർ തകരാറ് സുരക്ഷാ നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ଟାୟାର୍ କ୍ଷତି ସୁରକ୍ଷା ମାର୍ଗଦର୍ଶିକା';
      }
    }
    if (upper.contains('SCRATCH')) {
      switch (lang) {
        case 'hi': return 'बाहरी पेंट खरोंच (Scratch) मरम्मत मार्गदर्शन';
        case 'ta': return 'மேற்பரப்பு பெயிண்ட் கீறல் பழுது வழிகாட்டுதல்';
        case 'te': return 'బాహ్య పెయింట్ గీతలు మరమ్మతు మార్గదర్శకత్వం';
        case 'kn': return 'ಬಾಹ್ಯ ಪೇಂಟ್ ಗೀರು ದುರಸ್ತಿ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'বাহ্যিক পেইন্ট স্ক্র্যাচ মেরামত নির্দেশিকা';
        case 'mr': return 'बाहेरील पेंट ओरखडा दुरुस्ती मार्गदर्शन';
        case 'gu': return 'પેઇન્ટ સ્ક્રેચ સમારકામ માર્ગદર્શન';
        case 'pa': return 'ਪੇਂਟ ਸਕ੍ਰੈਚ ਮੁਰੰਮਤ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'പെയിന്റിലെ പോറലുകൾ പരിഹരിക്കാനുള്ള നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ପେଣ୍ଟ୍ ସ୍କ୍ରାଚ୍ ମରାମତି ମାର୍ଗଦର୍ଶିକା';
      }
    }
    if (upper.contains('DENT')) {
      switch (lang) {
        case 'hi': return 'बॉडी पैनल डेंट (Dent) मरम्मत मार्गदर्शन';
        case 'ta': return 'பாடி பேனல் பள்ளம் (Dent) பழுது வழிகாட்டுதல்';
        case 'te': return 'బాడీ ప్యానెల్ డెంట్ (Dent) మరమ్మతు మార్గదర్శకత్వం';
        case 'kn': return 'ಬಾಡಿ ಪ್ಯಾನೆಲ್ ಡೆಂಟ್ ದುರಸ್ತಿ ಮಾರ್ಗದರ್ಶನ';
        case 'bn': return 'বডি প্যানেল ডেন্ট মেরামত নির্দেশিকা';
        case 'mr': return 'बॉडी पॅनेल डेंट दुरुस्ती मार्गदर्शन';
        case 'gu': return 'બોડી પેનલ ડેન્ટ સમારકામ માર્ગદર્શન';
        case 'pa': return 'ਬਾਡੀ ਪੈਨਲ ਡੈਂਟ ਮੁਰੰਮਤ ਮਾਰਗਦਰਸ਼ਨ';
        case 'ml': return 'ബോഡി പാനൽ ഡെന്റ് പരിഹരിക്കാനുള്ള നിർദ്ദേശങ്ങൾ';
        case 'or': return 'ବଡି ପ୍ୟାନେଲ୍ ଡେଣ୍ଟ୍ ମରାମତି ମାର୍ଗଦର୍ଶିକା';
      }
    }

    // 2. DTC codes
    for (final code in ['P0300', 'P0128', 'P0401', 'P0171', 'P0420', 'P0217', 'P0133', 'P0455', 'P0700']) {
      if (upper.contains(code)) {
        final match = _guidanceTranslations[lang]?[code];
        if (match != null && match['title'] != null) {
          return match['title'] as String;
        }
      }
    }
    return fallback;
  }

  static String getGuidanceWhatWeFound(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();

    // 1. Visual damage guidance
    if (lower.contains('headlight') || lower.contains('taillight') || lower.contains('cracked or broken')) {
      switch (lang) {
        case 'hi': return 'आपकी हेडलाइट या टेललाइट में दरार या टूटने की संभावना पाई गई है।';
        case 'ta': return 'உங்கள் முகப்பு விளக்கு அல்லது பின்புற விளக்கு விரிசல் அடைந்துள்ளதாக அல்லது உடைந்திருக்கலாம் என்று கண்டறியப்பட்டுள்ளது.';
        case 'te': return 'మీ హెడ్‌లైట్ లేదా టెయిల్‌లైట్ పగిలిపోయినట్లు లేదా విరిగిపోయినట్లు గుర్తించబడింది.';
        case 'kn': return 'ನಿಮ್ಮ ಹೆಡ್‌ಲೈಟ್ ಅಥವಾ ಟೈಲ್‌ಲೈಟ್ ಬಿರುಕು ಬಿಟ್ಟಿದೆ ಅಥವಾ ಮುರಿದಿದೆ ಎಂದು ಕಂಡುಬಂದಿದೆ.';
        case 'bn': return 'আপনার হেডলাইট বা পেছনের লাইটে ফাটল বা ভাঙা দেখা গেছে।';
        case 'mr': return 'तुमची हेडलाइट किंवा टेललाइट क्रॅक किंवा तुटलेली आढळली आहे.';
        case 'gu': return 'તમારી હેડલાઇટ અથવા ટેલલાઇટ તૂટેલી અથવા તિરાડ પડેલી જણાય છે.';
        case 'pa': return 'ਤੁਹਾਡੀ ਹੈੱਡਲਾਈਟ ਜਾਂ ਟੇਲਲਾਈਟ ਟੁੱਟੀ ਹੋਈ ਜਾਂ ਤਰੇੜ ਵਾਲੀ ਹੋ ਸਕਦੀ ਹੈ।';
        case 'ml': return 'ഹെഡ്‌ലൈറ്റിലോ ടെയിൽലൈറ്റിലോ വിള്ളലോ തകരാറോ കണ്ടെത്തി.';
        case 'or': return 'ଆପଣଙ୍କ ହେଡଲାଇଟ୍ କିମ୍ବା ଟେଲଲାଇଟ୍ ଫାଟିଯାଇଥିବା ବା ଭାଙ୍ଗିଯାଇଥିବା ଚିହ୍ନଟ ହୋଇଛି।';
      }
    }
    if (lower.contains('windshield') || lower.contains('crack that may affect')) {
      switch (lang) {
        case 'hi': return 'आपकी विंडशील्ड में एक दरार पाई गई है जो दृश्यता या कांच की मजबूती को प्रभावित कर सकती है।';
        case 'ta': return 'உங்கள் விண்ட்ஷீல்டில் விரிசல் உள்ளது, இது பார்வையை அல்லது கண்ணாடியின் வலிமையைப் பாதிக்கலாம்.';
        case 'te': return 'మీ విండ్‌షీల్డ్‌లో పగులు ఉంది, ఇది దృష్టిని లేదా గాజు బలాన్ని ప్రభావితం చేయవచ్చు.';
        case 'kn': return 'ನಿಮ್ಮ ವಿಂಡ್‌ಶೀಲ್ಡ್‌ನಲ್ಲಿ ಬಿರುಕು ಇದೆ, ಇದು ನಿಮ್ಮ ದೃಷ್ಟಿ ಅಥವಾ ಗಾಜಿನ ಬಲವನ್ನು ಕುಂದಿಸಬಹುದು.';
        case 'bn': return 'আপনার উইন্ডশীল্ডে একটি ফাটল রয়েছে যা দৃষ্টি বা কাঁচের শক্তিকে প্রভাবিত করতে পারে।';
        case 'mr': return 'तुमच्या विंडशील्डवर एक क्रॅक आहे जो दृश्यमानता किंवा काचेच्या मजबुतीवर परिणाम करू शकतो.';
        case 'gu': return 'તમારી વિન્ડશિલ્ડમાં તિરાડ છે જે દ્રશ્યતા અથવા કાચની મજબૂતાઈને અસર કરી શકે છે.';
        case 'pa': return 'ਤੁਹਾਡੀ ਵਿੰਡਸ਼ੀਲਡ ਵਿੱਚ ਇੱਕ ਤਰੇੜ ਹੈ ਜੋ ਤੁਹਾਡੇ ਦ੍ਰਿਸ਼ ਜਾਂ ਸ਼ੀਸ਼ੇ ਦੀ ਮਜ਼ਬੂਤੀ ਨੂੰ ਪ੍ਰਭਾਵਤ ਕਰ ਸਕਦੀ ਹੈ।';
        case 'ml': return 'വിൻഡ്ഷീൽഡിലെ വിള്ളൽ കാഴ്‌ചയെയോ ഗ്ലാസിന്റെ ബലത്തെയോ ബാധിച്ചേക്കാം.';
        case 'or': return 'ଆପଣଙ୍କ ୱିଣ୍ଡଶିଲ୍ଡରେ ଏକ ଫାଟ ଅଛି ଯାହା ଦୃଶ୍ୟମାନତା କିମ୍ବା କାଚର ଶକ୍ତିକୁ ପ୍ରଭାବିତ କରିପାରେ।';
      }
    }
    if (lower.contains('bumper assembly') || lower.contains('damage was detected on your bumper')) {
      switch (lang) {
        case 'hi': return 'आपकी बम्पर असेंबली पर बाहरी क्षति का पता चला है।';
        case 'ta': return 'உங்கள் பம்பர் பகுதியில் சேதம் கண்டறியப்பட்டுள்ளது.';
        case 'te': return 'మీ బంపర్ అసెంబ్లీపై నష్టం గుర్తించబడింది.';
        case 'kn': return 'ನಿಮ್ಮ ಬಂಪರ್ ಜೋಡಣೆಯಲ್ಲಿ ಹಾನಿ ಕಂಡುಬಂದಿದೆ.';
        case 'bn': return 'আপনার বাম্পার সমাবেশে ক্ষতি সনাক্ত করা হয়েছে।';
        case 'mr': return 'तुमच्या बंपर असेंब्लीवर नुकसान आढळले आहे.';
        case 'gu': return 'તમારી બમ્પર એસેમ્બલી પર નુકસાન જણાયું છે.';
        case 'pa': return 'ਤੁਹਾਡੀ ਬੰਪਰ ਅਸੈਂਬਲੀ ਵਿੱਚ ਨੁਕਸਾਨ ਪਾਇਆ ਗਿਆ ਹੈ।';
        case 'ml': return 'ബമ്പർ ഭാഗത്ത് കേടുപാടുകൾ കണ്ടെത്തിയിട്ടുണ്ട്.';
        case 'or': return 'ଆପଣଙ୍କ ବମ୍ପର ଆସେମ୍ବଲିରେ କ୍ଷତି ଚିହ୍ନଟ ହୋଇଛି।';
      }
    }
    if (lower.contains('tire appears flat') || lower.contains('deflated') || lower.contains('tire')) {
      switch (lang) {
        case 'hi': return 'एक टायर पंचर, अत्यधिक हवा रहित या क्षतिग्रस्त दिखाई देता है।';
        case 'ta': return 'ஒரு டயர் பஞ்சராகவோ அல்லது சேதமடைந்ததாகவோ தெரிகிறது.';
        case 'te': return 'ఒక టైర్ ఫ్లాట్‌గా, గణనీయంగా గాలి తగ్గిపోయినట్లు లేదా దెబ్బతిన్నట్లు కనిపిస్తోంది.';
        case 'kn': return 'ಒಂದು ಟೈರ್ ಪಂಕ್ಚರ್ ಆಗಿದೆ ಅಥವಾ ಹಾನಿಗೊಳಗಾಗಿದೆ ಎಂದು ತೋರುತ್ತದೆ.';
        case 'bn': return 'একটি টায়ার ফ্ল্যাট, বাতাসহীন বা ক্ষতিগ্রস্থ দেখাচ্ছে।';
        case 'mr': return 'एक टायर पंक्चर किंवा खराब झालेला दिसत आहे.';
        case 'gu': return 'એક ટાયર પંચર અથવા ક્ષતિગ્રસ્ત જણાય છે.';
        case 'pa': return 'ਇੱਕ ਟਾਇਰ ਪੰਕਚਰ ਜਾਂ ਖਰਾਬ ਜਾਪਦਾ ਹੈ।';
        case 'ml': return 'ഒരു ടയർ കാറ്റ് കുറഞ്ഞതോ തകരാറിലായതോ ആയി കാണപ്പെടുന്നു.';
        case 'or': return 'ଗୋଟିଏ ଟାୟାର୍ ପଞ୍ଚର କିମ୍ବା କ୍ଷତିଗ୍ରସ୍ତ ଥିବା ଜଣାପଡୁଛି।';
      }
    }
    if (lower.contains('surface paint scratch') || lower.contains('scratching was detected')) {
      switch (lang) {
        case 'hi': return 'वाहन के बाहरी पैनल पर पेंट की खरोंच (Scratch) का पता चला है।';
        case 'ta': return 'வாகனத்தின் வெளிப்புற பேனலில் பெயிண்ட் கீறல் கண்டறியப்பட்டுள்ளது.';
        case 'te': return 'వాహనం బాహ్య ప్యానెల్‌పై పెయింట్ గీతలు గుర్తించబడ్డాయి.';
        case 'kn': return 'ವಾಹನದ ಬಾಹ್ಯ ಪ್ಯಾನೆಲ್‌ನಲ್ಲಿ ಪೇಂಟ್ ಗೀರು ಕಂಡುಬಂದಿದೆ.';
        case 'bn': return 'গাড়ির বাইরের প্যানেলে পেইন্ট স্ক্র্যাচ সনাক্ত হয়েছে।';
        case 'mr': return 'वाहनाच्या बाहेरील पॅनेलवर पेंट ओरखडा आढळला आहे.';
        case 'gu': return 'વાહનની સપાટી પર પેઇન્ટ સ્ક્રેચ જણાયો છે.';
        case 'pa': return 'ਵਾਹਨ ਦੇ ਬਾਹਰੀ ਪੈਨਲ ਤੇ ਪੇਂਟ ਸਕ੍ਰੈਚ ਪਾਇਆ ਗਿਆ ਹੈ।';
        case 'ml': return 'വാഹനത്തിന്റെ പുറം പാനലിൽ പെയിന്റ് പോറൽ കണ്ടെത്തി.';
        case 'or': return 'ଗାଡିର ବାହ୍ୟ ପ୍ୟାନେଲରେ ପେଣ୍ଟ୍ ସ୍କ୍ରାଚ୍ ଚିହ୍ନଟ ହୋଇଛି।';
      }
    }
    if (lower.contains('panel dent') || lower.contains('indentation was detected')) {
      switch (lang) {
        case 'hi': return 'वाहन की बॉडी पर पैनल डेंट या दबाव का निशान पाया गया है।';
        case 'ta': return 'வாகனத்தின் உடலில் பேனல் பள்ளம் (Dent) கண்டறியப்பட்டுள்ளது.';
        case 'te': return 'వాహనం బాడీపై ప్యానెల్ డెంట్ గుర్తించబడింది.';
        case 'kn': return 'ವಾಹನದ ದೇಹದಲ್ಲಿ ಪ್ಯಾನೆಲ್ ಡೆಂಟ್ ಕಂಡುಬಂದಿದೆ.';
        case 'bn': return 'গাড়ির বডিতে প্যানেল ডেন্ট সনাক্ত হয়েছে।';
        case 'mr': return 'वाहनाच्या बॉडीवर पॅनेल डेंट आढळला आहे.';
        case 'gu': return 'વાહનની બોડી પર પેનલ ડેન્ટ જણાયો છે.';
        case 'pa': return 'ਵਾਹਨ ਦੀ ਬਾਡੀ ਤੇ ਪੈਨਲ ਡੈਂਟ ਪਾਇਆ ਗਿਆ ਹੈ।';
        case 'ml': return 'വാഹനത്തിന്റെ ബോഡിയിൽ ഡെന്റ് കണ്ടെത്തി.';
        case 'or': return 'ଗାଡିର ବଡିରେ ପ୍ୟାନେଲ୍ ଡେଣ୍ଟ୍ ଚିହ୍ନଟ ହୋଇଛି।';
      }
    }

    // 2. OBD DTC guidance
    if (lower.contains('cylinder') || lower.contains('misfire')) {
      final match = _guidanceTranslations[lang]?['P0300'];
      if (match != null && match['what_we_found'] != null) return match['what_we_found'] as String;
    }
    if (lower.contains('recirculate') || lower.contains('egr')) {
      final match = _guidanceTranslations[lang]?['P0401'];
      if (match != null && match['what_we_found'] != null) return match['what_we_found'] as String;
    }
    if (lower.contains('temperature') || lower.contains('warm')) {
      final match = _guidanceTranslations[lang]?['P0128'];
      if (match != null && match['what_we_found'] != null) return match['what_we_found'] as String;
    }
    if (lower.contains('lean') || lower.contains('fuel')) {
      final match = _guidanceTranslations[lang]?['P0171'];
      if (match != null && match['what_we_found'] != null) return match['what_we_found'] as String;
    }
    return fallback;
  }

  static String getGuidanceWhyThisMatters(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();

    // 1. Visual damage guidance
    if (lower.contains('broken lights reduce') || lower.contains('visibility') || lower.contains('headlight')) {
      switch (lang) {
        case 'hi': return 'टूटी हुई लाइटें दृश्यता कम करती हैं और रात में दुर्घटना का खतरा बढ़ाती हैं। इसके अलावा अंदर नमी जाने से वायरिंग शॉर्ट हो सकती है।';
        case 'ta': return 'உடைந்த விளக்குகள் பார்வைத்திறனைக் குறைத்து இரவு நேர விபத்து அபாயத்தை அதிகரிக்கும். மின்சாரக் கோளாறுகளையும் ஏற்படுத்தலாம்.';
        case 'te': return 'విరిగిన లైట్లు రాత్రి వేళల్లో ప్రమాదాల ముప్పును పెంచుతాయి. నీరు లోపలికి చేరి వైరింగ్ దెబ్బతినే అవకాశం ఉంది.';
        case 'kn': return 'ಮುರಿದ ದೀಪಗಳು ರಾತ್ರಿಯ ಗೋಚರತೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ ಅಪಘಾತದ ಅಪಾಯವನ್ನು ಹೆಚ್ಚಿಸುತ್ತವೆ.';
        case 'bn': return 'ভাঙা লাইট রাতে দৃশ্যমানতা কমায় এবং দুর্ঘটনার ঝুঁকি বাড়ায়।';
        case 'mr': return 'तुटलेल्या दिव्यांमुळे रात्री अपघाताचा धोका वाढतो आणि वायरिंग शॉर्ट होऊ शकते.';
        case 'gu': return 'તૂટેલી લાઇટો રાત્રે દ્રશ્યતા ઘટાડે છે અને અકસ્માતનું જોખમ વધારે છે.';
      }
    }
    if (lower.contains('cracks can spread') || lower.contains('rollover') || lower.contains('windshield')) {
      switch (lang) {
        case 'hi': return 'सड़क के झटकों और तापमान से दरारें तेजी से फैलती हैं, जिससे दृश्यता बाधित होती है और वाहन पलटने की स्थिति में छत की मजबूती घट जाती है।';
        case 'ta': return 'விரிசல்கள் அதிர்வுகளால் வேகமாகப் பரவி, ஓட்டுநரின் பார்வையைத் தடுக்கும் மற்றும் விபத்தின் போது கூரையின் வலிமையைக் குறைக்கும்.';
        case 'te': return 'రోడ్డు కుదుపుల వల్ల పగుళ్లు వేగంగా విస్తరించి ప్రమాదకరంగా మారతాయి.';
        case 'kn': return 'ರಸ್ತೆಯ ಕಂಪನಗಳಿಂದ ಬಿರುಕುಗಳು ವೇಗವಾಗಿ ಹರಡಬಹುದು ಮತ್ತು ಚಾಲಕನ ನೋಟಕ್ಕೆ ಅಡ್ಡಿಯಾಗಬಹುದು.';
        case 'bn': return 'ফাটল দ্রুত ছড়িয়ে পড়তে পারে এবং দৃষ্টিশক্তিকে বাধাগ্রস্ত করতে পারে।';
        case 'mr': return 'रस्त्यावरील धक्क्यांमुळे क्रॅक वेगाने पसरू शकतो आणि छत कमकुवत होऊ शकते.';
      }
    }
    if (lower.contains('bumpers absorb impact') || lower.contains('radiator') || lower.contains('bumper')) {
      switch (lang) {
        case 'hi': return 'बम्पर कम गति की टक्कर में झटके को अवशोषित करते हैं और उसके पीछे स्थित रेडिएटर, एसी कंडेनसर और सेंसर की सुरक्षा करते हैं।';
        case 'ta': return 'பம்பர்கள் மோதல் அதிர்வுகளைத் தாங்கி, பின்னால் உள்ள ரேடியேட்டர் மற்றும் சென்சார்களைப் பாதுகாக்கின்றன.';
        case 'te': return 'బంపర్లు ప్రభావ శక్తిని గ్రహించి వెనుక ఉన్న రేడియేటర్ మరియు సెన్సార్లను రక్షిస్తాయి.';
        case 'kn': return 'ಬಂಪರ್‌ಗಳು ಡಿಕ್ಕಿಯ ಹೊಡೆತವನ್ನು ಹೀರಿಕೊಂಡು ಒಳಗಿನ ರೇಡಿಯೇಟರ್ ಅನ್ನು ರಕ್ಷಿಸುತ್ತವೆ.';
      }
    }
    if (lower.contains('driving on an underinflated') || lower.contains('blowout') || lower.contains('tire')) {
      switch (lang) {
        case 'hi': return 'हवा रहित या क्षतिग्रस्त टायर पर चलने से अचानक टायर फटने (blowout), गाड़ी का संतुलन बिगड़ने और पहिये के रिम को स्थायी नुकसान का गंभीर खतरा होता है।';
        case 'ta': return 'காற்றற்ற டயரில் ஓட்டுவது டயர் வெடிப்பு மற்றும் ஸ்டீயரிங் கட்டுப்பாட்டை இழக்கும் பெரும் ஆபத்தை ஏற்படுத்தும்.';
        case 'te': return 'గాలి లేని టైర్‌పై నడపడం వల్ల టైర్ పేలిపోయి ప్రమాదం జరిగే అవకాశం ఉంది.';
        case 'kn': return 'ಪಂಕ್ಚರ್ ಆದ ಟೈರ್‌ನಲ್ಲಿ ಚಾಲನೆ ಮಾಡುವುದರಿಂದ ಟೈರ್ ಸ್ಫೋಟಗೊಳ್ಳುವ ಅಪಾಯವಿರುತ್ತದೆ.';
      }
    }
    if (lower.contains('surface paint') || lower.contains('bare metal') || lower.contains('rust')) {
      switch (lang) {
        case 'hi': return 'गहरी खरोंचें प्राइमर की परत को चीरकर धातु को नमी के संपर्क में लाती हैं, जिससे पैनल में जंग (rusting) लगना शुरू हो जाता है।';
        case 'ta': return 'ஆழமான கீறல்கள் ஈரப்பதம் காரணமாக துருப்பிடிப்பதை (rust) விரைவுபடுத்தும்.';
        case 'te': return 'లోతైన గీతల వల్ల లోహానికి తుప్పు పట్టే ప్రమాదం ఉంది.';
      }
    }
    if (lower.contains('dents may affect') || lower.contains('door opening') || lower.contains('dent')) {
      switch (lang) {
        case 'hi': return 'डेंट से दरवाजों के खुलने-बंद होने में रुकावट आ सकती है और पानी जमा होकर जंग का कारण बन सकता है।';
        case 'ta': return 'பள்ளங்கள் கதவு மூடுவதைப் பாதிக்கலாம் மற்றும் துருப்பிடிக்க வழிவகுக்கும்.';
        case 'te': return 'డెంట్ల వల్ల తలుపులు సరిగ్గా మూతపడకపోవచ్చు మరియు తుప్పు పట్టవచ్చు.';
      }
    }

    // 2. OBD DTC guidance
    if (lower.contains('misfire') || lower.contains('catalytic')) {
      final match = _guidanceTranslations[lang]?['P0300'];
      if (match != null && match['why_this_matters'] != null) return match['why_this_matters'] as String;
    }
    if (lower.contains('recirculates') || lower.contains('exhaust gas') || lower.contains('pinging')) {
      final match = _guidanceTranslations[lang]?['P0401'];
      if (match != null && match['why_this_matters'] != null) return match['why_this_matters'] as String;
    }
    if (lower.contains('operating temperature') || lower.contains('cabin heat')) {
      final match = _guidanceTranslations[lang]?['P0128'];
      if (match != null && match['why_this_matters'] != null) return match['why_this_matters'] as String;
    }
    return fallback;
  }

  static String getGuidanceWhatYouShouldDoNow(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();

    // 1. Visual damage guidance
    if (lower.contains('inspect the lens') || lower.contains('bulbs promptly') || lower.contains('headlight')) {
      switch (lang) {
        case 'hi': return 'लेंस और बल्बों की जांच करें। सड़क पर कानूनी रूप से सुरक्षित रहने के लिए टूटी हुई लाइट तुरंत बदलें।';
        case 'ta': return 'விளக்குகளைப் பரிசோதிக்கவும். பாதுகாப்பாக இருக்க உடைந்த பாகங்களை உடனடியாக மாற்றவும்.';
        case 'te': return 'లైట్లను పరిశీలించండి. విరిగిన భాగాలను వెంటనే మార్చండి.';
        case 'kn': return 'ದೀಪಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ ಮತ್ತು ಮುರಿದ ಭಾಗಗಳನ್ನು ತಕ್ಷಣ ಬದಲಾಯಿಸಿ.';
      }
    }
    if (lower.contains('do not delay glass') || lower.contains('windshield replacement') || lower.contains('windshield')) {
      switch (lang) {
        case 'hi': return 'शीशे की जांच में देरी न करें। छोटी दरार को रेजिन से ठीक करवाएं, जबकि बड़ी दरार में विंडशील्ड बदलवाएं।';
        case 'ta': return 'கண்ணாடி பரிசோதனையை தாமதிக்க வேண்டாம். தேவையானால் உடனடியாக புதிய விண்ட்ஷீல்டு பொருத்தவும்.';
        case 'te': return 'విండ్‌షీల్డ్ పగులును నిర్లక్ష్యం చేయవద్దు. త్వరగా గ్లాస్ మరమ్మతు చేయించండి.';
      }
    }
    if (lower.contains('bumper is firmly attached') || lower.contains('rubbing against') || lower.contains('bumper')) {
      switch (lang) {
        case 'hi': return 'जांचें कि बम्पर पहियों से रगड़ तो नहीं खा रहा है। यदि बम्पर सुरक्षित है तो वर्कशॉप ले जाकर क्लिप्स और सेंसर चेक करवाएं।';
        case 'ta': return 'பம்பர் டயர்களில் உராயவில்லை என்பதை உறுதிசெய்து மெக்கானிக்கிடம் செல்லவும்.';
        case 'te': return 'బంపర్ గట్టిగా అమర్చబడి ఉందో లేదో తనిఖీ చేసి వర్క్‌షాప్‌కు తీసుకెళ్లండి.';
      }
    }
    if (lower.contains('stop in a safe place') || lower.contains('spare tire') || lower.contains('puncture') || lower.contains('tire')) {
      switch (lang) {
        case 'hi': return 'तुरंत सुरक्षित स्थान पर रुकें। पंचर टायर पर गाड़ी न चलाएं। स्पेयर टायर लगाएं या सड़क किनारे सहायता लें।';
        case 'ta': return 'பாதுகாப்பான இடத்தில் உடனடியாக நிறுத்துங்கள். காற்றற்ற டயரில் ஓட்ட வேண்டாம். மாற்று டயரைப் பொருத்தவும்.';
        case 'te': return 'వెంటనే సురక్షిత ప్రదేశంలో ఆపండి. ఫ్లాట్ టైర్‌పై డ్రైవ్ చేయకండి. స్పేర్ టైర్ అమర్చండి.';
        case 'kn': return 'ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ನಿಲ್ಲಿಸಿ. ಸ್ಪೇರ್ ಟೈರ್ ಬದಲಾಯಿಸಿ ಅಥವಾ ಪಂಕ್ಚರ್ ಸಹಾಯ ಪಡೆಯಿರಿ.';
      }
    }
    if (lower.contains('scratch depth') || lower.contains('touch up') || lower.contains('scratch')) {
      switch (lang) {
        case 'hi': return 'खरोंच की गहराई जांचें। मामूली खरोंच को बफ करवाएं; धातु तक पहुंची खरोंच पर शीघ्र जंग-रोधी पेंट करवाएं।';
        case 'ta': return 'கீறலின் ஆழத்தை சரிபார்க்கவும். துருப்பிடிக்காமல் இருக்க பெயிண்ட் டச்-அப் செய்யவும்.';
        case 'te': return 'గీతలను పరిశీలించి తుప్పు పట్టకుండా పెయింట్ టచ్-అప్ చేయించండి.';
      }
    }
    if (lower.contains('pdr') || lower.contains('paintless dent repair') || lower.contains('dent')) {
      switch (lang) {
        case 'hi': return 'जांचें कि दरवाजे ठीक से बंद हो रहे हैं या नहीं। बिना पेंट क्षति वाले डेंट को PDR तकनीक से ठीक करवाएं।';
        case 'ta': return 'கதவுகள் சரியாக மூடுகின்றனவா என்று சரிபார்த்து PDR நிபுணரை அணுகவும்.';
        case 'te': return 'తలుపులు సజావుగా తెరుచుకుంటున్నాయో లేదో తనిఖీ చేయండి.';
      }
    }

    // 2. OBD DTC guidance
    if (lower.contains('flashing') || lower.contains('shaking')) {
      final match = _guidanceTranslations[lang]?['P0300'];
      if (match != null && match['what_you_should_do_now'] != null) return match['what_you_should_do_now'] as String;
    }
    if (lower.contains('checked before replacing parts') || lower.contains('system checked')) {
      final match = _guidanceTranslations[lang]?['P0401'];
      if (match != null && match['what_you_should_do_now'] != null) return match['what_you_should_do_now'] as String;
    }
    if (lower.contains('cooling system') || lower.contains('thermostat')) {
      final match = _guidanceTranslations[lang]?['P0128'];
      if (match != null && match['what_you_should_do_now'] != null) return match['what_you_should_do_now'] as String;
    }
    return fallback;
  }

  static String getGuidanceCanIKeepDriving(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();
    if (lang == 'hi') {
      if (lower.contains('stop in a safe place') || lower.contains('immediately')) return 'तुरंत सुरक्षित स्थान पर रुकें; आगे न चलाएं।';
      if (lower.contains('avoid unnecessary') || lower.contains('avoid night') || lower.contains('avoid rough')) return 'अनावश्यक या तेज ड्राइविंग से बचें; जल्द मरम्मत करवाएं।';
      if (lower.contains('arrange a mechanic') || lower.contains('appointment') || lower.contains('cautiously')) return 'सावधानी से ड्राइव करें और शीघ्र मैकेनिक से अपॉइंटमेंट लें।';
      if (lower.contains('no immediate action') || lower.contains('safe to drive')) return 'सामान्य परिस्थितियों में चलाना सुरक्षित है। नियमित सर्विस में दिखाएं।';
    } else if (lang == 'ta') {
      if (lower.contains('stop in a safe place') || lower.contains('immediately')) return 'உடனடியாக பாதுகாப்பான இடத்தில் வாகனத்தை நிறுத்துங்கள்.';
      if (lower.contains('avoid unnecessary')) return 'தேவையற்ற பயணங்களைத் தவிர்க்கவும்; பரிசோதிக்கவும்.';
      if (lower.contains('arrange a mechanic')) return 'விரைவில் மெக்கானிக்கிடம் செல்லவும்.';
      if (lower.contains('safe to drive') || lower.contains('no immediate action')) return 'இயல்பு நிலையில் பாதுகாப்பானது.';
    } else if (lang == 'te') {
      if (lower.contains('stop in a safe place') || lower.contains('immediately')) return 'వెంటనే సురక్షిత ప్రదేశంలో ఆపండి.';
      if (lower.contains('avoid unnecessary')) return 'అనవసరంగా డ్రైవ్ చేయకండి; త్వరగా తనిఖీ చేయించండి.';
      if (lower.contains('arrange a mechanic')) return 'త్వరలో మెకానిక్‌ను సంప్రదించండి.';
      if (lower.contains('safe to drive') || lower.contains('no immediate action')) return 'సురక్షితంగా డ్రైవ్ చేయవచ్చు.';
    } else if (lang == 'kn') {
      if (lower.contains('stop in a safe place')) return 'ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ತಕ್ಷಣ ನಿಲ್ಲಿಸಿ.';
      if (lower.contains('avoid unnecessary')) return 'ಅನಗತ್ಯ ಚಾಲನೆಯನ್ನು ತಪ್ಪಿಸಿ; ತಪಾಸಣೆ ನಡೆಸಿ.';
      if (lower.contains('safe to drive')) return 'ಸಾಮಾನ್ಯ ಸ್ಥಿತಿಯಲ್ಲಿ ಚಾಲನೆ ಸುರಕ್ಷಿತ.';
    }
    return fallback;
  }

  static List<String> getMechanicChecks(List<String> originalChecks, String langCode) {
    final lang = _norm(langCode);
    if (lang == 'en') return originalChecks;
    return originalChecks.map((c) {
      final l = c.toLowerCase();
      if (lang == 'hi') {
        if (l.contains('headlamp housing') || l.contains('lens condition')) return 'हेडलाइट हाउसिंग एवं लेंस की स्थिति';
        if (l.contains('bulb operation') || l.contains('filament')) return 'बल्ब कार्यप्रणाली एवं फिलामेंट निरंतरता';
        if (l.contains('wiring harness') || l.contains('moisture corrosion')) return 'वायरिंग हार्नेस एवं नमी से जंग की जांच';
        if (l.contains('beam alignment')) return 'हेडलाइट बीम अलाइनमेंट एवं लेवलिंग';
        if (l.contains('crack length') || l.contains('spreading risk')) return 'दरार की लंबाई एवं फैलने के जोखिम का मूल्यांकन';
        if (l.contains('driver swept area') || l.contains('visibility obstruction')) return 'ड्राइवर दृश्यता क्षेत्र में रुकावट की जांच';
        if (l.contains('laminated glass') || l.contains('layer separation')) return 'लेमिनेटेड कांच की परतों का अलगाव';
        if (l.contains('adas camera') || l.contains('sensor calibration')) return 'ADAS कैमरा एवं ग्लास सेंसर कैलिब्रेशन';
        if (l.contains('bumper mounting clips') || l.contains('absorber bracket')) return 'बम्पर क्लिप्स एवं शॉक एब्जॉर्बर ब्रैकेट की मजबूती';
        if (l.contains('radiator and ac condenser') || l.contains('clearance')) return 'रेडिएटर और एसी कंडेनसर के बीच सुरक्षित दूरी';
        if (l.contains('parking sensors') || l.contains('radar')) return 'पार्किंग सेंसर, रडार एवं फॉग लैंप वायरिंग';
        if (l.contains('impact beam') || l.contains('crumple zone')) return 'इम्पैक्ट बीम एवं क्रंपल ज़ोन अलाइनमेंट';
        if (l.contains('tread depth') || l.contains('uneven wear')) return 'ट्रेड की गहराई एवं घिसाव पैटर्न';
        if (l.contains('sidewall punctures') || l.contains('cuts') || l.contains('bulges')) return 'साइडवॉल कट, उभार (bulge) एवं पंचर निरीक्षण';
        if (l.contains('wheel rim') || l.contains('bead seal')) return 'पहिए की रिम, बीड सील एवं संरचनात्मक संतुलन';
        if (l.contains('tpms sensor') || l.contains('valve stem')) return 'TPMS टायर प्रेशर सेंसर एवं वाल्व स्टेम स्थिति';
        if (l.contains('scratch depth assessment') || l.contains('clear-coat')) return 'खरोंच की गहराई का मूल्यांकन (क्लियर-कोट बनाम धातु)';
        if (l.contains('corrosion') || l.contains('oxidation')) return 'आंतरिक जंग या ऑक्सीकरण का निरीक्षण';
        if (l.contains('paintless dent repair') || l.contains('pdr feasibility')) return 'पेंटलेस डेंट रिपेयर (PDR) की उपयुक्तता';
        if (l.contains('door latch') || l.contains('hinge') || l.contains('weatherstrip')) return 'दरवाजे की कुंडी, हिंज एवं वेदरस्ट्रिप सील अलाइनमेंट';
        if (l.contains('spark plug') || l.contains('ignition coil')) return 'स्पार्क प्लग और इग्निशन कॉइल की स्थिति';
        if (l.contains('fuel pressure') || l.contains('injector')) return 'ईंधन दबाव और फ्यूल इंजेक्टर';
        if (l.contains('intake air') || l.contains('vacuum')) return 'इंटेक एयर लीक्स और वैक्यूम पाइप';
        if (l.contains('compression') || l.contains('timing')) return 'सिलेंडर कंप्रेशन और इंजन टाइमिंग';
        if (l.contains('thermostat')) return 'थर्मोस्टेट कार्यप्रणाली';
        if (l.contains('egr')) return 'ईजीआर वाल्व और ट्यूबों में कार्बन जमाव';
      } else if (lang == 'ta') {
        if (l.contains('spark plug')) return 'ஸ்பார்க் பிளக் மற்றும் இக்னிஷன் காயில்கள்';
        if (l.contains('fuel pressure')) return 'எரிபொருள் அழுத்தம் மற்றும் இன்ஜெக்டர்கள்';
        if (l.contains('intake air') || l.contains('vacuum')) return 'காற்று குழாய் கசிவுகள்';
        if (l.contains('compression')) return 'என்ஜின் அழுத்தம் மற்றும் டைமிங்';
        if (l.contains('headlamp') || l.contains('lens')) return 'விளக்கு மற்றும் கண்ணாடி நிலை';
        if (l.contains('windshield') || l.contains('crack')) return 'விரிசல் அளவு மற்றும் பரவல் ஆய்வு';
        if (l.contains('bumper')) return 'பம்பர் கிளிப்புகள் மற்றும் சென்சார்கள்';
        if (l.contains('tread depth') || l.contains('sidewall')) return 'டயர் தேய்மானம் மற்றும் வெட்டுக்கள்';
      } else if (lang == 'te') {
        if (l.contains('spark plug')) return 'స్పార్క్ ప్లగ్‌లు & ఇగ్నిషన్ కాయిల్స్';
        if (l.contains('fuel pressure')) return 'ఇంధన పీడనం & ఇంజెక్టర్లు';
        if (l.contains('intake air') || l.contains('vacuum')) return 'గాలి లీకులు & వాక్యూమ్ లైన్లు';
        if (l.contains('headlamp') || l.contains('lens')) return 'హెడ్‌లైట్ లెన్స్ మరియు వైరింగ్';
        if (l.contains('windshield')) return 'విండ్‌షీల్డ్ పగులు తీవ్రత';
        if (l.contains('bumper')) return 'బంపర్ మౌంటింగ్ మరియు సెన్సార్లు';
      }
      return c;
    }).toList();
  }

  static String getTechnicalDetails(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();
    if (lang == 'hi') {
      if (lower.contains('cmvr') || lower.contains('rule 105') || lower.contains('headlamp')) {
        return 'भारतीय केंद्रीय मोटर वाहन नियम (CMVR) नियम 105 पूरी तरह कार्यात्मक हेडलाइट्स अनिवार्य करता है। टूटे लेंस प्रकाश बीम को बिगाड़ते हैं।';
      }
      if (lower.contains('ais-040') || lower.contains('windshield') || lower.contains('roof crush')) {
        return 'AIS-040 और CMVR सुरक्षा नियम स्पष्ट दृष्टि अनिवार्य करते हैं। लेमिनेटेड विंडशील्ड वाहन की छत की संरचनात्मक मजबूती में 30% योगदान देती है।';
      }
      if (lower.contains('bumper') || lower.contains('energy-absorbing')) {
        return 'आधुनिक प्लास्टिक बम्पर के पीछे इम्पैक्ट बीम और क्रैश सेंसर होते हैं। दृश्य विकृति मध्यम होने पर भी आंतरिक सेंसर प्रभावित हो सकते हैं।';
      }
      if (lower.contains('underinflated') || lower.contains('flexing') || lower.contains('sidewall ply')) {
        return 'हवा कम होने पर बार-बार मुड़ने से टायर में अत्यधिक गर्मी पैदा होती है, जिससे साइडवॉल की परतें अलग होकर टायर फट सकता है।';
      }
      if (lower.contains('paint') || lower.contains('primer') || lower.contains('corrosion')) {
        return 'ऑटोमोटिव पेंट कई सुरक्षा परतों से बनता है। प्राइमर से नीचे जाने वाली खरोंच धातु को विद्युत-रासायनिक जंग के संपर्क में लाती है।';
      }
      if (lower.contains('p0300')) {
        final match = _guidanceTranslations[lang]?['P0300'];
        if (match != null && match['technical_details'] != null) return match['technical_details'] as String;
      }
      if (lower.contains('p0128')) {
        final match = _guidanceTranslations[lang]?['P0128'];
        if (match != null && match['technical_details'] != null) return match['technical_details'] as String;
      }
      if (lower.contains('p0401')) {
        final match = _guidanceTranslations[lang]?['P0401'];
        if (match != null && match['technical_details'] != null) return match['technical_details'] as String;
      }
    }
    return fallback;
  }

  // ---------------------------------------------------------------------------
  // 12. Repair Cost Estimation Localization
  // ---------------------------------------------------------------------------
  static String getEstimateTitle(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'वाहन मरम्मत एवं प्रतिस्थापन लागत अनुमान';
      case 'ta': return 'வாகன பழுது & மாற்றுச் செலவு மதிப்பீடு';
      case 'te': return 'వాహన మరమ్మతు & భర్తీ ఖర్చు అంచనా';
      case 'kn': return 'ವಾಹನ ದುರಸ್ತಿ ಮತ್ತು ಬದಲಿ ವೆಚ್ಚದ ಅಂದಾಜು';
      case 'bn': return 'যানবাহন মেরামত ও প্রতিস্থাপন খরচ অনুমান';
      case 'gu': return 'વાહન સમારકામ અને બદલવાનો ખર્ચ અંદાજ';
      case 'mr': return 'વાહન दुरुस्ती आणि बदलण्याचा खर्च अंदाज';
      default: return 'Vehicle Repair & Replacement Cost Estimate';
    }
  }

  static String getNoDamageNoEstimateNeeded(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'कोई क्षति नहीं मिली — किसी लागत अनुमान की आवश्यकता नहीं है।';
      case 'ta': return 'சேதம் எதுவும் கண்டறியப்படவில்லை — செலவு மதிப்பீடு தேவையில்லை.';
      case 'te': return 'ఎలాంటి నష్టం కనుగొనబడలేదు — ఖర్చు అంచనా అవసరం లేదు.';
      case 'kn': return 'ಯಾವುದೇ ಹಾನಿ ಕಂಡುಬಂದಿಲ್ಲ — ಯಾವುದೇ ವೆಚ್ಚದ ಅಂದಾಜು ಅಗತ್ಯವಿಲ್ಲ.';
      case 'bn': return 'কোন ক্ষতি সনাক্ত হয়নি — কোন খরচ অনুমানের প্রয়োজন নেই।';
      case 'gu': return 'કોઈ નુકસાન મળ્યું નથી — કોઈ ખર્ચ અંદાજની જરૂર નથી.';
      case 'mr': return 'कोणतेही नुकसान आढळले नाही — कोणत्याही खर्चाच्या अंदाजाची आवश्यकता नाही.';
      case 'pa': return 'ਕੋਈ ਨੁਕਸਾਨ ਨਹੀਂ ਮਿਲਿਆ — ਕਿਸੇ ਖਰਚੇ ਦੇ ਅੰਦਾਜ਼ੇ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।';
      case 'ml': return 'കേടുപാടുകളൊന്നും കണ്ടെത്തിയില്ല — ചെലവ് കണക്കാക്കേണ്ടതില്ല.';
      case 'or': return 'କୌଣସି କ୍ଷତି ମିଳିନାହିଁ — ଖର୍ଚ୍ଚ ଆକଳନ ଆବଶ୍ୟକ ନାହିଁ।';
      default: return 'No damage detected — no cost estimation is needed.';
    }
  }

  static String getScenarioRepairLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'विकल्प A: मरम्मत';
      case 'ta': return 'விருப்பம் A: பழுது';
      case 'te': return 'ఎంపిక A: మరమ్మతు';
      default: return 'Scenario A: Repair';
    }
  }

  static String getScenarioReplaceLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'विकल्प B: प्रतिस्थापन';
      case 'ta': return 'விருப்பம் B: மாற்றுதல்';
      case 'te': return 'ఎంపిక B: భర్తీ';
      default: return 'Scenario B: Replace';
    }
  }

  static String getRecommendedBadge(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'अनुशंसित विकल्प';
      case 'ta': return 'பரிந்துரைக்கப்பட்ட தேர்வு';
      case 'te': return 'సిఫార్సు చేయబడిన ఎంపిక';
      default: return 'RECOMMENDED OPTION';
    }
  }

  static String getExpectedCostLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'अपेक्षित कुल लागत (जीएसटी 18% सहित)';
      case 'ta': return 'எதிர்பார்க்கப்படும் மொத்த செலவு (18% ஜிஎஸ்டி உட்பட)';
      case 'te': return 'అంచనా వేసిన మొత్తం ఖర్చు (18% జీఎస్టీతో)';
      default: return 'Expected Total Cost (GST 18% Included)';
    }
  }

  static String getCostRangeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'संभावित लागत सीमा (न्यूनतम – अधिकतम)';
      case 'ta': return 'மதிப்பிடப்பட்ட வரம்பு (குறைந்தபட்சம் – அதிகபட்சம்)';
      case 'te': return 'అంచనా పరిధి (కనిష్ట – గరిష్ట)';
      default: return 'Estimated Range (Min – Max)';
    }
  }

  static String getItemizedBreakdownLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मद-वार लागत विवरण';
      case 'ta': return 'உருப்படி வாரியான செலவு விவரம்';
      case 'te': return 'వస్తువుల వారీగా ఖర్చుల వివరాలు';
      default: return 'Itemized Cost Breakdown';
    }
  }

  static String getSourcesProvenanceLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सत्यापित ऑनलाइन पार्ट्स स्रोत (भारत)';
      case 'ta': return 'சரிபார்க்கப்பட்ட ஆன்லைன் பாகங்கள் மூலங்கள்';
      case 'te': return 'ధృవీకరించబడిన ఆన్‌లైన్ విడిభాగాల వనరులు';
      default: return 'Verified Online Part Sources (India)';
    }
  }

  static String getConfirmComponentButton(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'पुर्जे की पुष्टि / परिवर्तन करें';
      case 'ta': return 'பாகத்தை உறுதிசெய் / திருத்து';
      case 'te': return 'భాగాన్ని నిర్ధారించండి / సవరించండి';
      default: return 'Confirm / Edit Component';
    }
  }

  static String getRefreshPricingButton(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'ताज़ा बाज़ार मूल्य प्राप्त करें';
      case 'ta': return 'சந்தை விலையைப் புதுப்பிக்கவும்';
      case 'te': return 'తాజా మార్కెట్ ధరలను పొందండి';
      default: return 'Refresh Live Market Prices';
    }
  }

  static String getIndicativeDisclaimer(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सूचना: यह अनुमान दृश्य क्षति और भारतीय बाज़ार पार्ट्स कैटलॉग पर आधारित है। आंतरिक दोषों के लिए गैरेज जांच आवश्यक है। सड़क योग्यता मूल्यांकन वित्तीय निर्णयों से स्वतंत्र है।';
      case 'ta': return 'அறிவிப்பு: இந்த மதிப்பீடு பார்வைக்குத் தெரியும் சேதம் மற்றும் இந்திய சந்தை பாகங்கள் பட்டியலை அடிப்படையாகக் கொண்டது. சாலைத்தகுதி மதிப்பீடு பழுதுபார்க்கும் செலவிலிருந்து சுயாதீனமானது.';
      case 'te': return 'గమనిక: ఈ అంచనా కనిపించే నష్టం మరియు భారతీయ మార్కెట్ భాగాల కేటలాగ్‌లపై ఆధారపడి ఉంటుంది. రోడ్‌వర్తినెస్ భద్రతా నియమాలు మరమ్మతు ఖర్చుల నుండి స్వతంత్రంగా ఉంటాయి.';
      default: return 'Notice: Indicative estimate for bodyshop planning based on active Indian online parts catalogues. Concealed internal defects require physical workshop inspection. Safety rules remain independent of repair costs.';
    }
  }

  static String getCategoryName(String category, String langCode) {
    final cat = category.toLowerCase();
    switch (_norm(langCode)) {
      case 'hi':
        if (cat == 'part') return 'नया पुर्जा';
        if (cat == 'labour') return 'बॉडीशॉप श्रम';
        if (cat == 'painting') return 'पेंट एवं रीफ़िनिश';
        if (cat == 'materials') return 'सामग्री एवं उपभोग्य';
        if (cat == 'taxes') return 'कर (जीएसटी 18%)';
        if (cat == 'shipping') return 'शिपिंग / डिलीवरी';
        return category.toUpperCase();
      case 'ta':
        if (cat == 'part') return 'புதிய பாகம்';
        if (cat == 'labour') return 'பழுதுபார்க்கும் கூலி';
        if (cat == 'painting') return 'வண்ணப்பூச்சு';
        if (cat == 'materials') return 'பொருட்கள்';
        if (cat == 'taxes') return 'வரி (18% ஜிஎஸ்டி)';
        if (cat == 'shipping') return 'டெலிவரி கட்டணம்';
        return category.toUpperCase();
      default:
        return category.toUpperCase();
    }
  }

  static String getExtentName(String extent, String langCode) {
    switch (_norm(langCode)) {
      case 'hi':
        if (extent == 'minor') return 'मामूली (Minor)';
        if (extent == 'moderate') return 'मध्यम (Moderate)';
        if (extent == 'extensive') return 'व्यापक (Extensive)';
        return extent;
      case 'ta':
        if (extent == 'minor') return 'குறைந்தளவு (Minor)';
        if (extent == 'moderate') return 'மிதமான (Moderate)';
        if (extent == 'extensive') return 'அதிகளவு (Extensive)';
        return extent;
      default:
        return extent[0].toUpperCase() + extent.substring(1);
    }
  }
}
