import 'package:flutter/material.dart';
import '../models/complaint_model.dart';

class AIAnalysisScreen extends StatelessWidget {
  final ComplaintModel complaint;

  const AIAnalysisScreen({super.key, required this.complaint});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Analysis'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'AI Analysis Results',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Category: ${complaint.category ?? 'N/A'}'),
                    Text('Subcategory: ${complaint.subcategory ?? 'N/A'}'),
                    Text('Severity: ${complaint.severity ?? 'N/A'}'),
                    Text('Priority: ${complaint.priority ?? 'N/A'}'),
                    Text('Department: ${complaint.department ?? 'N/A'}'),
                    Text('SLA: ${complaint.slaHours ?? 0} hours'),
                    Text('Summary: ${complaint.summary ?? 'N/A'}'),
                    const Divider(height: 24, thickness: 1),
                    Text('Recommended Action: ${complaint.recommendedAction ?? 'N/A'}',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    Text('Confidence: ${(complaint.confidence ?? 0).toStringAsFixed(2)}'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                // In a real app, we might do something else, but for now just go to my complaints
                Navigator.of(context).pushNamed('/my-complaints');
              },
              child: const Text('Confirm and Submit'),
            ),
          ],
        ),
      ),
    );
  }
}