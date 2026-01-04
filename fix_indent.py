import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section starting from "User is logged in"
parts = content.split('# User is logged in - show main app')

if len(parts) == 2:
    before = parts[0]
    after = parts[1]
    
    # Find where the try block starts
    try_start = after.find('try:')
    if try_start != -1:
        before_try = after[:try_start + 4]  # Include 'try:'
        after_try = after[try_start + 4:]
        
        # Find the first except block (for the main app)
        except_match = re.search(r'\nexcept Exception as e:\n    st\.error\(f"❌ Error in main app UI', after_try)
        
        if except_match:
            main_code = after_try[:except_match.start()]
            after_except = after_try[except_match.start():]
            
            # Indent all non-empty lines in main_code by 4 spaces if they don't already start with 4+ spaces
            lines = main_code.split('\n')
            indented_lines = []
            
            for line in lines:
                if line.strip():  # Not empty
                    # Check current indentation
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent < 4:
                        # Add 4 spaces
                        indented_lines.append('    ' + line)
                    else:
                        indented_lines.append(line)
                else:
                    indented_lines.append(line)
            
            # Reconstruct
            new_content = before + '# User is logged in - show main app' + before_try + '\n'.join(indented_lines) + after_except
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Fixed indentation successfully")
        else:
            print("Could not find except block")
    else:
        print("Could not find try block")
else:
    print("Could not split content")
