"""
Module voor het optimaliseren van door python_to_js_converter gegenereerde JavaScript code
voor gebruik in Node.js-omgevingen zoals Vercel.
"""

import re
import json
import os

def get_clean_function_name(filename, default_name="processData"):
    """
    Genereert een goede functienaam op basis van de bestandsnaam.
    
    Args:
        filename (str): De bestandsnaam
        default_name (str): De standaard functienaam als er geen goede kan worden afgeleid
        
    Returns:
        str: Een schone functienaam
    """
    # Verwijder extensie en path
    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # Verwijder eventuele getallen tussen haakjes (bijv. 'bestand (1).py' -> 'bestand')
    name_without_numbers = re.sub(r'\s*\(\d+\)', '', name_without_ext)
    
    # Vervang speciale tekens door onderstrepingen
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name_without_numbers)
    
    # Zorg ervoor dat het een geldige JavaScript identifier is
    if not clean_name or not re.match(r'^[a-zA-Z_]', clean_name):
        clean_name = 'get_' + clean_name if clean_name else default_name
    
    # Maak camelCase van snake_case
    parts = clean_name.split('_')
    camel_case = parts[0].lower() + ''.join(part.capitalize() for part in parts[1:] if part)
    
    # Als het nog steeds leeg is, gebruik default_name
    if not camel_case:
        camel_case = default_name
    
    return camel_case

