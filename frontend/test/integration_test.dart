import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:pragati/models/complaint_model.dart';

const String baseUrl = 'http://127.0.0.1:8000/api/v1';

void main() {
  group('End-to-end workflow test', () {
    late String complaintId;

    test('Submit a complaint (citizen flow)', () async {
      final complaintData = {
        'citizen_id': 'citizen_example_uid', // Backend uses this hardcoded value
        'description': 'The street lights near our college have not been working for five days.',
        'location': 'Main Street, Near College',
      };

      final response = await http.post(
        Uri.parse('$baseUrl/complaints/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(complaintData),
      );

      expect(response.statusCode, 200);

      final complaint = ComplaintModel.fromJson(jsonDecode(response.body));
      expect(complaint.description, complaintData['description']);
      expect(complaint.location, complaintData['location']);
      expect(complaint.citizenId, complaintData['citizen_id']);
      expect(complaint.id, isNotNull);
      expect(complaint.status, 'AI_PROCESSED'); // After AI processing
      expect(complaint.aiSource, 'nvidia');
      expect(complaint.category, isNotNull);
      expect(complaint.severity, isNotNull);

      complaintId = complaint.id!;
      expect(complaintId, isNotNull);
    });

    test('Retrieve the complaint (citizen tracking)', () async {
      final response = await http.get(Uri.parse('$baseUrl/complaints/$complaintId'));

      expect(response.statusCode, 200);

      final complaint = ComplaintModel.fromJson(jsonDecode(response.body));
      expect(complaint.id, complaintId);
      expect(complaint.description, 'The street lights near our college have not been working for five days.');
      expect(complaint.status, 'AI_PROCESSED');
    });

    test('Officer assigns and updates status (officer flow)', () async {
      // Assign officer
      final assignResponse = await http.patch(
        Uri.parse('$baseUrl/complaints/$complaintId/assign'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'officer_id': 'officer_001'}),
      );

      expect(assignResponse.statusCode, 200);

      final assignedComplaint = ComplaintModel.fromJson(jsonDecode(assignResponse.body));
      expect(assignedComplaint.assignedOfficer, 'officer_001');
      expect(assignedComplaint.status, 'ASSIGNED');

      // Update status to IN_PROGRESS
      final inProgressResponse = await http.patch(
        Uri.parse('$baseUrl/complaints/$complaintId/status'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'status': 'IN_PROGRESS'}),
      );

      expect(inProgressResponse.statusCode, 200);

      final inProgressComplaint = ComplaintModel.fromJson(jsonDecode(inProgressResponse.body));
      expect(inProgressComplaint.status, 'IN_PROGRESS');

      // Update status to RESOLVED
      final resolvedResponse = await http.patch(
        Uri.parse('$baseUrl/complaints/$complaintId/status'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'status': 'RESOLVED'}),
      );

      expect(resolvedResponse.statusCode, 200);

      final resolvedComplaint = ComplaintModel.fromJson(jsonDecode(resolvedResponse.body));
      expect(resolvedComplaint.status, 'RESOLVED');
      expect(resolvedComplaint.resolvedAt, isNotNull);
      // Verify resolved_at is set (not null and is a string in ISO format)
      expect(resolvedComplaint.resolvedAt, isNotNull);
    });

    test('Verify complaint in citizen tracking after resolution', () async {
      final response = await http.get(Uri.parse('$baseUrl/complaints/$complaintId'));

      expect(response.statusCode, 200);

      final complaint = ComplaintModel.fromJson(jsonDecode(response.body));
      expect(complaint.id, complaintId);
      expect(complaint.status, 'RESOLVED');
      expect(complaint.resolvedAt, isNotNull);
    });
  });
}