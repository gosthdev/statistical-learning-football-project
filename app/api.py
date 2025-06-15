import os
import shutil # Keep for potential future use, but not for writing content

class Api:
    def __init__(self):
        self.window = None
        # Path to default datasets, relative to project root
        self.default_data_path = os.path.join('data', 'default_datasets')
        # Path to where raw files will be copied, relative to project root
        self.raw_data_output_path = os.path.join('data', 'raw')

    def set_window(self, window):
        self.window = window

    def load_default_datasets(self):
        """
        Reads file names from the default datasets folder and returns them to JavaScript.
        """
        try:
            # Assuming main.py runs from the project root, paths are relative to it.
            if not os.path.isdir(self.default_data_path):
                print(f"Error: Default dataset directory not found at '{self.default_data_path}'.")
                return []
            files = [f for f in os.listdir(self.default_data_path) if f.endswith('.csv')]
            return files
        except Exception as e:
            print(f"Error listing default datasets: {e}")
            return []

    def process_files(self, files_to_process):
        """
        Receives the list of files from JS.
        Copies each valid file to the self.raw_data_output_path (data/raw/) directory.
        """
        print("Received for processing (content mode):", 
              [{'name': f.get('name'), 'type': f.get('type'), 'content_length': len(f.get('content')) if f.get('content') else 0} for f in files_to_process])
        
        files_to_write_to_raw = [] # Store {'name': ..., 'content': ...} for uploaded files

        # Determine full source paths for each file
        for file_info in files_to_process:
            original_name = file_info.get('name')
            file_type = file_info.get('type')
            file_content = file_info.get('content') # Content from JS

            if file_type == 'default':
                print(f"Info: Default file '{original_name}' will be skipped for writing to raw directory.")
                # Default files are not copied to data/raw as per new requirement
                continue 
            
            elif file_type == 'uploaded':
                if original_name and file_content is not None: # Check if content is present (even if empty string)
                    files_to_write_to_raw.append({'name': original_name, 'content': file_content})
                    print(f"Info: Uploaded file '{original_name}' (content length: {len(file_content)}) is eligible for writing.")
                elif not original_name:
                    print(f"Warning: Uploaded file has no name. Skipping.")
                else: # No content
                    print(f"Warning: Uploaded file '{original_name}' has no content. Skipping.")
            else:
                print(f"Warning: Unknown file type for '{original_name}': {file_type}. Skipping.")

        if not files_to_write_to_raw:
            return {"status": "info", "message": "No uploaded files with content were found to write to the raw directory."}

        # Ensure the raw_data_output_path directory exists
        try:
            os.makedirs(self.raw_data_output_path, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory {self.raw_data_output_path}: {e}")
            return {"status": "error", "message": f"Could not create destination directory: {e}"}

        written_files_count = 0
        failed_writes_info = []

        print(f"Attempting to write content of {len(files_to_write_to_raw)} uploaded file(s) to '{self.raw_data_output_path}'...")

        for detail in files_to_write_to_raw:
            file_name_for_destination = detail['name']
            content_to_write = detail['content']
            dest_path = os.path.join(self.raw_data_output_path, file_name_for_destination)
            
            try:
                with open(dest_path, 'w', encoding='utf-8') as f: # Open in text write mode
                    f.write(content_to_write)
                print(f"Content written to: '{dest_path}'")
                written_files_count += 1
            except Exception as e:
                error_msg = f"Error writing content for '{file_name_for_destination}' to '{dest_path}': {e}"
                print(error_msg)
                failed_writes_info.append({'name': file_name_for_destination, 'error': str(e)})
        
        if written_files_count == len(files_to_write_to_raw) and written_files_count > 0:
            return {"status": "success", "message": f"{written_files_count} uploaded file(s) successfully written to '{self.raw_data_output_path}'."}
        elif written_files_count > 0:
            return {"status": "partial_success", 
                    "message": f"{written_files_count} of {len(files_to_write_to_raw)} file(s) written. {len(failed_writes_info)} failed.",
                    "failures": failed_writes_info}
        else: # All attempts to write failed (but there were files to write)
            return {"status": "error", 
                    "message": f"Failed to write content for any of the eligible uploaded files to '{self.raw_data_output_path}'.",
                    "failures": failed_writes_info}