def optimize_js_code(js_code, filename):
    """
    Optimaliseert JavaScript code voor gebruik in Node.js (Vercel) omgevingen.
    
    Args:
        js_code (str): De JavaScript code
        filename (str): De originele bestandsnaam
        
    Returns:
        str: De geoptimaliseerde JavaScript code
    """
    # Vervang placeholder functienamen ($1, $2, etc.)
    function_name = get_clean_function_name(filename)
    
    # Speciale behandeling voor contract templates bestanden die vaak dit patroon gebruiken
    if 'contract_templates' in filename or 'get_templates' in js_code:
        js_code = re.sub(r'function\s+\$1\s*\(\$2\)\s*\{', f'function getContractTemplates() {{', js_code)
        
        # Vervang ook de template content comment-block-placeholders met strings
        js_code = re.sub(r"'content':\s*\/\*\*\s*\n\s*\*\s*\$1\s*\n\s*\*\/", "'content': \"TEMPLATE_CONTENT_HIER\"", js_code)
        js_code = re.sub(r"'content'\s*:\s*\/\*\*[^*]*\*\/", "'content': \"TEMPLATE_CONTENT_HIER\"", js_code)
        
        # Vervang 'templates = [' door 'const templates = ['
        js_code = re.sub(r'\n(\s*)templates\s*=\s*\[', r'\n\1const templates = [', js_code)
    else:
        # Algemene placeholder functienaam
        js_code = re.sub(r'function\s+\$1\s*\(\$2\)', f'function {function_name}()', js_code)
    
    # Vervang comment-blocks als content met strings in objecten
    js_code = re.sub(r"'content':\s*\/\*\*\s*\n\s*\*\s*\$1\s*\n\s*\*\/", "'content': \"CONTENT_PLACEHOLDER\"", js_code)
    js_code = re.sub(r"'content'\s*:\s*\/\*\*[^*]*\*\/", "'content': \"CONTENT_PLACEHOLDER\"", js_code)
    js_code = re.sub(r"'description':\s*\/\*\*[^*]*\*\/", "'description': \"DESCRIPTION_PLACEHOLDER\"", js_code)
    
    # Fix dubbele declaraties voor dezelfde variabele (conflicterende imports)
    js_code_lines = js_code.split('\n')
    imports_seen = set()
    fixed_lines = []
    
    # Bijhouden van variabelen die al gedeclareerd zijn (voor en binnen functies)
    global_vars = set()
    func_vars = set()
    in_function = False
    brace_depth = 0
    
    i = 0
    while i < len(js_code_lines):
        line = js_code_lines[i]
        
        # Bijhouden van functiecontext en geneste accolades
        if 'function' in line and '{' in line:
            in_function = True
            brace_depth += line.count('{')
        elif '{' in line:
            brace_depth += line.count('{')
            
        if '}' in line:
            brace_depth -= line.count('}')
            if brace_depth <= 0 and in_function:
                in_function = False
                func_vars.clear()  # Reset functievariabelen bij elke functie-afsluiting
                brace_depth = 0
        
        # Zoek naar require-imports
        if '// import ' in line and i+6 < len(js_code_lines) and '.catch (e) {' in js_code_lines[i+6]:
            # Extraheer module naam
            module_match = re.search(r'// import (.*?);', line)
            if module_match:
                module_name = module_match.group(1).strip()
                if module_name in imports_seen:
                    # Sla deze import over (6 regels)
                    i += 7
                    continue
                else:
                    imports_seen.add(module_name)
                    
                    # Als het een algemene import is zoals "os", vervang door betere naam
                    if module_name in ["os", "json", "datetime", "sys", "re", "time", "math"]:
                        var_name = f"{module_name}Module"
                        fixed_lines.append(f"// Import {module_name} module")
                        fixed_lines.append(f"let {var_name};")
                        fixed_lines.append(f"try {{")
                        fixed_lines.append(f"  {var_name} = require('{module_name}');")
                        fixed_lines.append(f"}} catch (e) {{")
                        fixed_lines.append(f"  console.warn('Module {module_name} kon niet worden ingeladen, functionaliteit kan beperkt zijn');")
                        fixed_lines.append(f"}}")
                        global_vars.add(var_name)  # Houd bij dat deze variabele bestaat
                        i += 7
                        continue
        
        # Fix voor dubbele variabele declaraties
        var_decl_match = re.match(r'^(\s*)(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
        if var_decl_match:
            spaces, decl_type, var_name = var_decl_match.groups()
            if in_function:
                if var_name in func_vars:
                    # Verwijder duplicated declaratie binnen een functie
                    line = re.sub(r'^(\s*)(const|let|var)\s+', r'\1', line)
                else:
                    func_vars.add(var_name)
            else:
                if var_name in global_vars:
                    # Verwijder duplicated declaratie op global niveau
                    line = re.sub(r'^(\s*)(const|let|var)\s+', r'\1', line)
                else:
                    global_vars.add(var_name)
        
        # Fix inline functiedeclaraties zonder const/let/var
        func_decl_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\(', line)
        if func_decl_match and not re.search(r'(const|let|var)\s+', line):
            spaces, func_name = func_decl_match.groups()
            line = f"{spaces}const {func_name} = function("
        
        # Voeg variabele declaraties toe (const, let) voor andere toewijzingen
        assign_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if assign_match and not re.search(r'(const|let|var|this\.)\s*', line) and not line.strip().startswith('//'):
            spaces, var_name, value = assign_match.groups()
            
            # Sla bekende globals en properties over
            if var_name not in ['module', 'exports', 'window'] and not var_name.startswith('this.'):
                # Gebruik let of const afhankelijk van waarde/context
                is_object = '{' in value and value.strip().endswith('{') 
                is_array = '[' in value and not ']' in value
                declaration = 'let' if is_object or is_array else 'const'
                line = f"{spaces}{declaration} {var_name} = {value}"
        
        fixed_lines.append(line)
        i += 1
    
    js_code = '\n'.join(fixed_lines)
    
    # Vervang algemene placeholder variabelen
    js_code = re.sub(r'\$1', 'value', js_code)
    js_code = re.sub(r'\$2', 'key', js_code)
    js_code = re.sub(r'\$3', 'data', js_code)
    
    # Fix dubbele exports (als ze al bestaan in de code)
    if 'module.exports' in js_code:
        # Verwijder handmatig toegevoegde exports aan het eind
        js_code = re.sub(r'\n\n// Export voor Node\.js\nmodule\.exports = \{\n  [a-zA-Z0-9_]+\n\};\n$', '', js_code)
    else:
        # Voeg basis export toe als die er nog niet is
        exported_items = []
        
        # Zoek naar template variabelen als die bestaan
        if 'templates =' in js_code or 'getContractTemplates' in js_code:
            exported_items.append('templates')
            exported_items.append('getContractTemplates')
        # Voeg standaard functienaam toe
        else:
            exported_items.append(function_name)
        
        # Voeg andere variabelen/functies toe die geëxporteerd moeten worden
        for common_export in ['htmlContent', 'cssContent', 'data', 'sqlContent', 'content']:
            if f'const {common_export} =' in js_code:
                exported_items.append(common_export)
        
        # Zoek specifieke functies voor verschillende bestandstypen
        if 'renderHtmlToElement' in js_code:
            exported_items.extend(['renderHtmlToElement', 'createHtmlFragment', 'parseHtmlWithJSDOM', 'writeHtmlToFile'])
        if 'injectCssToPage' in js_code:
            exported_items.extend(['injectCssToPage', 'isCssInjected', 'writeCssToFile', 'generateStyleTag'])
        if 'splitQueries' in js_code:
            exported_items.extend(['splitQueries', 'executeQuery', 'executeWithMySQL', 'executeWithPostgres'])
            
        # Genereer de export code
        js_code += "\n\n// CommonJS exports voor Node.js\nmodule.exports = {\n"
        for i, item in enumerate(exported_items):
            js_code += f"  {item}"
            if i < len(exported_items) - 1:
                js_code += ","
            js_code += "\n"
        js_code += "};\n"
    
    # Consistentie in export notatie
    js_code = js_code.replace("if (typeof module !== 'undefined' && module.exports)", "// CommonJS exports\nif (typeof module !== 'undefined' && module.exports)")
    
    # Zorg dat er een waarschuwingscommentaar over handmatige aanpassingen bovenaan staat
    if "AUTOMATISCH GEGENEREERD" in js_code and "VOOR GEBRUIK MET VERCEL/NODE.JS" not in js_code:
        js_code = js_code.replace("AUTOMATISCH GEGENEREERD", 
                                 "AUTOMATISCH GEGENEREERD - VOOR GEBRUIK MET VERCEL/NODE.JS\n * Handmatige aanpassingen kunnen nodig zijn voor optimale functionaliteit.")
    
    return js_code

def optimize_js_file(input_path, output_path):
    """
    Optimaliseert een JavaScript bestand voor Node.js.
    
    Args:
        input_path (str): Het pad naar het input JavaScript bestand
        output_path (str): Het pad waar het geoptimaliseerde bestand moet worden opgeslagen
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        js_code = f.read()
    
    optimized_code = optimize_js_code(js_code, os.path.basename(input_path))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(optimized_code)
    
    print(f"Geoptimaliseerd bestand opgeslagen als {output_path}")

def batch_optimize_directory(input_dir, output_dir):
    """
    Optimaliseert alle JavaScript bestanden in een directory.
    
    Args:
        input_dir (str): De directory met input JavaScript bestanden
        output_dir (str): De directory waar geoptimaliseerde bestanden moeten worden opgeslagen
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.js'):
                input_path = os.path.join(root, file)
                # Behoud relatieve mapstructuur
                rel_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, rel_path)
                
                # Zorg dat de output directory bestaat
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                optimize_js_file(input_path, output_path)
                print(f"Geoptimaliseerd: {rel_path}")

# Voorbeeld gebruik:
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]) and sys.argv[1].endswith('.js'):
            # Optimaliseer één bestand
            output_path = sys.argv[1].replace('.js', '.optimized.js')
            if len(sys.argv) > 2:
                output_path = sys.argv[2]
            optimize_js_file(sys.argv[1], output_path)
        elif os.path.isdir(sys.argv[1]):
            # Optimaliseer een hele directory
            output_dir = os.path.join(os.path.dirname(sys.argv[1]), "optimized_js")
            if len(sys.argv) > 2:
                output_dir = sys.argv[2]
            batch_optimize_directory(sys.argv[1], output_dir)
        else:
            print(f"Fout: {sys.argv[1]} is geen JavaScript bestand of directory")
    else:
        print("Gebruik: python js_converter_optimizer.py <js_file_or_directory> [output_path]")