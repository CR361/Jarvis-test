/**
 * AUTOMATISCH GEGENEREERD - VOOR GEBRUIK MET VERCEL/NODE.JS
 * Handmatige aanpassingen kunnen nodig zijn voor optimale functionaliteit. DOOR CODE-NAAR-JAVASCRIPT CONVERTER
 * Dit is een JavaScript module die is gegenereerd uit een .html bestand.
 * Deze module werkt zowel in Node.js als in browser-omgeving.
 * 
 * Originele bestandsnaam: [filename]
 * Geconverteerd op: 10-04-2025 21:37:30
 */

/**
 * JavaScript module gegenereerd uit HTML template
 * Deze module stelt de HTML beschikbaar als string en bevat functies om deze te gebruiken
 */

// De originele HTML als string
const htmlContent = "{% extends 'base.html' %}\n\n{% block title %}Contract ondertekenen - Jarvis{% endblock %}\n\n{% block extra_css %}\n<style>\n    #signature-pad {\n        border: 1px solid #ddd;\n        border-radius: 4px;\n        background-color: #fff;\n    }\n    .signature-container {\n        max-width: 600px;\n        margin: 0 auto;\n    }\n</style>\n{% endblock %}\n\n{% block content %}\n<div class=\"container py-4\">\n    <div class=\"text-center mb-4\">\n        <h1 class=\"mb-3\">\n            <i class=\"fas fa-file-signature text-primary me-2\"></i>Contract ondertekenen\n        </h1>\n        {% if contract.status == 'ondertekend' %}\n        <div class=\"alert alert-success\">\n            <i class=\"fas fa-check-circle me-2\"></i>Dit contract is al ondertekend.\n        </div>\n        {% elif contract.status != 'verzonden' %}\n        <div class=\"alert alert-warning\">\n            <i class=\"fas fa-exclamation-triangle me-2\"></i>Dit contract kan niet worden ondertekend.\n        </div>\n        {% endif %}\n    </div>\n\n    <div class=\"row\">\n        <div class=\"col-lg-8 mx-auto\">\n            <div class=\"card shadow-sm mb-4\">\n                <div class=\"card-header\">\n                    <h5 class=\"mb-0\">{{ contract.title }}</h5>\n                </div>\n                <div class=\"card-body\">\n                    <p class=\"mb-3\">\n                        <strong>Klant:</strong> {{ contract.customer.name }}\n                        {% if contract.customer.company %}({{ contract.customer.company }}){% endif %}\n                    </p>\n                    \n                    <div class=\"contract-content mb-4\">\n                        {{ contract.content|safe }}\n                    </div>\n                    \n                    {% if just_signed %}\n                    <div class=\"alert alert-success\">\n                        <i class=\"fas fa-check-circle me-2\"></i>Hartelijk dank voor het ondertekenen van dit contract. Een kopie is bewaard in ons systeem.\n                    </div>\n                    \n                    <div class=\"text-center mb-4\">\n                        <h5 class=\"mb-3\">Uw handtekening:</h5>\n                        <img src=\"{{ contract.signature_data }}\" alt=\"Uw handtekening\" style=\"max-width: 100%; max-height: 200px; border: 1px solid #ddd; padding: 10px;\">\n                        <p class=\"mt-2\">Ondertekend door: {{ contract.signed_by }}</p>\n                        <p>Datum: {{ contract.signed_at.strftime('%d-%m-%Y %H:%M') }}</p>\n                    </div>\n                    {% elif can_sign %}\n                    <div class=\"signature-container mb-4\">\n                        <h5>Plaats uw handtekening hieronder:</h5>\n                        \n                        <form method=\"POST\" action=\"{{ url_for('contract_sign', contract_id=contract.id) }}\" id=\"signature-form\">\n                            <input type=\"hidden\" name=\"csrf_token\" value=\"{{ csrf_token() }}\">\n                            <input type=\"hidden\" name=\"signature_data\" id=\"signature-data\">\n                            \n                            <div class=\"mb-3\">\n                                <canvas id=\"signature-pad\" width=\"600\" height=\"200\"></canvas>\n                            </div>\n                            \n                            <div class=\"d-flex gap-2 mb-4\">\n                                <button type=\"button\" class=\"btn btn-outline-secondary\" id=\"clear-signature\">\n                                    <i class=\"fas fa-eraser me-2\"></i>Wissen\n                                </button>\n                            </div>\n                            \n                            <div class=\"mb-3\">\n                                <label for=\"signed_by\" class=\"form-label\">Uw volledige naam *</label>\n                                <input type=\"text\" class=\"form-control\" id=\"signed_by\" name=\"signed_by\" required>\n                                <div class=\"form-text\">Voer uw volledige naam in zoals vermeld in het contract.</div>\n                            </div>\n                            \n                            <div class=\"form-check mb-3\">\n                                <input class=\"form-check-input\" type=\"checkbox\" id=\"agree-terms\" required>\n                                <label class=\"form-check-label\" for=\"agree-terms\">\n                                    Ik heb het contract gelezen en ga akkoord met de voorwaarden\n                                </label>\n                            </div>\n                            \n                            <div class=\"d-grid\">\n                                <button type=\"submit\" class=\"btn btn-primary\" id=\"sign-button\">\n                                    <i class=\"fas fa-signature me-2\"></i>Contract ondertekenen\n                                </button>\n                            </div>\n                        </form>\n                    </div>\n                    {% else %}\n                    <div class=\"alert alert-secondary text-center\">\n                        <i class=\"fas fa-info-circle me-2\"></i>Dit contract kan niet worden ondertekend.\n                    </div>\n                    {% endif %}\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n{% endblock %}\n\n{% block extra_js %}\n{% if can_sign %}\n<script src=\"https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js\"></script>\n<script>\n    document.addEventListener('DOMContentLoaded', function() {\n        const canvas = document.getElementById('signature-pad');\n        const signaturePad = new SignaturePad(canvas, {\n            backgroundColor: 'rgb(255, 255, 255)',\n            penColor: 'rgb(0, 0, 0)'\n        });\n        \n        // Handle window resize to maintain signature pad aspect ratio\n        function resizeCanvas() {\n            const ratio = Math.max(window.devicePixelRatio || 1, 1);\n            canvas.width = canvas.offsetWidth * ratio;\n            canvas.height = canvas.offsetHeight * ratio;\n            canvas.getContext(\"2d\").scale(ratio, ratio);\n            signaturePad.clear(); // Otherwise isEmpty() might return incorrect value\n        }\n        \n        window.addEventListener(\"resize\", resizeCanvas);\n        resizeCanvas();\n        \n        // Clear signature button\n        document.getElementById('clear-signature').addEventListener('click', function() {\n            signaturePad.clear();\n        });\n        \n        // Form submission\n        document.getElementById('signature-form').addEventListener('submit', function(e) {\n            if (signaturePad.isEmpty()) {\n                e.preventDefault();\n                alert('Plaats a.u.b. uw handtekening voordat u het contract ondertekent.');\n                return false;\n            }\n            \n            // Versie 1.1: Verminder de kwaliteit om te grote requests te voorkomen\n            const signatureData = signaturePad.toDataURL('image/jpeg', 0.5); // JPEG met 50% kwaliteit\n            document.getElementById('signature-data').value = signatureData;\n        });\n    });\n</script>\n{% endif %}\n{% endblock %}\n";

