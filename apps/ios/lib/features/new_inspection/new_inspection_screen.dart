import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import '../progress/analysis_progress_screen.dart';

class NewInspectionScreen extends StatefulWidget {
  const NewInspectionScreen({super.key});

  @override
  State<NewInspectionScreen> createState() => _NewInspectionScreenState();
}

class _NewInspectionScreenState extends State<NewInspectionScreen> {
  int _currentStep = 0;
  final ImagePicker _picker = ImagePicker();

  // Form Fields
  final _makeController = TextEditingController(text: 'BMW');
  final _modelController = TextEditingController(text: '330i');
  final _yearController = TextEditingController(text: '2021');
  final _mileageController = TextEditingController(text: '35420');
  final _vinController = TextEditingController();

  // Selected Assets
  final List<File> _selectedImages = [];
  File? _selectedObdCsv;
  String? _obdFileName;
  int? _obdFileSize;

  bool _isSubmitting = false;
  String _submitProgressText = '';
  String? _errorMessage;

  @override
  void dispose() {
    _makeController.dispose();
    _modelController.dispose();
    _yearController.dispose();
    _mileageController.dispose();
    _vinController.dispose();
    super.dispose();
  }

  // --- Image Handling ---

  Future<void> _pickImage(ImageSource source) async {
    try {
      if (source == ImageSource.camera) {
        final photo = await _picker.pickImage(source: ImageSource.camera, imageQuality: 90);
        if (photo != null && !_containsPath(photo.path)) {
          setState(() => _selectedImages.add(File(photo.path)));
        }
      } else {
        final picked = await _picker.pickMultiImage(imageQuality: 90);
        final newFiles = picked
            .map((x) => File(x.path))
            .where((f) => !_containsPath(f.path))
            .toList();
        if (newFiles.isNotEmpty) {
          setState(() => _selectedImages.addAll(newFiles));
        }
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error accessing camera or photos: $e')),
      );
    }
  }

  /// Guards against the same file being added twice (repeat selection).
  bool _containsPath(String path) => _selectedImages.any((f) => f.path == path);

  void _removeImage(int index) {
    setState(() => _selectedImages.removeAt(index));
  }

  // --- OBD CSV Handling ---

