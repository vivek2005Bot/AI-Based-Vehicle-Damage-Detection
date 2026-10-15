import 'package:flutter_test/flutter_test.dart';
import 'package:vehicle_damage_ai/main.dart';
import 'package:vehicle_damage_ai/features/splash/splash_screen.dart';

void main() {
  testWidgets('App smoke test - mounts VehicleDamageInspectionApp and shows Splash', (WidgetTester tester) async {
    await tester.pumpWidget(const VehicleDamageInspectionApp());
    expect(find.byType(SplashScreen), findsOneWidget);
    expect(find.text('Vehicle Damage AI'), findsOneWidget);
  });
}