/**
 * Rendert de HTML naar een DOM element in browser-omgeving
 * @param {Element|string} container - DOM element of selector string
 */
function renderHtmlToElement(container) {
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    const targetElement = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;
    
    if (!targetElement) {
      console.error('Target element not found');
      return;
    }
    
    targetElement.innerHTML = htmlContent;
  } else {
    console.warn('renderHtmlToElement is alleen beschikbaar in browser-omgeving');
  }
}

/**
 * Maakt een nieuwe DOM element met de HTML inhoud in browser-omgeving
 * @returns {DocumentFragment|null} Een document fragment met de HTML inhoud
 */
function createHtmlFragment() {
  // Check of we in een browser-omgeving zijn
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    const template = document.createElement('template');
    template.innerHTML = htmlContent;
    return template.content.cloneNode(true);
  } else {
    console.warn('createHtmlFragment is alleen beschikbaar in browser-omgeving');
    return null;
  }
}

/**
 * Parse HTML naar een DOM structuur (Node.js compatibel met jsdom)
 * @param {Object} jsdom - De jsdom module (vereist voor Node.js: npm install jsdom)
 * @returns {Object} Het geparste document object
 */
function parseHtmlWithJSDOM(jsdom) {
  if (!jsdom || !jsdom.JSDOM) {
    throw new Error('Geldige jsdom module vereist. Installeer met: npm install jsdom');
  }
  return new jsdom.JSDOM(htmlContent).window.document;
}

/**
 * Schrijft de HTML inhoud naar een bestand (Node.js omgeving)
 * @param {string} filepath - Het pad waar de HTML naartoe geschreven moet worden
 * @returns {Promise<void>} Promise die voltooid wordt wanneer het bestand is geschreven
 */
async function writeHtmlToFile(filepath) {
  // Check of we in een Node.js omgeving zijn
  if (typeof require !== 'undefined') {
    try {
      const fs = require('fs').promises;
      await fs.writeFile(filepath, htmlContent, 'utf8');
      console.log(`HTML geschreven naar ${filepath}`);
    } catch (error) {
      console.error(`Fout bij het schrijven van HTML naar bestand: ${error.message}`);
      throw error;
    }
  } else {
    console.warn('writeHtmlToFile is alleen beschikbaar in Node.js omgeving');
  }
}

// Node.js module exports
// CommonJS exports
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    htmlContent,
    renderHtmlToElement,
    createHtmlFragment,
    parseHtmlWithJSDOM,
    writeHtmlToFile
  };
}

// Browser/ES module exports
if (typeof window !== 'undefined') {
  window.HTMLModule = {
    htmlContent,
    renderHtmlToElement,
    createHtmlFragment
  };
}
