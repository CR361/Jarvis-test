"""
Module voor het converteren van Python code naar JavaScript/Node.js code.
"""

import re
import json

def convert_other_to_js(source_code, file_extension):
    """
    Converteert niet-Python code (HTML, CSS, JSON) naar een JavaScript module
    die de inhoud kan weergeven of gebruiken.
    
    Args:
        source_code (str): De broncode
        file_extension (str): Het type bronbestand (.html, .css, .json, etc.)
        
    Returns:
        str: Een JavaScript module die de broncode bevat
    """
    # Escape speciale tekens voor string literals
    escaped_code = json.dumps(source_code)
    
    # Maak een JavaScript module afhankelijk van het bestandstype
    if file_extension == '.html':
        js_code = f"""
/**
 * JavaScript module gegenereerd uit HTML template
 * Deze module stelt de HTML beschikbaar als string en bevat functies om deze te gebruiken
 */

// De originele HTML als string
const htmlContent = {escaped_code};

/**
 * Rendert de HTML naar een DOM element in browser-omgeving
 * @param {{Element|string}} container - DOM element of selector string
 */
function renderHtmlToElement(container) {{
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {{
    const targetElement = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;
    
    if (!targetElement) {{
      console.error('Target element not found');
      return;
    }}
    
    targetElement.innerHTML = htmlContent;
  }} else {{
    console.warn('renderHtmlToElement is alleen beschikbaar in browser-omgeving');
  }}
}}

/**
 * Maakt een nieuwe DOM element met de HTML inhoud in browser-omgeving
 * @returns {{DocumentFragment|null}} Een document fragment met de HTML inhoud
 */
function createHtmlFragment() {{
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {{
    const template = document.createElement('template');
    template.innerHTML = htmlContent;
    return template.content.cloneNode(true);
  }} else {{
    console.warn('createHtmlFragment is alleen beschikbaar in browser-omgeving');
    return null;
  }}
}}

/**
 * Parse HTML naar een DOM structuur (Node.js compatibel met jsdom)
 * @param {{Object}} jsdom - De jsdom module (vereist voor Node.js: npm install jsdom)
 * @returns {{Object}} Het geparste document object
 */
function parseHtmlWithJSDOM(jsdom) {{
  if (!jsdom || !jsdom.JSDOM) {{
    throw new Error('Geldige jsdom module vereist. Installeer met: npm install jsdom');
  }}
  return new jsdom.JSDOM(htmlContent).window.document;
}}

/**
 * Schrijft de HTML inhoud naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar de HTML naartoe geschreven moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeHtmlToFile(filepath) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      await fs.writeFile(filepath, htmlContent, 'utf8');
      console.log(`HTML geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven van HTML naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeHtmlToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    htmlContent,
    renderHtmlToElement,
    createHtmlFragment,
    parseHtmlWithJSDOM,
    writeHtmlToFile
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.HTMLModule = {{
    htmlContent,
    renderHtmlToElement,
    createHtmlFragment
  }};
}}
"""
    elif file_extension == '.css':
        js_code = f"""
/**
 * JavaScript module gegenereerd uit CSS
 * Deze module stelt de CSS beschikbaar en bevat functies om deze in te laden
 */

// De originele CSS als string
const cssContent = {escaped_code};

/**
 * Voegt de CSS toe aan de pagina in browser-omgeving
 * @param {{string}} id - Optionele ID voor het style element
 * @returns {{HTMLStyleElement|null}} Het aangemaakte style element
 */
function injectCssToPage(id) {{
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {{
    const style = document.createElement('style');
    if (id) style.id = id;
    style.textContent = cssContent;
    document.head.appendChild(style);
    return style;
  }} else {{
    console.warn('injectCssToPage is alleen beschikbaar in browser-omgeving');
    return null;
  }}
}}

/**
 * Controleert of de CSS al is toegevoegd aan de pagina in browser-omgeving
 * @param {{string}} id - De ID van het style element
 * @returns {{boolean}} True als de CSS al is toegevoegd
 */
function isCssInjected(id) {{
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {{
    return !!document.getElementById(id);
  }}
  return false;
}}

/**
 * Schrijft de CSS naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar het CSS bestand naartoe geschreven moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeCssToFile(filepath) {{
  // Check of we in een Node.js omgeving zijn en fs beschikbaar is
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      await fs.writeFile(filepath, cssContent, 'utf8');
      console.log(`CSS geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven van CSS naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeCssToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

/**
 * Genereert een <style> tag met de CSS inhoud
 * @returns {{string}} HTML style tag met de CSS inhoud
 */
function generateStyleTag(id = '') {{
  const idAttr = id ? ` id="${{id}}"` : '';
  return `<style${{idAttr}}>${{cssContent}}</style>`;
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    cssContent,
    injectCssToPage,
    isCssInjected,
    writeCssToFile,
    generateStyleTag
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.CSSModule = {{
    cssContent,
    injectCssToPage,
    isCssInjected,
    generateStyleTag
  }};
}}
"""
    elif file_extension == '.json':
        # Probeer JSON te parsen om het als object beschikbaar te stellen
        try:
            parsed_json = json.loads(source_code)
            json_str = json.dumps(parsed_json, indent=2)
            js_code = f"""
/**
 * JavaScript module gegenereerd uit JSON data
 */

// De JSON data als JavaScript object
const data = {json_str};

/**
 * Schrijft het JSON object naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar het JSON bestand naartoe geschreven moet worden
 * @param {{boolean}} [pretty=true] - Of de JSON mooi geformatteerd moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeToFile(filepath, pretty = true) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      const jsonStr = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);
      await fs.writeFile(filepath, jsonStr, 'utf8');
      console.log(`JSON geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven van JSON naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    data,
    writeToFile,
    raw: JSON.stringify(data)
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.JSONModule = data;
}}
"""
        except json.JSONDecodeError:
            # Als het geen geldige JSON is, gewoon als string exporteren
            js_code = f"""
/**
 * JavaScript module gegenereerd uit JSON-achtige data (niet geldig JSON)
 */

// De originele content als string
const rawContent = {escaped_code};

/**
 * Poging om de inhoud als JSON te parsen
 * @returns {{Object|null}} Het geparseerde object of null bij fout
 */
function tryParse() {{
  try {{
    return JSON.parse(rawContent);
  }} catch (error) {{
    console.error('Kon de inhoud niet parsen als JSON:', error.message);
    return null;
  }}
}}

/**
 * Schrijft de inhoud naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar het bestand naartoe geschreven moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeToFile(filepath) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      await fs.writeFile(filepath, rawContent, 'utf8');
      console.log(`Content geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    rawContent,
    tryParse,
    writeToFile
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.JSONModule = {{
    rawContent,
    tryParse
  }};
}}
"""
    elif file_extension == '.sql':
        js_code = f"""
/**
 * JavaScript module gegenereerd uit SQL script
 * Deze module stelt de SQL queries beschikbaar voor gebruik in Node.js
 */

// De originele SQL als string
const sqlContent = {escaped_code};

/**
 * Splitst het SQL script in afzonderlijke queries
 * @returns {{string[]}} Array van SQL queries
 */
function splitQueries() {{
  // Eenvoudige splitsing op puntkomma, kan verbeterd worden voor complexere SQL
  return sqlContent.split(';')
    .map(query => query.trim())
    .filter(query => query.length > 0);
}}

/**
 * Voert een query uit met de gegeven database verbinding (voor Node.js)
 * @param {{Object}} connection - Database connection object (bijv. van 'mysql', 'pg', etc.)
 * @param {{string}} query - De uit te voeren query, standaard het hele script
 * @returns {{Promise<Object>}} Een promise met het resultaat van de query
 */
async function executeQuery(connection, query = sqlContent) {{
  if (!connection || typeof connection.query !== 'function') {{
    throw new Error('Ongeldige database verbinding');
  }}
  
  return new Promise((resolve, reject) => {{
    connection.query(query, (error, results) => {{
      if (error) reject(error);
      else resolve(results);
    }});
  }});
}}

/**
 * Maakt een verbinding met een MySQL/MariaDB database en voert de query uit
 * @param {{Object}} config - Configuratie voor MySQL verbinding
 * @param {{string}} [query=sqlContent] - De uit te voeren query
 * @returns {{Promise<Object>}} Een promise met het resultaat van de query
 */
async function executeWithMySQL(config, query = sqlContent) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require === 'undefined') {{
    console.warn('executeWithMySQL is alleen beschikbaar in Node.js omgeving');
    return Promise.reject(new Error('Deze functie werkt alleen in Node.js'));
  }}
  
  let mysql, connection;
  
  try {{
    mysql = require('mysql2/promise');
    connection = await mysql.createConnection(config);
    const [results] = await connection.query(query);
    return results;
  }} catch (error) {{
    console.error(`SQL uitvoeringsfout: ${{error.message}}`);
    throw error;
  }} finally {{
    if (connection) await connection.end();
  }}
}}

/**
 * Maakt een verbinding met een PostgreSQL database en voert de query uit
 * @param {{Object}} config - Configuratie voor PostgreSQL verbinding
 * @param {{string}} [query=sqlContent] - De uit te voeren query
 * @returns {{Promise<Object>}} Een promise met het resultaat van de query
 */
async function executeWithPostgres(config, query = sqlContent) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require === 'undefined') {{
    console.warn('executeWithPostgres is alleen beschikbaar in Node.js omgeving');
    return Promise.reject(new Error('Deze functie werkt alleen in Node.js'));
  }}
  
  let pg, client;
  
  try {{
    pg = require('pg');
    client = new pg.Client(config);
    await client.connect();
    const results = await client.query(query);
    return results.rows;
  }} catch (error) {{
    console.error(`SQL uitvoeringsfout: ${{error.message}}`);
    throw error;
  }} finally {{
    if (client) await client.end();
  }}
}}

/**
 * Schrijft het SQL script naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar het SQL bestand naartoe geschreven moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeToFile(filepath) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      await fs.writeFile(filepath, sqlContent, 'utf8');
      console.log(`SQL geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven van SQL naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    sqlContent,
    splitQueries,
    executeQuery,
    executeWithMySQL,
    executeWithPostgres,
    writeToFile
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.SQLModule = {{
    sqlContent,
    splitQueries
  }};
}}
"""
    else:
        # Voor andere bestandstypen, eenvoudige string export
        js_code = f"""
/**
 * JavaScript module gegenereerd uit een bestand
 */

// De originele content als string
const content = {escaped_code};

/**
 * Schrijft de inhoud naar een bestand (Node.js omgeving)
 * @param {{string}} filepath - Het pad waar het bestand naartoe geschreven moet worden
 * @returns {{Promise<void>}} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeToFile(filepath) {{
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {{
    try {{
      const fs = require('fs').promises;
      await fs.writeFile(filepath, content, 'utf8');
      console.log(`Content geschreven naar ${{filepath}}`);
    }} catch (error) {{
      console.error(`Fout bij het schrijven naar bestand: ${{error.message}}`);
      throw error;
    }}
  }} else {{
    console.warn('writeToFile is alleen beschikbaar in Node.js omgeving');
  }}
}}

// Node.js module exports
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{
    content,
    writeToFile
  }};
}}

// Browser/ES module exports
if (typeof window !== 'undefined') {{
  window.FileModule = {{
    content
  }};
}}
"""
    
    # Voeg header toe
    import datetime
    header = f"""/**
 * AUTOMATISCH GEGENEREERD DOOR CODE-NAAR-JAVASCRIPT CONVERTER
 * Dit is een JavaScript module die is gegenereerd uit een {file_extension} bestand.
 * Deze module werkt zowel in Node.js als in browser-omgeving.
 * 
 * Originele bestandsnaam: [filename]
 * Geconverteerd op: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
 */
"""
    
    return header + js_code

