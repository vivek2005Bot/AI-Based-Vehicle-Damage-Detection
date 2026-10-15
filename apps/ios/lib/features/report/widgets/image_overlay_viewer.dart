import 'package:flutter/material.dart';
import '../../../core/models/inspection_model.dart';
import '../../../core/models/report_model.dart';
import '../../../core/networking/api_client.dart';

class ImageOverlayViewer extends StatefulWidget {
  final String inspectionId;
  final ImageFindingModel finding;
  final List<InspectionFileModel> inspectionFiles;

  const ImageOverlayViewer(
      {super.key, required this.inspectionId, required this.finding, this.inspectionFiles = const []});

  @override
  State<ImageOverlayViewer> createState() => _ImageOverlayViewerState();
}

class _ImageOverlayViewerState extends State<ImageOverlayViewer> {
  bool _showBoxes = true;
  bool _showMasks = true;
  ImageProvider? _photo;
  bool _photoLoading = true;
  String? _photoError;

  Color _getClassColor(String label) {
    switch (label.toLowerCase()) {
      case 'bumper_smash':
        return Colors.redAccent;
      case 'glass_crack':
        return Colors.purpleAccent;
      case 'flat_tire':
        return Colors.deepOrangeAccent;
      case 'broken_light':
        return Colors.amber;
      case 'dent':
        return Colors.blueAccent;
      case 'scratch':
      default:
        return Colors.cyan;
    }
  }

  @override
  void initState() {
    super.initState();
    _loadPhoto();
  }

