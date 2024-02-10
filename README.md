# API Service for Converting JSON and XML Files to a Dictionary

## Overview

This API service allows you to upload multiple JSON and XML files and receive a unified dictionary containing the processed information from all documents. It handles data normalization and merging to create a consolidated result.

## Key Features

- Supports both JSON and XML file uploads.
- Normalizes dates and durations within documents.
- Merges data from multiple files into a single dictionary.
- Provides a user-friendly API endpoint for easy integration.

## API Endpoint

- **URL:** `/api/upload_files`
- **Method:** POST

### Request

- Multipart/form-data
- files: List of files to upload (required)

### Response

- JSON
- data: Processed data dictionary or an error message.