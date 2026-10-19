import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AppLanguage {
  final String code;
  final String name;
  final String nativeName;
  final bool isRtl;

  const AppLanguage({
    required this.code,
    required this.name,
    required this.nativeName,
    this.isRtl = false,
  });

  Locale get locale => Locale(code);
}

class LocaleService {
  static const String _storageKeyLocale = 'app_selected_locale';
  static final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const List<AppLanguage> supportedLanguages = [
    AppLanguage(code: 'en', name: 'English', nativeName: 'English'),
    AppLanguage(code: 'hi', name: 'Hindi', nativeName: 'हिन्दी'),
    AppLanguage(code: 'ta', name: 'Tamil', nativeName: 'தமிழ்'),
    AppLanguage(code: 'te', name: 'Telugu', nativeName: 'తెలుగు'),
    AppLanguage(code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ'),
    AppLanguage(code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം'),
    AppLanguage(code: 'bn', name: 'Bengali', nativeName: 'বাংলা'),
    AppLanguage(code: 'mr', name: 'Marathi', nativeName: 'मराठी'),
    AppLanguage(code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી'),
    AppLanguage(code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ'),
    AppLanguage(code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ'),
    AppLanguage(code: 'as', name: 'Assamese', nativeName: 'অসমীয়া'),
    AppLanguage(code: 'ur', name: 'Urdu', nativeName: 'اردو', isRtl: true),
    AppLanguage(code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्'),
    AppLanguage(code: 'ks', name: 'Kashmiri', nativeName: 'کٲشُر', isRtl: true),
    AppLanguage(code: 'kok', name: 'Konkani', nativeName: 'कोंकणी'),
    AppLanguage(code: 'mni', name: 'Manipuri / Meitei', nativeName: 'মেইতেই'),
    AppLanguage(code: 'ne', name: 'Nepali', nativeName: 'नेपाली'),
    AppLanguage(code: 'sd', name: 'Sindhi', nativeName: 'سنڌي', isRtl: true),
    AppLanguage(code: 'doi', name: 'Dogri', nativeName: 'डोगरी'),
    AppLanguage(code: 'mai', name: 'Maithili', nativeName: 'मैथिली'),
    AppLanguage(code: 'brx', name: 'Bodo', nativeName: 'बड़ो'),
    AppLanguage(code: 'sat', name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ'),
  ];

  static final ValueNotifier<Locale> currentLocaleNotifier = ValueNotifier<Locale>(const Locale('en'));

  static Locale get currentLocale => currentLocaleNotifier.value;
  static String get currentLanguageCode => currentLocale.languageCode;

  static AppLanguage get currentLanguage {
    return supportedLanguages.firstWhere(
      (lang) => lang.code == currentLocale.languageCode,
      orElse: () => supportedLanguages.first,
    );
  }

  static bool get isCurrentRtl => currentLanguage.isRtl;

  static bool isRtl(String code) =>
      supportedLanguages.firstWhere((lang) => lang.code == code, orElse: () => supportedLanguages.first).isRtl;

  static Future<void> initialize() async {
    try {
      final savedCode = await _storage.read(key: _storageKeyLocale);
      if (savedCode != null && savedCode.isNotEmpty) {
        final matched = supportedLanguages.any((lang) => lang.code == savedCode);
        if (matched) {
          currentLocaleNotifier.value = Locale(savedCode);
          return;
        }
      }
    } catch (_) {}
    currentLocaleNotifier.value = const Locale('en');
  }

  static Future<void> setLocale(Locale newLocale) async {
    final matched = supportedLanguages.any((lang) => lang.code == newLocale.languageCode);
    final target = matched ? newLocale : const Locale('en');

    currentLocaleNotifier.value = target;
    try {
      await _storage.write(key: _storageKeyLocale, value: target.languageCode);
    } catch (_) {}
  }

  static Future<void> setLanguageByCode(String code) async {
    await setLocale(Locale(code));
  }
}

/// Fallback localizations delegate ensuring widgets requiring Material/Cupertino
/// localizations gracefully fallback to English when Flutter SDK lacks built-in
/// support for specialty regional locales (e.g. Sanskrit, Santali, Dogri).
class FallbackMaterialLocalizationsDelegate extends LocalizationsDelegate<MaterialLocalizations> {
  const FallbackMaterialLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => true;

  @override
  Future<MaterialLocalizations> load(Locale locale) async {
    try {
      return await GlobalMaterialLocalizations.delegate.load(locale);
    } catch (_) {
      return await GlobalMaterialLocalizations.delegate.load(const Locale('en'));
    }
  }

  @override
  bool shouldReload(FallbackMaterialLocalizationsDelegate old) => false;
}

class FallbackCupertinoLocalizationsDelegate extends LocalizationsDelegate<CupertinoLocalizations> {
  const FallbackCupertinoLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => true;

  @override
  Future<CupertinoLocalizations> load(Locale locale) async {
    try {
      return await GlobalCupertinoLocalizations.delegate.load(locale);
    } catch (_) {
      return await GlobalCupertinoLocalizations.delegate.load(const Locale('en'));
    }
  }

  @override
  bool shouldReload(FallbackCupertinoLocalizationsDelegate old) => false;
}