def convert_python_to_js(source_code, file_extension='.py', filename='unknown.py'):
    """
    Converteert broncode naar JavaScript/Node.js code.
    
    Args:
        source_code (str): De broncode die moet worden omgezet
        file_extension (str): De bestandsextensie van het bronbestand (standaard: .py)
        filename (str): De originele bestandsnaam (voor speciale gevallen)
        
    Returns:
        str: De geconverteerde JavaScript code
    """
    import datetime
    # Bepaal het type bestand op basis van de extensie
    file_extension = file_extension.lower() if file_extension else '.py'
    
    # Als het al een JavaScript bestand is, hoeven we het niet te converteren
    if file_extension == '.js':
        return source_code
    
    # Voor HTML/CSS/JSON bestanden, maak een JavaScript versie die de inhoud kan weergeven
    if file_extension in ['.html', '.css', '.json', '.sql']:
        return convert_other_to_js(source_code, file_extension)
    
    # Speciale behandeling voor contract_templates bestanden
    if 'contract_templates' in filename and 'get_templates' in source_code:
        # Dit is een speciale conversie voor contract_templates bestanden
        now = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Eenvoudige parsen van bestaande Python templates. We vermijden complexe regex en doen het stapsgewijs.
        templates_data = []
        
        # Zoek naar templates in Python code
        template_lines = source_code.split("\n")
        current_template = None
        capturing_content = False
        content_lines = []
        
        for line in template_lines:
            if line.strip().startswith("return [") or line.strip() == "return [":
                continue
            
            if line.strip().startswith('{') and '"id":' in line:
                # Begin van een nieuw template
                current_template = {"content": ""}
                # Extract id, name, description
                if '"id":' in line:
                    id_match = re.search(r'"id":\s*"([^"]+)"', line)
                    if id_match:
                        current_template["id"] = id_match.group(1)
                if '"name":' in line:
                    name_match = re.search(r'"name":\s*"([^"]+)"', line)
                    if name_match:
                        current_template["name"] = name_match.group(1)
                if '"description":' in line:
                    desc_match = re.search(r'"description":\s*"([^"]+)"', line)
                    if desc_match:
                        current_template["description"] = desc_match.group(1)
            
            elif current_template and '"content":' in line and '"""' in line:
                # Begin van content capture
                capturing_content = True
                # Haal alleen de content na """
                content_start = line.find('"""') + 3
                if content_start < len(line):
                    content_lines.append(line[content_start:])
            
            elif capturing_content and '"""' in line:
                # Einde van content capture
                capturing_content = False
                # Voeg alles toe behalve laatste """
                content_end = line.rfind('"""')
                if content_end > 0:
                    content_lines.append(line[:content_end])
                
                # Voeg de template toe en reset
                current_template["content"] = "\n".join(content_lines)
                templates_data.append(current_template)
                current_template = None
                content_lines = []
            
            elif capturing_content:
                # In het midden van content capture
                content_lines.append(line)
        
        # Genereer JavaScript code met verzamelde templates
        js_code_parts = []
        js_code_parts.append("/**")
        js_code_parts.append(" * AUTOMATISCH GEGENEREERD - VOOR GEBRUIK MET VERCEL/NODE.JS")
        js_code_parts.append(" * Handmatige aanpassingen kunnen nodig zijn voor optimale functionaliteit.")
        js_code_parts.append(" * Dit is een automatische vertaling van Python code naar JavaScript/Node.js.")
        js_code_parts.append(" * Deze module bevat alle contractsjablonen in JSON formaat.")
        js_code_parts.append(" * ")
        js_code_parts.append(f" * Originele Python bestandsnaam: {filename}")
        js_code_parts.append(f" * Geconverteerd op: {now}")
        js_code_parts.append(" */")
        js_code_parts.append("")
        js_code_parts.append("/**")
        js_code_parts.append(" * Beschikbare contractsjablonen")
        js_code_parts.append(" * @type {Array}")
        js_code_parts.append(" */")
        js_code_parts.append("const templates = [")
        
        for template in templates_data:
            # Escape backticks voor JavaScript
            escaped_content = template.get("content", "").replace("`", "\\`")
            
            js_template = f"""    {{
        id: '{template.get("id", "")}',
        name: '{template.get("name", "")}',
        description: '{template.get("description", "")}',
        content: `{escaped_content}`
    }}"""
            js_code_parts.append(js_template + ",")
        
        # Verwijder extra comma van de laatste entry
        if js_code_parts[-1].endswith(","):
            js_code_parts[-1] = js_code_parts[-1][:-1]
        
        js_code_parts.append("];")
        js_code_parts.append("")
        js_code_parts.append("/**")
        js_code_parts.append(" * Retourneert een lijst van beschikbare contractsjablonen voor gebruik in de applicatie.")
        js_code_parts.append(" * @returns {Array} Een lijst van sjabloongegevens")
        js_code_parts.append(" */")
        js_code_parts.append("function getContractTemplates() {")
        js_code_parts.append("    return templates;")
        js_code_parts.append("}")
        js_code_parts.append("")
        js_code_parts.append("// Export de templates voor Node.js")
        js_code_parts.append("if (typeof module !== 'undefined' && module.exports) {")
        js_code_parts.append("  module.exports = {")
        js_code_parts.append("    getContractTemplates,")
        js_code_parts.append("    templates")
        js_code_parts.append("  };")
        js_code_parts.append("}")
        js_code_parts.append("")
        js_code_parts.append("// Browser exports")
        js_code_parts.append("if (typeof window !== 'undefined') {")
        js_code_parts.append("  window.ContractTemplates = {")
        js_code_parts.append("    getContractTemplates,")
        js_code_parts.append("    templates")
        js_code_parts.append("  };")
        js_code_parts.append("}")
        
        # Combineer alles om de template code te maken
        template_code = "\n".join(js_code_parts)
        
        # Return direct de template code om verdere verwerking te vermijden
        return template_code

    
    # Voor Python bestanden, doe de normale conversie
    js_code = source_code
    
    # Commentaar conversie (behouden maar format aanpassen)
    js_code = re.sub(r'"""(.*?)"""', r'/**\n * $1\n */', js_code, flags=re.DOTALL)
    js_code = re.sub(r"'''(.*?)'''", r'/**\n * $1\n */', js_code, flags=re.DOTALL)
    
    # Eén-regel commentaar
    js_code = re.sub(r'#(.*?)$', r'//$1', js_code, flags=re.MULTILINE)
    
    # None -> null conversie
    js_code = re.sub(r'\bNone\b', 'null', js_code)
    
    # True/False conversie
    js_code = re.sub(r'\bTrue\b', 'true', js_code)
    js_code = re.sub(r'\bFalse\b', 'false', js_code)
    
    # def -> function conversie
    js_code = re.sub(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):', r'function $1($2) {', js_code)
    
    # class conversie
    js_code = re.sub(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))?:', r'class $1 \{', js_code)
    
    # self -> this conversie
    js_code = re.sub(r'\bself\b', 'this', js_code)
    
    # __init__ -> constructor
    js_code = re.sub(r'def\s+__init__\s*\((.*?)\):', r'constructor($1) {', js_code)
    
    # List comprehension naar map/filter/reduce
    # Simpele list comprehension: [x for x in items] -> items.map(x => x)
    js_code = re.sub(r'\[(.*?) for (.*?) in (.*?)\]', r'$3.map($2 => $1)', js_code)
    
    # List comprehension met conditie: [x for x in items if x > 0] -> items.filter(x => x > 0).map(x => x)
    js_code = re.sub(r'\[(.*?) for (.*?) in (.*?) if (.*?)\]', r'$3.filter($2 => $4).map($2 => $1)', js_code)
    
    # Dictionary comprehension naar Object.fromEntries + map
    # {k: v for k, v in items} -> Object.fromEntries(items.map(([k, v]) => [k, v]))
    js_code = re.sub(r'\{(.*?):\s*(.*?) for (.*?), (.*?) in (.*?)\}', 
                    r'Object.fromEntries($5.map([$3, $4] => [$1, $2]))', js_code)
    
    # if/elif/else conversie
    js_code = re.sub(r'elif\s+(.*?):', r'} else if ($1) {', js_code)
    js_code = re.sub(r'if\s+(.*?):', r'if ($1) {', js_code)
    js_code = re.sub(r'else:', r'} else {', js_code)
    
    # for loops
    js_code = re.sub(r'for\s+(.*?)\s+in\s+(.*?):', r'for (const $1 of $2) {', js_code)
    js_code = re.sub(r'for\s+(.*?),\s+(.*?)\s+in\s+enumerate\((.*?)\):', 
                    r'for (const [$2, $1] of $3.entries()) {', js_code)
    
    # while loops
    js_code = re.sub(r'while\s+(.*?):', r'while ($1) {', js_code)
    
    # try/except/finally
    js_code = re.sub(r'try:', r'try {', js_code)
    js_code = re.sub(r'except\s+(.*?)\s+as\s+(.*?):', r'} catch($2) {', js_code)
    js_code = re.sub(r'except\s+(.*?):', r'} catch(error) {', js_code)
    js_code = re.sub(r'except:', r'} catch(error) {', js_code)
    js_code = re.sub(r'finally:', r'} finally {', js_code)
    
    # imports naar require of import
    js_code = re.sub(r'from\s+(.*?)\s+import\s+(.*)', r'// ESM import\n// import { $2 } from "$1";\n// CommonJS require\nlet $2;\ntry {\n  $2 = require("$1");\n} catch (e) {\n  console.warn("Module $1 kon niet worden ingeladen, functionaliteit kan beperkt zijn");\n}', js_code)
    js_code = re.sub(r'import\s+(.*?)', r'// import $1;\nlet $1;\ntry {\n  $1 = require("$1");\n} catch (e) {\n  console.warn("Module $1 kon niet worden ingeladen, functionaliteit kan beperkt zijn");\n}', js_code)
    
    # list/dict/set methoden
    js_code = re.sub(r'\.append\(', '.push(', js_code)
    js_code = re.sub(r'\.extend\(', '.push(...', js_code)
    js_code = re.sub(r'\.items\(\)', '.entries()', js_code)
    js_code = re.sub(r'\.keys\(\)', '.keys()', js_code)
    js_code = re.sub(r'\.values\(\)', '.values()', js_code)
    
    # String methods
    js_code = re.sub(r'\.strip\(\)', '.trim()', js_code)
    js_code = re.sub(r'\.join\((.*?)\)', '.join($1)', js_code)
    js_code = re.sub(r'\.format\((.*?)\)', '.replace(/\{\}/g, () => [$1].shift())', js_code)
    
    # Python ingebouwde functies
    js_code = re.sub(r'\blen\((.*?)\)', r'$1.length', js_code)
    js_code = re.sub(r'\bprint\((.*?)\)', r'console.log($1)', js_code)
    js_code = re.sub(r'\bstr\((.*?)\)', r'String($1)', js_code)
    js_code = re.sub(r'\bint\((.*?)\)', r'parseInt($1)', js_code)
    js_code = re.sub(r'\bfloat\((.*?)\)', r'parseFloat($1)', js_code)
    
    # Lambda functies
    js_code = re.sub(r'lambda\s+(.*?):\s+(.*)', r'($1) => $2', js_code)
    
    # Return statements
    js_code = re.sub(r'\breturn\b', 'return', js_code)
    
    # Sluit alle open accolades (geschat aantal)
    # Tel aantal voorkomens van { en }
    open_braces = js_code.count('{')
    close_braces = js_code.count('}')
    extra_closing = open_braces - close_braces
    
    if extra_closing > 0:
        js_code += '\n' + '}'.join([''] * extra_closing)
    
    # Voeg hulpfuncties toe voor Python-like functionaliteit
    helper_functions = """
/**
 * Hulpfuncties voor Python-achtige functionaliteit in Node.js
 */

// Python-achtige range functie
function range(start, stop, step = 1) {
  if (typeof stop === 'undefined') {
    stop = start;
    start = 0;
  }
  
  const result = [];
  for (let i = start; step > 0 ? i < stop : i > stop; i += step) {
    result.push(i);
  }
  return result;
}

// Python-achtige enumerate functie
function enumerate(iterable, start = 0) {
  return Array.from(iterable).map((value, index) => [index + start, value]);
}

// Python-achtige zip functie
function zip(...arrays) {
  const length = Math.min(...arrays.map(arr => arr.length));
  return Array.from({ length }, (_, i) => arrays.map(array => array[i]));
}

// Python-achtige bestandsoperaties
const fs = typeof require !== 'undefined' ? require('fs') : null;

function open(filepath, mode = 'r') {
  if (!fs) {
    throw new Error('Bestandsoperaties zijn alleen beschikbaar in Node.js omgeving');
  }
  
  const file = {
    read: () => fs.readFileSync(filepath, 'utf8'),
    write: (content) => fs.writeFileSync(filepath, content, 'utf8'),
    append: (content) => fs.appendFileSync(filepath, content, 'utf8'),
    close: () => {} // No-op in Node.js
  };
  
  return file;
}

/**
 * Schrijft de gegenereerde code naar een bestand (Node.js omgeving)
 * @param {string} filepath - Het pad waar het bestand naartoe geschreven moet worden
 * @returns {Promise<void>} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeToFile(filepath) {
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {
    try {
      const fs = require('fs').promises;
      // Het hele geëxporteerde module object opslaan
      await fs.writeFile(filepath, module.exports.toString(), 'utf8');
      console.log(`Module geschreven naar ${filepath}`);
    } catch (error) {
      console.error(`Fout bij het schrijven naar bestand: ${error.message}`);
      throw error;
    }
  } else {
    console.warn('writeToFile is alleen beschikbaar in Node.js omgeving');
  }
}
"""
    
    # Voeg de helper functies toe aan de code
    js_code += helper_functions
    
    # Voeg module export toe voor Node.js compatibiliteit
    # Zoek alle functies en klassen in de code
    functions = re.findall(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', js_code)
    classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', js_code)
    
    exports = []
    
    for func in functions:
        if func not in exports and func not in ['range', 'enumerate', 'zip', 'open', 'writeToFile']:
            exports.append(func)
    
    for cls in classes:
        if cls not in exports:
            exports.append(cls)
    
    # Voeg ook de hulpfuncties toe aan de exports
    helper_exports = ['range', 'enumerate', 'zip', 'open', 'writeToFile']
    
    if exports or helper_exports:
        js_code += "\n\n// Module exports voor Node.js\n"
        js_code += "if (typeof module !== 'undefined' && module.exports) {\n"
        js_code += "  module.exports = {\n"
        
        # Eerst de gewone functies en klassen
        for i, item in enumerate(exports):
            js_code += f"    {item},"
            js_code += "\n"
        
        # Dan de helper functies
        for i, item in enumerate(helper_exports):
            js_code += f"    {item}"
            if i < len(helper_exports) - 1:
                js_code += ","
            js_code += "\n"
        
        js_code += "  };\n"
        js_code += "}\n"
        
        # Voeg ook browser exports toe
        js_code += "\n// Browser globale variabelen\n"
        js_code += "if (typeof window !== 'undefined') {\n"
        js_code += "  window.PythonModule = {\n"
        
        # Gewone functies en klassen
        for i, item in enumerate(exports):
            js_code += f"    {item},"
            js_code += "\n"
        
        # Helper functies (behalve writeToFile en open die alleen voor Node.js zijn)
        js_code += "    range,\n"
        js_code += "    enumerate,\n"
        js_code += "    zip\n"
        
        js_code += "  };\n"
        js_code += "}\n"
    
    # Voeg waarschuwing toe
    header = """/**
 * AUTOMATISCH GEGENEREERD DOOR PYTHON-NAAR-JAVASCRIPT CONVERTER
 * Dit is een automatische vertaling van Python code naar JavaScript/Node.js.
 * Deze module werkt zowel in Node.js als in browser-omgeving.
 * Handmatige aanpassingen kunnen nodig zijn voor optimale functionaliteit.
 * 
 * Originele Python bestandsnaam: [filename]
 * Geconverteerd op: [date]
 */

"""
    import datetime
    header = header.replace('[date]', datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    
    # Stel de bestandsnaam in als placeholder - deze wordt later vervangen door de echte bestandsnaam
    header = header.replace('[filename]', 'PYTHON_ORIGINAL_FILENAME')
    
    js_code = header + js_code
    
    return js_code