  @override
  void didUpdateWidget(covariant ImageOverlayViewer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.finding.imageId != widget.finding.imageId ||
        oldWidget.finding.fileId != widget.finding.fileId ||
        oldWidget.finding.filename != widget.finding.filename ||
        oldWidget.inspectionId != widget.inspectionId ||
        oldWidget.inspectionFiles.length != widget.inspectionFiles.length) {
      _loadPhoto();
    }
  }

  /// Resolve the exact uploaded file for this finding.
  /// Priority: report file_id -> filename match in inspection files -> image_url.
  InspectionFileModel? _resolveFile() {
    final f = widget.finding;
    final images = widget.inspectionFiles.where((e) => e.role == 'vehicle_image').toList();
    if (images.isEmpty) return null;
    if (f.fileId != null && f.fileId!.isNotEmpty) {
      for (final e in images) {
        if (e.id == f.fileId) return e;
      }
    }
    // Fallback for reports generated before file_id was stored: match filename.
    final name = f.filename.trim().toLowerCase();
    if (name.isNotEmpty) {
      for (final e in images) {
        if (e.originalFilename.trim().toLowerCase() == name) return e;
      }
      // image_picker names may be truncated in UI but full in backend; match prefix.
      final stem = name.split('.').first;
      if (stem.length >= 8) {
        for (final e in images) {
          if (e.originalFilename.toLowerCase().startsWith(stem.substring(0, 8))) return e;
        }
      }
    }
    // Last resort: single-image inspection -> that image.
    if (images.length == 1) return images.first;
    return null;
  }

  void _retryPhoto() => _loadPhoto();

  Future<void> _loadPhoto() async {
    final resolved = _resolveFile();
    // If file list not yet loaded, wait for parent to pass it (no car icon fallback).
    if (resolved == null && widget.inspectionFiles.isEmpty) {
      if (!mounted) return;
      setState(() {
        _photoLoading = true;
        _photoError = null;
      });
      return;
    }
    final fileId = resolved?.id ?? widget.finding.fileId;
    if (fileId == null || fileId.isEmpty) {
      if (!mounted) return;
      setState(() {
        _photo = null;
        _photoLoading = false;
        _photoError = 'Image unavailable for ${widget.finding.filename}';
      });
      return;
    }
    if (!mounted) return;
    setState(() {
      _photoLoading = true;
      _photoError = null;
    });
    try {
      final bytes = await ApiClient.getInspectionImageBytes(widget.inspectionId, fileId);
      if (!mounted) return;
      // Verify this response still belongs to current finding (multi-image safety).
      if ((_resolveFile()?.id ?? widget.finding.fileId) != fileId) return;
      setState(() {
        _photo = MemoryImage(bytes);
        _photoLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _photo = null;
        _photoLoading = false;
        _photoError = 'Image unavailable for ${widget.finding.filename} ($e)';
      });
    }
  }

  double _aspect() {
    final w = widget.finding.originalWidth;
    final h = widget.finding.originalHeight;
    if (w != null && h != null && w > 0 && h > 0) return w / h;
    return 4 / 3;
  }

  @override
  Widget build(BuildContext context) {
    final detections = widget.finding.detections;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    widget.finding.filename,
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Row(
                  children: [
                    FilterChip(
                      label: const Text('Boxes', style: TextStyle(fontSize: 11)),
                      selected: _showBoxes,
                      onSelected: (val) => setState(() => _showBoxes = val),
                    ),
                    const SizedBox(width: 6),
                    FilterChip(
                      label: const Text('Masks', style: TextStyle(fontSize: 11)),
                      selected: _showMasks,
                      onSelected: (val) => setState(() => _showMasks = val),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Real uploaded photo with overlay (contain-fit aware painter)
          AspectRatio(
            aspectRatio: _aspect(),
            child: LayoutBuilder(
              builder: (context, constraints) {
                final dispW = constraints.maxWidth;
                final dispH = constraints.maxHeight;
                final ow = (widget.finding.originalWidth ?? 1024).toDouble();
                final oh = (widget.finding.originalHeight ?? 1024).toDouble();
                final imgAspect = ow / oh;
                final boxAspect = dispW / dispH;
                double drawW, drawH, offX, offY;
                if (boxAspect > imgAspect) {
                  drawH = dispH;
                  drawW = dispH * imgAspect;
                  offX = (dispW - drawW) / 2;
                  offY = 0;
                } else {
                  drawW = dispW;
                  drawH = dispW / imgAspect;
                  offX = 0;
                  offY = (dispH - drawH) / 2;
                }
                return Stack(
                  fit: StackFit.expand,
                  children: [
                    Container(color: const Color(0xFF0F172A)),
                    if (_photo != null)
                      Positioned(
                        left: offX,
                        top: offY,
                        width: drawW,
                        height: drawH,
                        child: Image(image: _photo!, fit: BoxFit.fill),
                      )
                    else if (_photoLoading)
                      const Center(
                        child: SizedBox(
                          width: 26,
                          height: 26,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                      )
                    else
                      Center(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                _photoError ?? 'Image unavailable for ${widget.finding.filename}',
                                textAlign: TextAlign.center,
                                style: const TextStyle(color: Colors.white70, fontSize: 12),
                              ),
                              const SizedBox(height: 8),
                              OutlinedButton(
                                onPressed: _retryPhoto,
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        ),
                      ),

                    // Custom Overlay Painter
                    Positioned.fill(
                      child: CustomPaint(
                        painter: _DamageOverlayPainter(
                          detections: detections,
                          showBoxes: _showBoxes,
                          showMasks: _showMasks,
                          getColor: _getClassColor,
                          originalWidth: ow,
                          originalHeight: oh,
                          offsetX: offX,
                          offsetY: offY,
                          drawWidth: drawW,
                          drawHeight: drawH,
                        ),
                      ),
                    ),

                    if (detections.isEmpty && _photo != null)
                      Positioned(
                        left: 8,
                        bottom: 8,
                        right: 8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.62),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            widget.finding.assessment == 'inconclusive'
                                ? 'Unable to determine — manual review required'
                                    '${widget.finding.assessmentReason != null && widget.finding.assessmentReason!.isNotEmpty ? ' · ${widget.finding.assessmentReason}' : ''}'
                                : 'No damage above threshold — model completed with negative result',
                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ),
                  ],
                );
              },
            ),
          ),

          // Legend / Detection Instances
          if (detections.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Wrap(
                spacing: 8,
                runSpacing: 6,
                children: detections.map((det) {
                  final color = _getClassColor(det.label);
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: color.withValues(alpha: 0.4)),
                    ),
                    child: Text(
                      '${det.label.toUpperCase()} (${(det.confidence * 100).toInt()}%)',
                      style: TextStyle(
                        color: color,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
        ],
      ),
    );
  }
}

class _DamageOverlayPainter extends CustomPainter {
  final List<DetectionModel> detections;
  final bool showBoxes;
  final bool showMasks;
  final Color Function(String) getColor;
  final double originalWidth;
  final double originalHeight;
  final double offsetX;
  final double offsetY;
  final double drawWidth;
  final double drawHeight;

  _DamageOverlayPainter({
    required this.detections,
    required this.showBoxes,
    required this.showMasks,
    required this.getColor,
    required this.originalWidth,
    required this.originalHeight,
    required this.offsetX,
    required this.offsetY,
    required this.drawWidth,
    required this.drawHeight,
  });

  double _px(double xOrig) => offsetX + (xOrig / originalWidth) * drawWidth;
  double _py(double yOrig) => offsetY + (yOrig / originalHeight) * drawHeight;

  @override
  void paint(Canvas canvas, Size size) {
    for (final det in detections) {
      final color = getColor(det.label);

      final box = det.bboxXyxy;

      final rect = Rect.fromLTRB(
        _px(box[0]),
        _py(box[1]),
        _px(box[2]),
        _py(box[3]),
      );

      // Paint Polygon Mask
      if (showMasks && det.mask != null && det.mask!.length >= 3) {
        final path = Path();
        for (int i = 0; i < det.mask!.length; i++) {
          final pt = det.mask![i];
          final dx = _px(pt[0]);
          final dy = _py(pt[1]);
          if (i == 0) {
            path.moveTo(dx, dy);
          } else {
            path.lineTo(dx, dy);
          }
        }
        path.close();

        final maskPaint = Paint()
          ..color = color.withValues(alpha: 0.35)
          ..style = PaintingStyle.fill;
        canvas.drawPath(path, maskPaint);

        final contourPaint = Paint()
          ..color = color
          ..strokeWidth = 1.5
          ..style = PaintingStyle.stroke;
        canvas.drawPath(path, contourPaint);
      }

      // Paint Bounding Box
      if (showBoxes) {
        final boxPaint = Paint()
          ..color = color
          ..strokeWidth = 2.0
          ..style = PaintingStyle.stroke;
        canvas.drawRect(rect, boxPaint);

        // Label Tag
        final tp = TextPainter(
          text: TextSpan(
            text: ' ${det.label} ${(det.confidence * 100).toInt()}% ',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.w700,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        tp.layout();

        final tagRect = Rect.fromLTWH(
          rect.left,
          rect.top - 16 >= 0 ? rect.top - 16 : rect.top,
          tp.width,
          tp.height,
        );

        canvas.drawRect(tagRect, Paint()..color = color);
        tp.paint(canvas, Offset(tagRect.left, tagRect.top));
      }
    }
  }

  @override
  bool shouldRepaint(covariant _DamageOverlayPainter oldDelegate) {
    return oldDelegate.showBoxes != showBoxes ||
        oldDelegate.showMasks != showMasks ||
        oldDelegate.drawWidth != drawWidth ||
        oldDelegate.drawHeight != drawHeight;
  }
}
