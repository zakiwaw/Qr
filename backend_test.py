#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Barcode Generator
Tests all CRUD operations, barcode generation, and database storage
"""

import requests
import json
import base64
import re
from typing import Dict, List, Any
import time

# Configuration
BACKEND_URL = "https://barcode-hub-1.preview.emergentagent.com/api"
TIMEOUT = 30

class BarcodeAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.generated_barcodes = []  # Track generated barcodes for cleanup
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def is_valid_base64_image(self, data_url: str) -> bool:
        """Validate base64 image format"""
        try:
            if not data_url.startswith("data:image/"):
                return False
            
            # Extract base64 part
            base64_part = data_url.split(",")[1]
            
            # Try to decode
            decoded = base64.b64decode(base64_part)
            
            # Check if it's a valid image (PNG signature)
            return decoded.startswith(b'\x89PNG')
        except Exception:
            return False
    
    def test_root_endpoint(self):
        """Test API availability by testing a simple endpoint"""
        try:
            # Test the /api/barcodes endpoint as a health check since root returns frontend
            response = self.session.get(f"{self.base_url}/barcodes")
            if response.status_code == 200:
                data = response.json()
                if "barcodes" in data:
                    self.log_test("API Availability", "PASS", "Backend API is accessible and responding")
                    return True
                else:
                    self.log_test("API Availability", "FAIL", "Invalid response format")
                    return False
            else:
                self.log_test("API Availability", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Availability", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_generate_barcode_text(self):
        """Test barcode generation with text input"""
        test_data = {
            "text": "Hello World 2024"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-barcode",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["id", "text", "barcode_image", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Barcode (Text)", "FAIL", f"Missing fields: {missing_fields}")
                    return False
                
                # Validate data
                if data["text"] != test_data["text"]:
                    self.log_test("Generate Barcode (Text)", "FAIL", "Text mismatch")
                    return False
                
                # Validate barcode image
                if not self.is_valid_base64_image(data["barcode_image"]):
                    self.log_test("Generate Barcode (Text)", "FAIL", "Invalid base64 image")
                    return False
                
                # Store for cleanup
                self.generated_barcodes.append(data["id"])
                
                self.log_test("Generate Barcode (Text)", "PASS", f"Generated barcode ID: {data['id']}")
                return True
            else:
                self.log_test("Generate Barcode (Text)", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Barcode (Text)", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_generate_barcode_numbers(self):
        """Test barcode generation with numeric input"""
        test_data = {
            "text": "1234567890"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-barcode",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate barcode image
                if not self.is_valid_base64_image(data["barcode_image"]):
                    self.log_test("Generate Barcode (Numbers)", "FAIL", "Invalid base64 image")
                    return False
                
                # Store for cleanup
                self.generated_barcodes.append(data["id"])
                
                self.log_test("Generate Barcode (Numbers)", "PASS", f"Generated barcode ID: {data['id']}")
                return True
            else:
                self.log_test("Generate Barcode (Numbers)", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Generate Barcode (Numbers)", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_generate_barcode_mixed(self):
        """Test barcode generation with mixed alphanumeric input"""
        test_data = {
            "text": "ABC123XYZ789"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-barcode",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate barcode image
                if not self.is_valid_base64_image(data["barcode_image"]):
                    self.log_test("Generate Barcode (Mixed)", "FAIL", "Invalid base64 image")
                    return False
                
                # Store for cleanup
                self.generated_barcodes.append(data["id"])
                
                self.log_test("Generate Barcode (Mixed)", "PASS", f"Generated barcode ID: {data['id']}")
                return True
            else:
                self.log_test("Generate Barcode (Mixed)", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Generate Barcode (Mixed)", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_generate_barcode_empty_input(self):
        """Test error handling for empty input"""
        test_data = {
            "text": ""
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-barcode",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                self.log_test("Generate Barcode (Empty Input)", "PASS", "Correctly rejected empty input")
                return True
            else:
                self.log_test("Generate Barcode (Empty Input)", "FAIL", f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Generate Barcode (Empty Input)", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_generate_barcode_whitespace_input(self):
        """Test error handling for whitespace-only input"""
        test_data = {
            "text": "   "
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate-barcode",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                self.log_test("Generate Barcode (Whitespace Input)", "PASS", "Correctly rejected whitespace input")
                return True
            else:
                self.log_test("Generate Barcode (Whitespace Input)", "FAIL", f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Generate Barcode (Whitespace Input)", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_get_all_barcodes(self):
        """Test retrieving all barcodes"""
        try:
            response = self.session.get(f"{self.base_url}/barcodes")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "barcodes" not in data:
                    self.log_test("Get All Barcodes", "FAIL", "Missing 'barcodes' field")
                    return False
                
                # Check if it's a list
                if not isinstance(data["barcodes"], list):
                    self.log_test("Get All Barcodes", "FAIL", "'barcodes' is not a list")
                    return False
                
                # If we have generated barcodes, check if they're in the list
                if self.generated_barcodes:
                    barcode_ids = [barcode["id"] for barcode in data["barcodes"]]
                    found_count = sum(1 for gen_id in self.generated_barcodes if gen_id in barcode_ids)
                    
                    if found_count > 0:
                        self.log_test("Get All Barcodes", "PASS", f"Retrieved {len(data['barcodes'])} barcodes, found {found_count} generated ones")
                    else:
                        self.log_test("Get All Barcodes", "FAIL", "Generated barcodes not found in list")
                        return False
                else:
                    self.log_test("Get All Barcodes", "PASS", f"Retrieved {len(data['barcodes'])} barcodes")
                
                return True
            else:
                self.log_test("Get All Barcodes", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Barcodes", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_get_specific_barcode(self):
        """Test retrieving a specific barcode by ID"""
        if not self.generated_barcodes:
            self.log_test("Get Specific Barcode", "SKIP", "No generated barcodes to test with")
            return True
        
        barcode_id = self.generated_barcodes[0]
        
        try:
            response = self.session.get(f"{self.base_url}/barcode/{barcode_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["id", "text", "barcode_image", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Get Specific Barcode", "FAIL", f"Missing fields: {missing_fields}")
                    return False
                
                # Validate ID matches
                if data["id"] != barcode_id:
                    self.log_test("Get Specific Barcode", "FAIL", "ID mismatch")
                    return False
                
                # Validate barcode image
                if not self.is_valid_base64_image(data["barcode_image"]):
                    self.log_test("Get Specific Barcode", "FAIL", "Invalid base64 image")
                    return False
                
                self.log_test("Get Specific Barcode", "PASS", f"Retrieved barcode: {data['text']}")
                return True
            else:
                self.log_test("Get Specific Barcode", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specific Barcode", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_get_nonexistent_barcode(self):
        """Test retrieving a non-existent barcode"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            response = self.session.get(f"{self.base_url}/barcode/{fake_id}")
            
            if response.status_code == 404:
                self.log_test("Get Non-existent Barcode", "PASS", "Correctly returned 404 for non-existent barcode")
                return True
            else:
                self.log_test("Get Non-existent Barcode", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Non-existent Barcode", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_delete_barcode(self):
        """Test deleting a specific barcode"""
        if not self.generated_barcodes:
            self.log_test("Delete Barcode", "SKIP", "No generated barcodes to test with")
            return True
        
        barcode_id = self.generated_barcodes.pop()  # Remove from list as we're deleting it
        
        try:
            response = self.session.delete(f"{self.base_url}/barcode/{barcode_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data:
                    # Verify deletion by trying to get the barcode
                    verify_response = self.session.get(f"{self.base_url}/barcode/{barcode_id}")
                    if verify_response.status_code == 404:
                        self.log_test("Delete Barcode", "PASS", f"Successfully deleted barcode {barcode_id}")
                        return True
                    else:
                        self.log_test("Delete Barcode", "FAIL", "Barcode still exists after deletion")
                        return False
                else:
                    self.log_test("Delete Barcode", "FAIL", "Missing success message")
                    return False
            else:
                self.log_test("Delete Barcode", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Delete Barcode", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_delete_nonexistent_barcode(self):
        """Test deleting a non-existent barcode"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            response = self.session.delete(f"{self.base_url}/barcode/{fake_id}")
            
            if response.status_code == 404:
                self.log_test("Delete Non-existent Barcode", "PASS", "Correctly returned 404 for non-existent barcode")
                return True
            else:
                self.log_test("Delete Non-existent Barcode", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Delete Non-existent Barcode", "FAIL", f"Error: {str(e)}")
            return False
    
    def cleanup_generated_barcodes(self):
        """Clean up any remaining generated barcodes"""
        print("🧹 Cleaning up generated barcodes...")
        for barcode_id in self.generated_barcodes:
            try:
                self.session.delete(f"{self.base_url}/barcode/{barcode_id}")
            except:
                pass  # Ignore cleanup errors
        print(f"   Cleaned up {len(self.generated_barcodes)} barcodes\n")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Barcode Generator Backend API Tests")
        print(f"   Backend URL: {self.base_url}")
        print("=" * 60)
        
        test_results = []
        
        # Test order matters - generate barcodes first, then test retrieval/deletion
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Generate Barcode (Text)", self.test_generate_barcode_text),
            ("Generate Barcode (Numbers)", self.test_generate_barcode_numbers),
            ("Generate Barcode (Mixed)", self.test_generate_barcode_mixed),
            ("Generate Barcode (Empty Input)", self.test_generate_barcode_empty_input),
            ("Generate Barcode (Whitespace Input)", self.test_generate_barcode_whitespace_input),
            ("Get All Barcodes", self.test_get_all_barcodes),
            ("Get Specific Barcode", self.test_get_specific_barcode),
            ("Get Non-existent Barcode", self.test_get_nonexistent_barcode),
            ("Delete Barcode", self.test_delete_barcode),
            ("Delete Non-existent Barcode", self.test_delete_nonexistent_barcode),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name}: FAIL - Unexpected error: {str(e)}")
                test_results.append((test_name, False))
        
        # Cleanup
        self.cleanup_generated_barcodes()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Backend needs attention.")
            return False

def main():
    """Main test execution"""
    tester = BarcodeAPITester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)