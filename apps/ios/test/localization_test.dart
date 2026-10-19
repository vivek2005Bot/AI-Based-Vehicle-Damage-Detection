import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vehicle_damage_ai/core/localization/language_selector_widget.dart';
import 'package:vehicle_damage_ai/core/localization/locale_service.dart';
import 'package:vehicle_damage_ai/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LocaleService Unit & Widget Tests', () {
    test('Contains English and all 22 Scheduled Indian Languages (23 total)', () {
      expect(LocaleService.supportedLanguages.length, 23);

      final codes = LocaleService.supportedLanguages.map((l) => l.code).toSet();
      final requiredCodes = {
        'en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'gu', 'pa', 'or', 'as',
        'ur', 'sa', 'ks', 'kok', 'mni', 'ne', 'sd', 'doi', 'mai', 'brx', 'sat'
      };
      expect(codes, containsAll(requiredCodes));
    });

    test('RTL is correctly identified for Urdu, Kashmiri, and Sindhi', () {
      expect(LocaleService.isRtl('ur'), isTrue);
      expect(LocaleService.isRtl('ks'), isTrue);
      expect(LocaleService.isRtl('sd'), isTrue);
      expect(LocaleService.isRtl('en'), isFalse);
      expect(LocaleService.isRtl('hi'), isFalse);
      expect(LocaleService.isRtl('ta'), isFalse);
    });

    testWidgets('LanguageSelectorWidget renders and opens modal with all 23 languages', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: const LanguageSelectorWidget(),
            ),
          ),
        ),
      );

      // Verify the widget button is present
      expect(find.byType(LanguageSelectorWidget), findsOneWidget);

      // Tap to open bottom sheet
      await tester.tap(find.byType(LanguageSelectorWidget));
      await tester.pumpAndSettle();

      // Check modal title
      expect(find.text('Select Language / भाषा चुनें'), findsOneWidget);

      // Verify native names are present
      expect(find.text('English'), findsWidgets);
      expect(find.text('हिन्दी'), findsOneWidget);
      expect(find.text('தமிழ்'), findsOneWidget);

      // Scroll list to verify languages further down
      await tester.scrollUntilVisible(find.text('বাংলা'), 100);
      expect(find.text('বাংলা'), findsOneWidget);
    });

    testWidgets('App starts and mounts with supportedLocales', (tester) async {
      await tester.pumpWidget(const VehicleDamageInspectionApp());
      await tester.pump();
      expect(find.byType(VehicleDamageInspectionApp), findsOneWidget);
    });
  });
}
