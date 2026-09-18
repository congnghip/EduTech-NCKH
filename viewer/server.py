#!/usr/bin/env python3
"""
MOOCCubeX Raw Data Server
Lightweight server that streams and pages raw dataset files (JSONL, TSV) from data_raw/
Built with Python standard library - zero external dependencies required!
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, '../data_raw'))
if not os.path.exists(RAW_DIR):
    alt_raw = os.path.abspath(os.path.join(BASE_DIR, '../../Data_NCKH/data_raw'))
    if os.path.exists(alt_raw):
        RAW_DIR = alt_raw


def get_format(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.json':
        return 'jsonl'
    elif ext == '.txt':
        return 'tsv'
    return 'raw'

def format_size(bytes_sz):
    if bytes_sz < 1024:
        return f"{bytes_sz} B"
    elif bytes_sz < 1024 * 1024:
        return f"{bytes_sz / 1024:.1f} KB"
    elif bytes_sz < 1024 * 1024 * 1024:
        return f"{bytes_sz / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_sz / (1024 * 1024 * 1024):.2f} GB"

def get_tsv_columns(filename):
    name = os.path.splitext(filename)[0]
    col_mapping = {
        'comment-reply': ['comment_id', 'reply_id'],
        'concept-comment': ['concept_id', 'comment_id'],
        'concept-course': ['concept_id', 'course_id'],
        'concept-other': ['concept_id', 'other_id'],
        'concept-paper': ['concept_id', 'paper_id'],
        'concept-problem': ['concept_id', 'problem_id'],
        'concept-video': ['concept_id', 'ccid_or_video'],
        'course-comment': ['course_id', 'comment_id'],
        'course-school': ['course_id', 'school_id'],
        'course-teacher': ['course_id', 'teacher_id'],
        'exercise-problem': ['exercise_id', 'problem_id'],
        'user-comment': ['user_id', 'comment_id'],
        'user-reply': ['user_id', 'reply_id'],
        'video_id-ccid': ['video_id', 'ccid'],
    }
    return col_mapping.get(name, ['col_1', 'col_2'])

def list_raw_files():
    categories = ['entities', 'relations', 'prerequisites']
    files_list = []
    
    for cat in categories:
        cat_dir = os.path.join(RAW_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        for f in sorted(os.listdir(cat_dir)):
            if f.startswith('.'):
                continue
            path = os.path.join(cat_dir, f)
            if not os.path.isfile(path):
                continue
            sz = os.path.getsize(path)
            fmt = get_format(f)
            rel_path = f"{cat}/{f}"
            
            meta = {
                'rel_path': rel_path,
                'category': cat,
                'filename': f,
                'size_bytes': sz,
                'size_str': format_size(sz),
                'format': fmt,
            }
            if fmt == 'tsv':
                meta['tsv_columns'] = get_tsv_columns(f)
            files_list.append(meta)
            
    return files_list

class RawDataHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/files':
            self.handle_api_files()
        elif path == '/api/data':
            params = urllib.parse.parse_qs(parsed.query)
            self.handle_api_data(params)
        else:
            super().do_GET()

    def handle_api_files(self):
        files = list_raw_files()
        res = {
            'success': True,
            'count': len(files),
            'files': files
        }
        data_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data_bytes)))
        self.end_headers()
        self.wfile.write(data_bytes)

    def handle_api_data(self, params):
        rel_file = params.get('file', [''])[0]
        offset = int(params.get('offset', ['0'])[0])
        limit = min(int(params.get('limit', ['50'])[0]), 200)
        search = params.get('search', [''])[0].strip().lower()

        # Security check: prevent directory traversal
        target_path = os.path.abspath(os.path.join(RAW_DIR, rel_file))
        if not target_path.startswith(RAW_DIR) or not os.path.isfile(target_path):
            self.send_error_json(404, f"File not found: {rel_file}")
            return

        fmt = get_format(os.path.basename(target_path))
        tsv_cols = get_tsv_columns(os.path.basename(target_path)) if fmt == 'tsv' else None

        records = []
        raw_lines = []
        scanned = 0
        matches = 0
        has_more = False

        try:
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as fp:
                # If no search term, directly skip offset lines
                if not search:
                    for _ in range(offset):
                        line = fp.readline()
                        if not line:
                            break

                    for _ in range(limit):
                        line = fp.readline()
                        if not line:
                            break
                        line_stripped = line.strip()
                        if not line_stripped:
                            continue
                        raw_lines.append(line_stripped)
                        if fmt == 'jsonl':
                            try:
                                records.append(json.loads(line_stripped))
                            except Exception:
                                records.append({'_raw': line_stripped})
                        elif fmt == 'tsv':
                            parts = line_stripped.split('\t')
                            row_dict = {}
                            for i, p in enumerate(parts):
                                col_name = tsv_cols[i] if tsv_cols and i < len(tsv_cols) else f"col_{i+1}"
                                row_dict[col_name] = p
                            records.append(row_dict)
                        else:
                            records.append({'line': line_stripped})

                    # Check if there is next line
                    peek = fp.readline()
                    has_more = bool(peek)
                    scanned = offset + len(records)
                else:
                    # Search mode: scan up to max 50,000 lines to protect server
                    max_scan = 50000
                    current_idx = 0
                    while current_idx < max_scan:
                        line = fp.readline()
                        if not line:
                            break
                        current_idx += 1
                        if search in line.lower():
                            matches += 1
                            if matches > offset:
                                line_stripped = line.strip()
                                raw_lines.append(line_stripped)
                                if fmt == 'jsonl':
                                    try:
                                        records.append(json.loads(line_stripped))
                                    except Exception:
                                        records.append({'_raw': line_stripped})
                                elif fmt == 'tsv':
                                    parts = line_stripped.split('\t')
                                    row_dict = {}
                                    for i, p in enumerate(parts):
                                        col_name = tsv_cols[i] if tsv_cols and i < len(tsv_cols) else f"col_{i+1}"
                                        row_dict[col_name] = p
                                    records.append(row_dict)
                                else:
                                    records.append({'line': line_stripped})

                                if len(records) >= limit:
                                    has_more = True
                                    break
                    scanned = current_idx

            res = {
                'success': True,
                'file': rel_file,
                'format': fmt,
                'offset': offset,
                'limit': limit,
                'search': search,
                'scanned': scanned,
                'matches': matches if search else len(records),
                'has_more': has_more,
                'records': records,
                'raw_lines': raw_lines
            }
            data_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data_bytes)))
            self.end_headers()
            self.wfile.write(data_bytes)

        except Exception as e:
            self.send_error_json(500, f"Error reading file: {str(e)}")

    def send_error_json(self, code, msg):
        res = {'success': False, 'error': msg}
        data_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data_bytes)))
        self.end_headers()
        self.wfile.write(data_bytes)

def run_server(port=8080):
    server_address = ('0.0.0.0', port)
    while True:
        try:
            httpd = HTTPServer(server_address, RawDataHandler)
            break
        except OSError:
            port += 1
            server_address = ('0.0.0.0', port)

    print("\n" + "=" * 65)
    print("  🚀 MOOCCubeX RAW DATA EXPLORER SERVER")
    print(f"  📂 Raw data path: {RAW_DIR}")
    print(f"  🌐 Viewer URL:    http://localhost:{port}")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    p = 8080
    if len(sys.argv) > 1:
        try:
            p = int(sys.argv[1])
        except ValueError:
            pass
    run_server(p)
