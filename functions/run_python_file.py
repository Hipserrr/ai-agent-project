import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_dir]
        if args != None:
            command.extend(args)

        completed_process = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output_str = ""
        if completed_process.returncode != 0:
            output_str += f'Process exited with code {completed_process.returncode}'

        if completed_process.stdout == None and completed_process.stderr == None:
            output_str += "No output produced"
        else:
            output_str += f'STDOUT: {completed_process.stdout}'
            output_str += f'STDERR: {completed_process.stderr}'
        return output_str
    
    except Exception as e:
        return f"Error: executing Python file: {e}"