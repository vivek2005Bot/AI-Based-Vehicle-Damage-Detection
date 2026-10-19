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
      default: return 'What you might notice (may or may not occur):';
    }
  }

  static String getPossibleCausesLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'संभावित कारण / जांच के क्षेत्र:';
      case 'ta': return 'சாத்தியமான காரணங்கள் / சரிபார்க்க வேண்டிய பகுதிகள்:';
      case 'te': return 'సాధ్యమయ్యే కారణాలు / తనిఖీ చేయవలసిన ప్రాంతాలు:';
      default: return 'Possible causes / areas to check:';
    }
  }

  static String getNoticeLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सूचना: ';
      case 'ta': return 'அறிவிப்பு: ';
      case 'te': return 'గమనిక: ';
      default: return 'Notice: ';
    }
  }

  static String getStandardDefinitionLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'मानक परिभाषा: ';
      case 'ta': return 'நிலையான வரையறை: ';
      case 'te': return 'ప్రామాణిక నిర్వచనం: ';
      default: return 'Standard definition: ';
    }
  }

  static String getVerifiedSourceLabel(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'सत्यापित स्रोत: ';
      case 'ta': return 'சரிபார்க்கப்பட்ட ஆதாரம்: ';
      case 'te': return 'ధృవీకరించబడిన మూలం: ';
      default: return 'Verified Source: ';
    }
  }

  static String getNoObdTelemetryText(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'इस निरीक्षण के साथ कोई OBD-II टेलीमेट्री लॉग अपलोड नहीं किया गया था। पावरट्रेन और इलेक्ट्रॉनिक सबसिस्टम के स्वास्थ्य का मूल्यांकन नहीं किया गया था।';
      case 'ta': return 'இந்த ஆய்வில் OBD-II டெலிமெட்ரி பதிவு பதிவேற்றப்படவில்லை. எஞ்சின் மற்றும் மின்னணு பாகங்களின் நிலை மதிப்பீடு செய்யப்படவில்லை.';
      case 'te': return 'ఈ తనిఖీతో OBD-II టెలిమెట్రీ లాగ్ అప్‌లోడ్ చేయబడలేదు.';
      default: return 'No OBD-II telemetry log was uploaded with this inspection. Powertrain and electronic subsystem health was not evaluated.';
    }
  }

  static String getNoGuidanceText(String langCode) {
    switch (_norm(langCode)) {
      case 'hi': return 'कॉन्फ़िगर किए गए ज्ञानकोष में कोई सत्यापित मरम्मत मार्गदर्शन नहीं मिला।';
      case 'ta': return 'வழங்கப்பட்ட தரவுத்தளத்தில் சரிபார்க்கப்பட்ட பழுதுபார்ப்பு வழிகாட்டுதல் எதுவும் கிடைக்கவில்லை.';
      case 'te': return 'నాలెడ్జ్ బేస్‌లో ధృవీకరించబడిన మరమ్మతు మార్గదర్శకత్వం కనుగొనబడలేదు.';
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

  static String getGuidanceTitle(String keyOrDtc, String fallback, String langCode) {
    final lang = _norm(langCode);
    for (final code in ['P0300', 'P0128', 'P0401', 'P0171', 'P0420']) {
      if (fallback.toUpperCase().contains(code) || keyOrDtc.toUpperCase().contains(code)) {
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
      if (lower.contains('stop in a safe place')) return 'तुरंत सुरक्षित स्थान पर रुकें और सहायता लें।';
      if (lower.contains('avoid unnecessary')) return 'अनावश्यक ड्राइविंग से बचें; जल्द निरीक्षण करवाएं।';
      if (lower.contains('arrange a mechanic') || lower.contains('appointment')) return 'शीघ्र मैकेनिक से अपॉइंटमेंट लें।';
      if (lower.contains('no immediate action')) return 'तत्काल कार्रवाई की आवश्यकता नहीं। वाहन सुरक्षित है।';
    } else if (lang == 'ta') {
      if (lower.contains('stop in a safe place')) return 'உடனடியாக பாதுகாப்பான இடத்தில் வாகனத்தை நிறுத்துங்கள்.';
      if (lower.contains('avoid unnecessary')) return 'தேவையற்ற பயணங்களைத் தவிர்க்கவும்; பரிசோதிக்கவும்.';
      if (lower.contains('arrange a mechanic') || lower.contains('appointment')) return 'விரைவில் மெக்கானிக்கிடம் செல்லவும்.';
      if (lower.contains('no immediate action')) return 'உடனடி நடவடிக்கை தேவையில்லை. பாதுகாப்பானது.';
    } else if (lang == 'te') {
      if (lower.contains('stop in a safe place')) return 'వెంటనే సురక్షిత ప్రదేశంలో ఆపండి.';
      if (lower.contains('avoid unnecessary')) return 'అనవసరంగా డ్రైవ్ చేయకండి; త్వరగా తనిఖీ చేయించండి.';
      if (lower.contains('arrange a mechanic') || lower.contains('appointment')) return 'త్వరలో మెకానిక్‌ను సంప్రదించండి.';
      if (lower.contains('no immediate action')) return 'వెంటనే చర్య అవసరం లేదు. సురక్షితం.';
    }
    return fallback;
  }

  static List<String> getMechanicChecks(List<String> originalChecks, String langCode) {
    final lang = _norm(langCode);
    if (lang == 'hi') {
      return originalChecks.map((c) {
        final l = c.toLowerCase();
        if (l.contains('spark plug')) return 'स्पार्क प्लग और इग्निशन कॉइल';
        if (l.contains('fuel pressure')) return 'ईंधन दबाव और फ्यूल इंजेक्टर';
        if (l.contains('intake air') || l.contains('vacuum')) return 'इंटेक एयर लीक्स और वैक्यूम पाइप';
        if (l.contains('compression')) return 'सिलेंडर कंप्रेशन और इंजन टाइमिंग';
        if (l.contains('thermostat')) return 'थर्मोस्टेट कार्यप्रणाली';
        if (l.contains('egr')) return 'ईजीआर वाल्व और ट्यूबों में कार्बन जमाव';
        return c;
      }).toList();
    } else if (lang == 'ta') {
      return originalChecks.map((c) {
        final l = c.toLowerCase();
        if (l.contains('spark plug')) return 'ஸ்பார்க் பிளக் மற்றும் இக்னிஷன் காயில்கள்';
        if (l.contains('fuel pressure')) return 'எரிபொருள் அழுத்தம் மற்றும் இன்ஜெக்டர்கள்';
        if (l.contains('intake air') || l.contains('vacuum')) return 'காற்று குழாய் கசிவுகள்';
        if (l.contains('compression')) return 'என்ஜின் அழுத்தம் மற்றும் டைமிங்';
        return c;
      }).toList();
    } else if (lang == 'te') {
      return originalChecks.map((c) {
        final l = c.toLowerCase();
        if (l.contains('spark plug')) return 'స్పార్క్ ప్లగ్‌లు & ఇగ్నిషన్ కాయిల్స్';
        if (l.contains('fuel pressure')) return 'ఇంధన పీడనం & ఇంజెక్టర్లు';
        if (l.contains('intake air') || l.contains('vacuum')) return 'గాలి లీకులు & వాక్యూమ్ లైన్లు';
        if (l.contains('compression')) return 'సిలిండర్ కంప్రెషన్ & టైమింగ్';
        return c;
      }).toList();
    }
    return originalChecks;
  }

  static String getTechnicalDetails(String fallback, String langCode) {
    final lang = _norm(langCode);
    final lower = fallback.toLowerCase();
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
      case 'mr': return 'वाहन दुरुस्ती आणि बदलण्याचा खर्च अंदाज';
      default: return 'Vehicle Repair & Replacement Cost Estimate';
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