  Future<void> _pickObdCsv() async {
    try {
      final pickedFiles = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
      );

      if (pickedFiles.isNotEmpty) {
        final platformFile = pickedFiles.first;
        final path = platformFile.path;
        if (path != null) {
          final file = File(path);
          final size = await file.length();
          setState(() {
            _selectedObdCsv = file;
            _obdFileName = platformFile.name;
            _obdFileSize = size;
          });
        }
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error selecting CSV: $e')),
      );
    }
  }

  void _removeObdCsv() {
    setState(() {
      _selectedObdCsv = null;
      _obdFileName = null;
      _obdFileSize = null;
    });
  }

  // --- Submission ---

  Future<void> _submitInspection() async {
    if (_isSubmitting) return; // guard against double-tap duplicate submissions
    if (_selectedImages.isEmpty) {
      setState(() => _errorMessage = 'Please capture or select at least 1 vehicle image.');
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _submitProgressText = 'Creating draft inspection...';
    });

    try {
      final year = int.tryParse(_yearController.text.trim());
      final mileage = double.tryParse(_mileageController.text.trim());

      final inspection = await ApiClient.createInspection(
        make: _makeController.text.trim().isEmpty ? null : _makeController.text.trim(),
        model: _modelController.text.trim().isEmpty ? null : _modelController.text.trim(),
        year: year,
        mileage: mileage,
        vin: _vinController.text.trim().isEmpty ? null : _vinController.text.trim(),
      );

      setState(() => _submitProgressText = 'Uploading vehicle images (${_selectedImages.length})...');
      await ApiClient.uploadImages(inspection.id, _selectedImages);

      if (_selectedObdCsv != null) {
        setState(() => _submitProgressText = 'Uploading OBD-II telemetry CSV...');
        await ApiClient.uploadObdCsv(inspection.id, _selectedObdCsv!);
      }

      setState(() => _submitProgressText = 'Queueing AI analysis pipeline...');
      await ApiClient.triggerAnalysis(inspection.id);

      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => AnalysisProgressScreen(inspectionId: inspection.id),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSubmitting = false;
        _errorMessage = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Vehicle Inspection'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Step Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              color: Colors.white,
              child: Row(
                children: [
                  _buildStepIndicator(0, 'Vehicle'),
                  _buildStepDivider(),
                  _buildStepIndicator(1, 'Photos'),
                  _buildStepDivider(),
                  _buildStepIndicator(2, 'OBD-II'),
                  _buildStepDivider(),
                  _buildStepIndicator(3, 'Review'),
                ],
              ),
            ),
            const Divider(height: 1, color: AppTheme.borderSubtle),

            if (_errorMessage != null)
              Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.unsafeRed.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.unsafeRed.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: AppTheme.unsafeRed, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(_errorMessage!, style: const TextStyle(color: AppTheme.unsafeRed, fontSize: 13)),
                    ),
                  ],
                ),
              ),

            // Step Content
            Expanded(
              child: IndexedStack(
                index: _currentStep,
                children: [
                  _buildVehicleInfoStep(),
                  _buildImageCaptureStep(),
                  _buildObdUploadStep(),
                  _buildReviewSubmitStep(),
                ],
              ),
            ),

            // Bottom Navigation Buttons
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: AppTheme.borderSubtle)),
              ),
              child: Row(
                children: [
                  if (_currentStep > 0) ...[
                    Expanded(
                      flex: 1,
                      child: OutlinedButton(
                        onPressed: _isSubmitting ? null : () => setState(() => _currentStep--),
                        child: const Text('Back'),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: _isSubmitting
                          ? null
                          : () {
                              if (_currentStep < 3) {
                                setState(() {
                                  _errorMessage = null;
                                  _currentStep++;
                                });
                              } else {
                                _submitInspection();
                              }
                            },
                      child: _isSubmitting
                          ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                ),
                                const SizedBox(width: 10),
                                Text(_submitProgressText, style: const TextStyle(fontSize: 13)),
                              ],
                            )
                          : Text(_currentStep == 3 ? 'Submit for Analysis' : 'Next Step'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepIndicator(int stepIndex, String title) {
    final isActive = _currentStep == stepIndex;
    final isDone = _currentStep > stepIndex;

    return Expanded(
      child: Column(
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: isDone
                ? AppTheme.safeGreen
                : (isActive ? AppTheme.primaryCobalt : AppTheme.borderSubtle),
            child: isDone
                ? const Icon(Icons.check, size: 14, color: Colors.white)
                : Text(
                    '${stepIndex + 1}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: isActive ? Colors.white : AppTheme.textMuted,
                    ),
                  ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 11,
              fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
              color: isActive ? AppTheme.primaryDark : AppTheme.textMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepDivider() {
    return Container(
      width: 16,
      height: 1,
      color: AppTheme.borderSubtle,
      margin: const EdgeInsets.only(bottom: 16),
    );
  }

  // --- Step 1: Vehicle Info ---
  Widget _buildVehicleInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Vehicle Information (Optional)',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 6),
          const Text(
            'Vehicle details improve RAG manual retrieval and contextual risk classification.',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _makeController,
                  decoration: const InputDecoration(labelText: 'Make', hintText: 'e.g. BMW, Toyota'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _modelController,
                  decoration: const InputDecoration(labelText: 'Model', hintText: 'e.g. 330i, Camry'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _yearController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Year', hintText: 'e.g. 2021'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _mileageController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Mileage (km)', hintText: 'e.g. 35000'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _vinController,
            decoration: const InputDecoration(
              labelText: 'VIN (Optional, Masked)',
              hintText: '17-character VIN',
              prefixIcon: Icon(Icons.security_outlined, color: AppTheme.textMuted),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Note: VIN numbers are masked automatically upon receipt to protect vehicle privacy.',
            style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontStyle: FontStyle.italic),
          ),
        ],
      ),
    );
  }

  // --- Step 2: Multi-Angle Image Capture ---
  Widget _buildImageCaptureStep() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Vehicle Photos',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _selectedImages.isEmpty ? Colors.grey.shade200 : AppTheme.primaryCobalt.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${_selectedImages.length} photo(s) selected',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: _selectedImages.isEmpty ? AppTheme.textMuted : AppTheme.primaryCobalt,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Capture or select multiple angles (front, rear, quarter-panels, close-ups of damage).',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pickImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt, size: 18),
                  label: const Text('Camera'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryDark,
                    minimumSize: const Size.fromHeight(46),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => _pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library_outlined, size: 18),
                  label: const Text('Photo Library'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(46),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _selectedImages.isEmpty
                ? Container(
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceLight,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.borderSubtle, style: BorderStyle.solid),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo_outlined, size: 48, color: AppTheme.textMuted.withValues(alpha: 0.4)),
                          const SizedBox(height: 12),
                          const Text(
                            'No images selected yet',
                            style: TextStyle(color: AppTheme.textMuted, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Take a photo or choose from library',
                            style: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  )
                : GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 3,
                      crossAxisSpacing: 10,
                      mainAxisSpacing: 10,
                    ),
                    itemCount: _selectedImages.length,
                    itemBuilder: (context, index) {
                      final imgFile = _selectedImages[index];
                      return Stack(
                        fit: StackFit.expand,
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.file(imgFile, fit: BoxFit.cover),
                          ),
                          Positioned(
                            top: 4,
                            right: 4,
                            child: GestureDetector(
                              onTap: () => _removeImage(index),
                              child: Container(
                                padding: const EdgeInsets.all(4),
                                decoration: const BoxDecoration(
                                  color: Colors.black54,
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.close, size: 14, color: Colors.white),
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  // --- Step 3: OBD-II CSV Upload ---
  Widget _buildObdUploadStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'OBD-II Telemetry (Optional)',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 6),
          const Text(
            'Upload an existing vehicle PID CSV file. Telemetry helps detect hidden engine overheating, cylinder misfires, and active DTC fault codes.',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
          ),
          const SizedBox(height: 24),
          if (_selectedObdCsv == null)
            GestureDetector(
              onTap: _pickObdCsv,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceLight,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.primaryCobalt.withValues(alpha: 0.4), width: 1.5),
                ),
                child: Column(
                  children: [
                    Icon(Icons.upload_file_rounded, size: 52, color: AppTheme.primaryCobalt),
                    const SizedBox(height: 12),
                    const Text(
                      'Select OBD-II Telemetry CSV',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Tap to browse files (Seat Leon format or generic OBD-II PID logs)',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
            )
          else
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.safeGreen.withValues(alpha: 0.5)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: AppTheme.safeGreen.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.table_chart_rounded, color: AppTheme.safeGreen, size: 26),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _obdFileName ?? 'telemetry.csv',
                          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Size: ${((_obdFileSize ?? 0) / 1024).toStringAsFixed(1)} KB • Ready for analysis',
                          style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppTheme.unsafeRed),
                    onPressed: _removeObdCsv,
                  ),
                ],
              ),
            ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceLight,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: AppTheme.primaryCobalt, size: 20),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    'No live OBD dongle connection required. This release processes standard offline CSV time series logs.',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // --- Step 4: Review and Submit ---
  Widget _buildReviewSubmitStep() {
    final vehicleTitle = [
      _yearController.text.trim(),
      _makeController.text.trim(),
      _modelController.text.trim()
    ].where((s) => s.isNotEmpty).join(' ');

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Review Inspection Package',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 6),
          const Text(
            'Verify all attached vehicle data before dispatching the asynchronous agent pipeline.',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  _buildReviewRow('Vehicle', vehicleTitle.isEmpty ? 'Not specified' : vehicleTitle),
                  const Divider(color: AppTheme.borderSubtle, height: 18),
                  _buildReviewRow('Mileage', '${_mileageController.text.trim()} km'),
                  const Divider(color: AppTheme.borderSubtle, height: 18),
                  _buildReviewRow('Photos Attached', '${_selectedImages.length} image(s)'),
                  const Divider(color: AppTheme.borderSubtle, height: 18),
                  _buildReviewRow(
                    'OBD-II Telemetry',
                    _selectedObdCsv != null ? _obdFileName! : 'None (Exterior only)',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceLight,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.shield_outlined, color: AppTheme.primaryCobalt, size: 20),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Our 4-stage pipeline evaluates damaged vs intact panels, localizes bounding boxes, computes severity ratios, and fuses with telemetry for a grounded risk report.',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReviewRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 13)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: AppTheme.primaryDark)),
      ],
    );
  }
}
